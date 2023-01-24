package main

import (
	"encoding/json"
	"iotics-training/pkg/helpers"
	"log"
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

/*** BONUS ***/
// func getInputMessages(inputListener ioticsApi.InputAPI_ReceiveInputMessagesClient, inputValueLabel string, ch <-chan bool) {
// 	log.Print("Waiting for Input Messages...")
// 	mappedData := make(map[string]interface{})

// 	for {
// 		msg, err := inputListener.Recv()
// 		if err != nil {
// 			log.Printf("Error: %v", err)
// 			break
// 		}
// 		msgReceived := msg.GetPayload().Message.Data
// 		err = json.Unmarshal(msgReceived, &mappedData)
// 		if err != nil {
// 			log.Printf("Error: %v", err)
// 			break
// 		}

// 		presence := bool(mappedData[inputValueLabel].(bool))
// 		log.Printf("Received Input message: %t", presence)

// 		ch <- presence
// 	}
// }

func getFeedData(feedListener ioticsApi.InterestAPI_FetchInterestsClient, twinId string, feedValueLabel string, ch chan<- bool) {
	log.Printf("Following Twin %s", twinId)
	mappedData := make(map[string]interface{})

	for {
		latestFeedData, err := feedListener.Recv()
		if err != nil {
			log.Printf("Error: %v", err)
			break
		}

		dataReceived := latestFeedData.GetPayload().FeedData.GetData()
		err = json.Unmarshal(dataReceived, &mappedData)
		if err != nil {
			log.Printf("Error: %v", err)
			break
		}

		temperature := int(mappedData[feedValueLabel].(float64))
		log.Printf("Received Temperature: %d from Twin %s", temperature, twinId)

		if temperature < 20 {
			ch <- true
		} else {
			ch <- false
		}
	}
}

func main() {
	resolverAddr, err := url.Parse(RESOLVER_URL)
	if err != nil {
		log.Fatalf("Could not parse RESOLVER_URL: %v", err)
	}
	resolverClient := register.NewDefaultRestResolverClient(resolverAddr)

	userIdentity, agentIdentity := helpers.CreateUserAndAgentWithAuthDelegation(
		resolverClient,
		USER_SEED, USER_KEY_NAME,
		AGENT_SEED, AGENT_KEY_NAME,
	)

	token := helpers.GetToken(agentIdentity, userIdentity, 600)
	apiContext := helpers.GetApiContext(token, HOST_GRPC_URL, "Synthesiser Connector")

	/*** CREATE TWIN THEROMSTAT WITH CONTROL DELEG ***/
	/* There's no need to create a Twin Model for this exercise.
	   If there was a need to create more than just a Twin Follower,
	   then probably a Twin Model would be beneficial.
	   We don't care abut changing the AllowLists either
	   (no one needs to find, describe or send data to this Twin). */
	twinThermostatIdentity := helpers.CreateTwinWithControlDelegation(resolverClient, AGENT_SEED, "Thermostat", agentIdentity)

	_, err = apiContext.TwinAPI.CreateTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.CreateTwinRequest{
			Headers: &apiContext.Headers,
			Payload: &ioticsApi.CreateTwinRequest_Payload{
				Id: twinThermostatIdentity.Did(),
			},
		},
	)
	if err != nil {
		log.Fatalf("Could not Create Twin: %v", err)
	}
	log.Printf("Twin created DID: %s", twinThermostatIdentity.Did())

	/*** SEARCH FOR 2 PUBLISHER TWINS ***/
	/* We need to find the 2 Twins Publisher. To do that we need to define:
	   1. One or more search criteria
	   2. The type of the response
	   3. The scope of the Search. */
	headersSearch := ioticsApi.Headers{
		ClientAppId:    "Iotics Search",
		TransactionRef: []string{"Search: Publisher Twins"},
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
							Key: helpers.PROPERTY_KEY_CREATED_BY,
							Value: &ioticsApi.Property_StringLiteralValue{
								StringLiteralValue: &ioticsApi.StringLiteral{
									Value: "Lorenzo Paris",
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

	var twinPubList []*ioticsApi.SearchResponse_TwinDetails

	for {
		resp, respErr := searchResponseClient.Recv()
		if respErr != nil {
			break
		}
		twinPubList = append(twinPubList, resp.GetPayload().GetTwins()...)
	}

	/*** FOLLOW PUBLISHERS' FEED DATA ***/
	/* In order to follow a Twin's Feed we need to know:
	   1. The Twin DID
	   2. The Host ID of the Twin Publisher (if remote)
	   3. The Feed ID.
	   However, in order to parse Feed's data we need to know the value of the Feed's Label
	   which can be retrieved via the DescribeFeed operation. */
	ch := make(chan bool, len(twinPubList)+1) // BONUS: len(twinPubList) + 1

	for _, twin := range twinPubList {
		feedOfInterest := twin.GetFeeds()[0]

		feedDescription, err := apiContext.FeedAPI.DescribeFeed(
			apiContext.CtxWithMeta,
			&ioticsApi.DescribeFeedRequest{
				Headers: &apiContext.Headers,
				Args: &ioticsApi.DescribeFeedRequest_Arguments{
					FeedId: feedOfInterest.FeedId,
				},
			},
		)
		if err != nil {
			log.Fatalf("Could not Describe Feed: %v", err)
		}

		feedValueLabel := feedDescription.GetPayload().Result.GetValues()[0].Label

		feedListener, err := apiContext.InterestAPI.FetchInterests(
			apiContext.CtxWithMeta,
			&ioticsApi.FetchInterestRequest{
				Headers: &apiContext.Headers,
				Args: &ioticsApi.FetchInterestRequest_Arguments{
					Interest: &ioticsApi.Interest{
						FollowerTwinId: &ioticsApi.TwinID{Id: twinThermostatIdentity.Did()},
						FollowedFeedId: feedOfInterest.FeedId,
					},
				},
			},
		)
		if err != nil {
			log.Fatalf("Could not receive Feed messages: %v", err)
		}

		go getFeedData(feedListener, feedOfInterest.FeedId.TwinId, feedValueLabel, ch)
	}

	/*** SEARCH FOR TWIN RADIATOR ***/
	headersSearch = ioticsApi.Headers{
		ClientAppId:    "Iotics Search",
		TransactionRef: []string{"Search: Twin Radiator"},
		RequestTimeout: timestamppb.New(time.Now().Add(time.Second * 3)),
	}

	searchResponseClient, searchErr = apiContext.SearchAPI.SynchronousSearch(
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
									Value: "Twin Radiator",
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

	var twinRadiatorList []*ioticsApi.SearchResponse_TwinDetails

	for {
		resp, respErr := searchResponseClient.Recv()
		if respErr != nil {
			break
		}
		twinRadiatorList = append(twinRadiatorList, resp.GetPayload().GetTwins()...)
	}

	/*** BONUS ***/
	// _, err = apiContext.TwinAPI.UpsertTwin(
	// 	apiContext.CtxWithMeta,
	// 	&ioticsApi.UpsertTwinRequest{
	// 		Headers: &apiContext.Headers,
	// 		Payload: &ioticsApi.UpsertTwinRequest_Payload{
	// 			TwinId: &ioticsApi.TwinID{Id: twinThermostatIdentity.Did()},
	// 			Properties: []*ioticsApi.Property{
	// 				{
	// 					Key: helpers.PROPERTY_KEY_LABEL,
	// 					Value: &ioticsApi.Property_LangLiteralValue{
	// 						LangLiteralValue: &ioticsApi.LangLiteral{
	// 							Value: "Twin Thermostat",
	// 							Lang:  "en",
	// 						},
	// 					},
	// 				},
	// 			},
	// 			Inputs: []*ioticsApi.UpsertInputWithMeta{
	// 				{
	// 					Id: "presence",
	// 					Values: []*ioticsApi.Value{
	// 						{
	// 							Label:    "presence_detected",
	// 							Comment:  "Inform thermostat of sensor state",
	// 							DataType: "boolean",
	// 						},
	// 					},
	// 				},
	// 			},
	// 		},
	// 	},
	// )
	// if err != nil {
	// 	log.Fatalf("Could not Upsert Twin: %v", err)
	// }

	// inputListener, rcvErr := apiContext.InputAPI.ReceiveInputMessages(
	// 	apiContext.CtxWithMeta,
	// 	&ioticsApi.ReceiveInputMessageRequest{
	// 		Headers: &apiContext.Headers,
	// 		Args: &ioticsApi.ReceiveInputMessageRequest_Arguments{
	// 			InputId: &ioticsApi.InputID{
	// 				Id:     "presence",
	// 				TwinId: twinThermostatIdentity.Did(),
	// 			},
	// 		},
	// 	},
	// )
	// if rcvErr != nil {
	// 	log.Fatalf("Could not receive Input messages: %v", rcvErr)
	// }

	// go getInputMessages(inputListener, "presence_detected", ch)

	/*** THERMOSTAT LOGIC ***/
	statusOn := false
	var dataToShare []byte
	for {
		turnOn := true

		for i := 0; i < len(twinPubList); i++ { // BONUS: i < len(twinPubList)+1
			turnOn = turnOn && <-ch
		}

		if turnOn && !statusOn {
			inputMessage := `{"turn_on": true}`
			dataToShare = []byte(inputMessage)

			_, err := apiContext.InterestAPI.SendInputMessage(
				apiContext.CtxWithMeta,
				&ioticsApi.SendInputMessageRequest{
					Headers: &apiContext.Headers,
					Args: &ioticsApi.SendInputMessageRequest_Arguments{
						Interest: &ioticsApi.InputInterest{
							SenderTwinId: &ioticsApi.TwinID{Id: twinThermostatIdentity.Did()},
							DestInputId:  twinRadiatorList[0].GetInputs()[0].InputId,
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

			statusOn = true // Update radiator's status
		} else if !turnOn && statusOn {
			inputMessage := `{"turn_on": false}`
			dataToShare = []byte(inputMessage)

			_, err := apiContext.InterestAPI.SendInputMessage(
				apiContext.CtxWithMeta,
				&ioticsApi.SendInputMessageRequest{
					Headers: &apiContext.Headers,
					Args: &ioticsApi.SendInputMessageRequest_Arguments{
						Interest: &ioticsApi.InputInterest{
							SenderTwinId: &ioticsApi.TwinID{Id: twinThermostatIdentity.Did()},
							DestInputId:  twinRadiatorList[0].GetInputs()[0].InputId,
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

			statusOn = false // Update radiator's status
		}
	}

}
