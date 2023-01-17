package main

import (
	"fmt"
	"iotics-training/pkg/helpers"
	"log"
	"math/rand"
	"net/url"
	"time"

	ioticsApi "github.com/Iotic-Labs/iotics-api-grpc-go/iotics/api"
	"github.com/Iotic-Labs/iotics-identity-go/pkg/register"
	"google.golang.org/protobuf/types/known/timestamppb"
)

const (
	RESOLVER_URL  = ""
	HOST_GRPC_URL = "" // <spacename>.iotics.com:10001

	USER_KEY_NAME = ""
	USER_SEED     = ""

	AGENT_KEY_NAME = ""
	AGENT_SEED     = ""
)

func main() {
	resolverAddr, err := url.Parse(RESOLVER_URL)
	if err != nil {
		log.Fatalf("Could not parse RESOLVER_URL: %v", err)
	}
	resolverClient := register.NewDefaultRestResolverClient(resolverAddr)

	userIdentity := helpers.CreateUserIdentity(resolverClient, USER_KEY_NAME, USER_SEED)
	agentIdentity := helpers.CreateAgentIdentity(resolverClient, AGENT_KEY_NAME, AGENT_SEED)
	helpers.AuthenticationDelegation(resolverClient, userIdentity, agentIdentity)

	token := helpers.GetToken(agentIdentity, userIdentity, 60)
	apiContext := helpers.GetApiContext(token, HOST_GRPC_URL, "Twin Sender")

	/*** CREATE TWIN MOTION SENSOR IDENTITY, THEN DELEGATE ***/
	/* We will reuse the AGENT_SEED to create the Twin Identity.
	   Multiple creations of the Twin Identity won't (re-)create the Identity. */
	twinMotionSensorIdentity := helpers.CreateTwinIdentity(resolverClient, "MotionSensor", AGENT_SEED)
	helpers.ControlDelegation(resolverClient, twinMotionSensorIdentity, agentIdentity)

	/*** CREATE TWIN MOTION SENSOR BASIC STRUCTURE, THEN DESCRIBE TWIN ***/
	/* For the sake of this exercise, this Twin only needs the Basic Structure
	   (no Properties/Feeds/Inputs) to send Input messages. */
	_, err = apiContext.TwinAPI.CreateTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.CreateTwinRequest{
			Headers: &apiContext.Headers,
			Payload: &ioticsApi.CreateTwinRequest_Payload{
				Id: twinMotionSensorIdentity.Did(),
			},
		},
	)
	if err != nil {
		log.Fatalf("Could not Create Twin: %v", err)
	}
	log.Printf("Twin created DID: %s", twinMotionSensorIdentity.Did())

	twinDescription, err := apiContext.TwinAPI.DescribeTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.DescribeTwinRequest{
			Headers: &apiContext.Headers,
			Args: &ioticsApi.DescribeTwinRequest_Arguments{
				TwinId: &ioticsApi.TwinID{
					Id: twinMotionSensorIdentity.Did(),
				},
			},
		},
	)
	if err != nil {
		log.Fatalf("Could not Describe Twin: %v", err)
	}
	log.Printf("Twin description: %v", twinDescription.GetPayload())

	/*** SEARCH FOR TWIN RADIATOR BY LABEL ***/
	/* "We need to Search the entire Network of Spaces (scope=GLOBAL)
	   rather than locally (scope=LOCAL) in order to find Twins in a remote Host.
	   The only search parameter we want to use for the sake of this exercise is the Twin's Label
	   which must match exactly the Label of the Twin we want to find.
	   -	Initially no Twins will be found (hostMetadataAllowList of Twin Radiator = noHost). */
	headersSearch := ioticsApi.Headers{
		ClientAppId:    "Iotics Search",
		TransactionRef: []string{"Search: Twin Radiator"}, // BONUS: "Twin Thermostat"
		// Timeout of 3 seconds is enough given the poor amount of Twins in the Network
		RequestTimeout: timestamppb.New(time.Now().Add(time.Second * 3)),
	}

	searchResponseClient, searchErr := apiContext.SearchAPI.SynchronousSearch(
		apiContext.CtxWithMeta,
		&ioticsApi.SearchRequest{
			Headers: &headersSearch,
			Scope:   ioticsApi.Scope_GLOBAL,
			Payload: &ioticsApi.SearchRequest_Payload{
				ResponseType: ioticsApi.ResponseType_FULL,
				Filter: &ioticsApi.SearchRequest_Payload_Filter{
					Properties: []*ioticsApi.Property{
						{
							Key: helpers.PROPERTY_KEY_LABEL,
							Value: &ioticsApi.Property_LangLiteralValue{
								LangLiteralValue: &ioticsApi.LangLiteral{
									Value: "Twin Radiator", // BONUS: "Twin Thermostat"
									Lang:  "en",
								},
							},
						},
					},
				},
			},
		},
	)
	if searchErr != nil {
		log.Fatalf("Could not search: %v", searchErr)
	}

	var twinsFound []*ioticsApi.SearchResponse_TwinDetails

	for {
		resp, respErr := searchResponseClient.Recv()
		if respErr != nil {
			break
		}
		twinsFound = append(twinsFound, resp.GetPayload().GetTwins()...)
	}

	log.Printf("Twins found: %s", twinsFound)

	/*** SEND INPUT MESSAGES ***/
	for {
		randBool := rand.Intn(2) == 1                            // Generate random bool
		inputMessage := fmt.Sprintf(`{"turn_on": %t}`, randBool) // BONUS: "presence_detected"
		dataToShare := []byte(inputMessage)

		_, err := apiContext.InterestAPI.SendInputMessage(
			apiContext.CtxWithMeta,
			&ioticsApi.SendInputMessageRequest{
				Headers: &apiContext.Headers,
				Args: &ioticsApi.SendInputMessageRequest_Arguments{
					Interest: &ioticsApi.InputInterest{
						SenderTwinId: &ioticsApi.TwinID{Id: twinMotionSensorIdentity.Did()},
						DestInputId:  twinsFound[0].GetInputs()[0].InputId,
					},
				},
				Payload: &ioticsApi.SendInputMessageRequest_Payload{
					Message: &ioticsApi.InputMessage{
						Data: dataToShare,
						Mime: "application/json",
					},
				},
			},
		)
		if err != nil {
			log.Fatalf("Could not send Input Message: %v", err)
		}
		log.Printf("Sending input message %s", inputMessage)

		time.Sleep(5 * time.Second)
	}
}
