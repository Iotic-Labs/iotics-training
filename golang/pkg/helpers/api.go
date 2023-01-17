package helpers

import (
	"context"
	"crypto/tls"
	"log"
	"time"

	ioticsApi "github.com/Iotic-Labs/iotics-api-grpc-go/iotics/api"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	grpc_meta "google.golang.org/grpc/metadata"
)

type IoticsApiContext struct {
	CtxWithMeta context.Context
	Headers     ioticsApi.Headers
	TwinAPI     ioticsApi.TwinAPIClient
	FeedAPI     ioticsApi.FeedAPIClient
	InputAPI    ioticsApi.InputAPIClient
	InterestAPI ioticsApi.InterestAPIClient
	SearchAPI   ioticsApi.SearchAPIClient
	MetaAPI     ioticsApi.MetaAPIClient
}

func grpcConnSetup(token string, hostGrpcUrl string) (context.Context, *grpc.ClientConn) {
	ctx := grpc_meta.AppendToOutgoingContext(context.Background(), "authorization", "bearer "+token)

	// This context is for limiting how long the connection attempt is made
	connCtx, cancel := context.WithTimeout(ctx, time.Second*30)
	defer cancel()

	tlsConfig := &tls.Config{}
	gRPCconn, err := grpc.DialContext(
		connCtx,
		hostGrpcUrl,
		grpc.WithBlock(),
		grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)),
	)
	if err != nil {
		log.Fatalf("Failed to create grpc conn %v ", err)
	}

	return ctx, gRPCconn
}

func GetApiContext(token string, host_grpc_url string, clientAppId string) IoticsApiContext {
	ctx, gRPCconn := grpcConnSetup(string(token), host_grpc_url)
	headers := ioticsApi.Headers{
		ClientAppId:    clientAppId,
		TransactionRef: []string{"IOTICS"},
	}

	return IoticsApiContext{
		CtxWithMeta: ctx,
		Headers:     headers,
		TwinAPI:     ioticsApi.NewTwinAPIClient(gRPCconn),
		FeedAPI:     ioticsApi.NewFeedAPIClient(gRPCconn),
		InputAPI:    ioticsApi.NewInputAPIClient(gRPCconn),
		InterestAPI: ioticsApi.NewInterestAPIClient(gRPCconn),
		SearchAPI:   ioticsApi.NewSearchAPIClient(gRPCconn),
		MetaAPI:     ioticsApi.NewMetaAPIClient(gRPCconn),
	}
}
