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

	userIdentity, agentIdentity := helpers.CreateUserAndAgentWithAuthDelegation(
		resolverClient,
		USER_SEED, USER_KEY_NAME,
		AGENT_SEED, AGENT_KEY_NAME,
	)

	token := helpers.GetToken(agentIdentity, userIdentity, 600)
	apiContext := helpers.GetApiContext(token, HOST_GRPC_URL, "Publisher Connector")

	/*** CREATE TWIN TEMPERATURE MODEL WITH CONTROL DELEG ***/
	/* Let's now use the HighLevel Identity library to create a new Twin Identity
	   and perform the Control Delegation with a single operation.
	   For the sake of this exercise, the Twin Model doesn't need any change to the AllowLists' (it can be not findable).
	   We want to use the Upsert operation as it combines multiple operations into a single one */
	twinTempModelIdentity := helpers.CreateTwinWithControlDelegation(resolverClient, AGENT_SEED, "TempModel", agentIdentity)

	response, err := apiContext.TwinAPI.UpsertTwin(
		apiContext.CtxWithMeta,
		&ioticsApi.UpsertTwinRequest{
			Headers: &apiContext.Headers,
			Payload: &ioticsApi.UpsertTwinRequest_Payload{
				TwinId: &ioticsApi.TwinID{Id: twinTempModelIdentity.Did()},
				Properties: []*ioticsApi.Property{
					{
						Key: helpers.PROPERTY_KEY_TYPE,
						Value: &ioticsApi.Property_UriValue{
							UriValue: &ioticsApi.Uri{
								Value: helpers.PROPERTY_VALUE_MODEL,
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_LABEL,
						Value: &ioticsApi.Property_LangLiteralValue{
							LangLiteralValue: &ioticsApi.LangLiteral{
								Value: "Temperature Sensor Model - LP",
								Lang:  "en",
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_COMMENT,
						Value: &ioticsApi.Property_LangLiteralValue{
							LangLiteralValue: &ioticsApi.LangLiteral{
								Value: "Model of a Temperature Sensor Twin",
								Lang:  "en",
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_SPACE_NAME,
						Value: &ioticsApi.Property_StringLiteralValue{
							StringLiteralValue: &ioticsApi.StringLiteral{
								Value: "Space A",
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_COLOR,
						Value: &ioticsApi.Property_StringLiteralValue{
							StringLiteralValue: &ioticsApi.StringLiteral{
								Value: "#9aceff",
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_CREATED_BY,
						Value: &ioticsApi.Property_StringLiteralValue{
							StringLiteralValue: &ioticsApi.StringLiteral{
								Value: "Lorenzo",
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_DEFINES,
						Value: &ioticsApi.Property_UriValue{
							UriValue: &ioticsApi.Uri{
								Value: helpers.PROPERTY_VALUE_SAREF_TEMPERATURE_SENSOR,
							},
						},
					},
					{
						Key: helpers.PROPERTY_KEY_SAREF_HAS_MODEL,
						Value: &ioticsApi.Property_StringLiteralValue{
							StringLiteralValue: &ioticsApi.StringLiteral{
								Value: "SET-LATER",
							},
						},
					},
				},
				Feeds: []*ioticsApi.UpsertFeedWithMeta{
					{
						Id: "temperature",
						Properties: []*ioticsApi.Property{
							{
								Key: helpers.PROPERTY_KEY_LABEL,
								Value: &ioticsApi.Property_LangLiteralValue{
									LangLiteralValue: &ioticsApi.LangLiteral{
										Value: "Temperature",
										Lang:  "en",
									},
								},
							},
							{
								Key: helpers.PROPERTY_KEY_COMMENT,
								Value: &ioticsApi.Property_LangLiteralValue{
									LangLiteralValue: &ioticsApi.LangLiteral{
										Value: "Current temperature of a Room",
										Lang:  "en",
									},
								},
							},
						},
						Values: []*ioticsApi.Value{
							{
								Label:    "reading",
								Comment:  "Temperature in Celsius degrees",
								DataType: "integer",
								Unit:     helpers.UNIT_DEGREE_CELSIUS,
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
	log.Printf("Upsert Twin response: %s", response.Payload)
	log.Printf("Twin Model DID: %s", twinTempModelIdentity.Did())

	/*** CREATE 2 TWINS OF TEMPERATURE SENSOR FROM THAT MODEL ***/
	/* Let's copy-paste the entire Twin Model upsert info with the right changes:
	   - twin_did
	   - 1st Twin Property
	   - Label
	   - Comment
	   - hostMetadataAllowList
	   - hostAllowList.
	   The Twins' setup phase ends here. */

	var twinIds []string

	for roomNumber := 1; roomNumber <= 2; roomNumber++ {
		twinTemperatureIdentity := helpers.CreateTwinWithControlDelegation(
			resolverClient,
			AGENT_SEED, fmt.Sprintf("Sensor%d", roomNumber),
			agentIdentity,
		)

		_, err = apiContext.TwinAPI.UpsertTwin(
			apiContext.CtxWithMeta,
			&ioticsApi.UpsertTwinRequest{
				Headers: &apiContext.Headers,
				Payload: &ioticsApi.UpsertTwinRequest_Payload{
					TwinId: &ioticsApi.TwinID{Id: twinTemperatureIdentity.Did()},
					Properties: []*ioticsApi.Property{
						{
							Key: helpers.PROPERTY_KEY_FROM_MODEL,
							Value: &ioticsApi.Property_UriValue{
								UriValue: &ioticsApi.Uri{
									Value: twinTempModelIdentity.Did(),
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_LABEL,
							Value: &ioticsApi.Property_LangLiteralValue{
								LangLiteralValue: &ioticsApi.LangLiteral{
									Value: fmt.Sprintf("Temperature Sensor LP - Room %d", roomNumber),
									Lang:  "en",
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_COMMENT,
							Value: &ioticsApi.Property_LangLiteralValue{
								LangLiteralValue: &ioticsApi.LangLiteral{
									Value: fmt.Sprintf("Temperature Sensor Twin - Room %d", roomNumber),
									Lang:  "en",
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_SPACE_NAME,
							Value: &ioticsApi.Property_StringLiteralValue{
								StringLiteralValue: &ioticsApi.StringLiteral{
									Value: "Space A",
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_COLOR,
							Value: &ioticsApi.Property_StringLiteralValue{
								StringLiteralValue: &ioticsApi.StringLiteral{
									Value: "#9aceff",
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_CREATED_BY,
							Value: &ioticsApi.Property_StringLiteralValue{
								StringLiteralValue: &ioticsApi.StringLiteral{
									Value: "Lorenzo Paris",
								},
							},
						},
						// Saref TemperatureSensor Ontology
						// Some of the properties of this ontology can be used to add more description to the Sensor
						{
							Key: helpers.PROPERTY_KEY_DEFINES,
							Value: &ioticsApi.Property_UriValue{
								UriValue: &ioticsApi.Uri{
									Value: helpers.PROPERTY_VALUE_SAREF_TEMPERATURE_SENSOR,
								},
							},
						},
						// Add "hasModel" property
						{
							Key: helpers.PROPERTY_KEY_SAREF_HAS_MODEL,
							Value: &ioticsApi.Property_StringLiteralValue{
								StringLiteralValue: &ioticsApi.StringLiteral{Value: "T1234"},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
							Value: &ioticsApi.Property_UriValue{
								UriValue: &ioticsApi.Uri{
									Value: helpers.PROPERTY_VALUE_ALLOW_ALL_HOSTS,
								},
							},
						},
						{
							Key: helpers.PROPERTY_KEY_HOST_ALLOW_LIST,
							Value: &ioticsApi.Property_UriValue{
								UriValue: &ioticsApi.Uri{
									Value: helpers.PROPERTY_VALUE_ALLOW_ALL_HOSTS,
								},
							},
						},
					},
					Feeds: []*ioticsApi.UpsertFeedWithMeta{
						{
							Id: "temperature",
							Properties: []*ioticsApi.Property{
								{
									Key: helpers.PROPERTY_KEY_LABEL,
									Value: &ioticsApi.Property_LangLiteralValue{
										LangLiteralValue: &ioticsApi.LangLiteral{
											Value: "Temperature",
											Lang:  "en",
										},
									},
								},
								{
									Key: helpers.PROPERTY_KEY_COMMENT,
									Value: &ioticsApi.Property_LangLiteralValue{
										LangLiteralValue: &ioticsApi.LangLiteral{
											Value: "Current temperature of a Room",
											Lang:  "en",
										},
									},
								},
							},
							Values: []*ioticsApi.Value{
								{
									Label:    "reading",
									Comment:  "Temperature in Celsius degrees",
									DataType: "integer",
									Unit:     helpers.UNIT_DEGREE_CELSIUS,
								},
							},
						},
					},
					Location: &ioticsApi.GeoLocation{
						Lat: 51.864, Lon: -0.412,
					},
				},
			},
		)
		if err != nil {
			log.Fatalf("Could not Upsert Twin: %v", err)
		}
		log.Printf("Twin created DID: %s", twinTemperatureIdentity.Did())

		// Update mapping
		twinIds = append(twinIds, twinTemperatureIdentity.Did())
	}

	/*** SHARE DATA ***/
	/* For each Twin we want to generate a random tenmperature and share the data */
	for {
		for _, twinId := range twinIds {
			randTemp := 10 + rand.Intn(16)
			messageToShare := fmt.Sprintf(`{"reading": %d}`, randTemp)
			dataToShare := []byte(messageToShare)

			apiContext.FeedAPI.ShareFeedData(
				apiContext.CtxWithMeta,
				&ioticsApi.ShareFeedDataRequest{
					Headers: &apiContext.Headers,
					Args: &ioticsApi.ShareFeedDataRequest_Arguments{
						FeedId: &ioticsApi.FeedID{
							Id:     "temperature",
							TwinId: twinId,
						},
					},
					Payload: &ioticsApi.ShareFeedDataRequest_Payload{
						Sample: &ioticsApi.FeedData{
							Data: dataToShare,
						},
					},
				},
			)

			log.Printf("Shared %s from Twin %s", messageToShare, twinId)
		}

		time.Sleep(5 * time.Second)
	}
}
