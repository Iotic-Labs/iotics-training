package main

import (
	"iotics-training/pkg/helpers"
	"log"
	"net/url"

	ioticsApi "github.com/Iotic-Labs/iotics-api-grpc-go/iotics/api"
	"github.com/Iotic-Labs/iotics-identity-go/pkg/register"
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

	token := helpers.GetToken(agentIdentity, userIdentity, 600)
	apiContext := helpers.GetApiContext(token, HOST_GRPC_URL, "Twin Receiver")

	/*** CREATE TWIN RADIATOR IDENTITY, THEN DELEGATE ***/
	/* We will reuse the AGENT_SEED to create the Twin Identity.
	   Multiple creations of the Twin Identity won't (re-)create the Identity. */
	twinRadiatorIdentity := helpers.CreateTwinIdentity(resolverClient, "Radiator", AGENT_SEED)
	helpers.ControlDelegation(resolverClient, twinRadiatorIdentity, agentIdentity)

	/*** UPSERT TWIN RADIATOR WITH LABEL AND INPUT, THEN DESCRIBE TWIN ***/
	/* The only way to create a Twin with an Input is through the Upsert operation.
	   -	Start without AllowLists: the Twin won't be found from a remote Host.
	   -	Add hostMetadataAllowList: the Twin will be found but
	   won't be able to interact with other Twins from a remote Host.
	   -	Add hostAllowList: the Twin will now receive data. */
	_, err = apiContext.TwinAPI.UpsertTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.UpsertTwinRequest{
			Headers: &apiContext.Headers,
			Payload: &ioticsApi.UpsertTwinRequest_Payload{
				TwinId: &ioticsApi.TwinID{Id: twinRadiatorIdentity.Did()},
				Properties: []*ioticsApi.Property{
					{
						Key: helpers.PROPERTY_KEY_LABEL,
						Value: &ioticsApi.Property_LangLiteralValue{
							LangLiteralValue: &ioticsApi.LangLiteral{
								Value: "Twin Radiator",
								Lang:  "en",
							},
						},
					},
					// Add later
					{
						Key: helpers.PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
						Value: &ioticsApi.Property_UriValue{
							UriValue: &ioticsApi.Uri{
								Value: helpers.PROPERTY_VALUE_ALLOW_ALL_HOSTS,
							},
						},
					},
					// Add later
					{
						Key: helpers.PROPERTY_KEY_HOST_ALLOW_LIST,
						Value: &ioticsApi.Property_UriValue{
							UriValue: &ioticsApi.Uri{
								Value: helpers.PROPERTY_VALUE_ALLOW_ALL_HOSTS,
							},
						},
					},
				},
				Inputs: []*ioticsApi.UpsertInputWithMeta{
					{
						Id: "radiator_switch",
						Values: []*ioticsApi.Value{
							{
								Label:    "turn_on",
								Comment:  "ON/OFF switch for the Radiator",
								DataType: "boolean",
							},
						},
					},
				},
			},
		},
	)
	if err != nil {
		log.Fatalf("Could not Upsert Twin: %v", err)
	}
	log.Printf("Twin created DID: %s", twinRadiatorIdentity.Did())

	twinDescription, err := apiContext.TwinAPI.DescribeTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.DescribeTwinRequest{
			Headers: &apiContext.Headers,
			Args: &ioticsApi.DescribeTwinRequest_Arguments{
				TwinId: &ioticsApi.TwinID{
					Id: twinRadiatorIdentity.Did(),
				},
			},
		},
	)
	if err != nil {
		log.Fatalf("Could not Describe Twin: %v", err)
	}
	log.Printf("Twin description: %s", twinDescription.GetPayload())

	/*** WAIT FOR INPUT MESSAGES ***/
	inputListener, rcvErr := apiContext.InputAPI.ReceiveInputMessages(
		apiContext.CtxWithMeta,
		&ioticsApi.ReceiveInputMessageRequest{
			Headers: &apiContext.Headers,
			Args: &ioticsApi.ReceiveInputMessageRequest_Arguments{
				InputId: &ioticsApi.InputID{
					Id:     "radiator_switch",
					TwinId: twinRadiatorIdentity.Did(),
				},
			},
		},
	)
	if rcvErr != nil {
		log.Fatalf("Could not receive Input messages: %v", rcvErr)
	}

	log.Print("Waiting for Input messages...")
	for {
		msg, receiveErr := inputListener.Recv()
		if receiveErr != nil {
			log.Printf("Error: %v", receiveErr)
			break
		}

		log.Printf("Input message: %s", msg.GetPayload().Message.Data)
	}
}
