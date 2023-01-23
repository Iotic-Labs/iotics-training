#!/bin/bash

SPACE_NAME="ganymede"
IOTICSPACE_DOMAIN="https://$SPACE_NAME.iotics.space"
RESOLVER_DOMAIN="https://did.prd.iotics.com"
HOST_ID="did:iotics:iotQYDB3DVsP1GpReFudw1NfqbVzni8czZKt"
WEBSOCKET_URL="wss://$SPACE_NAME.iotics.space/ws"
GRPC_WEB_PORT="11000"
GRPC_PORT="10001"
HTTPS_PORT="443"

function_test_curl_request() {
    if [[ $(curl -v -I $1 2>&1 | grep -c "Connected") -eq 1 ]]; then
        echo $2 "---> OK"
    else
        echo $2 "---> ERROR"
    fi
}

function_test_curl_request "$IOTICSPACE_DOMAIN:$HTTPS_PORT" "IOTICSpace Domain"
function_test_curl_request "$RESOLVER_DOMAIN:$HTTPS_PORT/1.0/discover/$HOST_ID" "Resolver Domain"
function_test_curl_request "$IOTICSPACE_DOMAIN:$GRPC_PORT" "gRPC Port"
function_test_curl_request "--http2-prior-knowledge --tlsv1.2 $IOTICSPACE_DOMAIN" "HTTP 2 with TLS>=v1.2 Enabled"
function_test_curl_request "-X POST $IOTICSPACE_DOMAIN:$GRPC_WEB_PORT/iotics.api.TwinAPI/ListAllTwins" "gRPC-Web Request Test"
function_test_curl_request "-H \"Connection: Upgrade\" -H \"Upgrade: websocket\" -H \"Host: ${IOTICSPACE_DOMAIN#*//}\" -H \"Origin: $IOTICSPACE_DOMAIN\" -H \"Sec-WebSocket-Key: ub7NHQCl1doMcqj6TRfsJw==\" -H \"Sec-WebSocket-Version: 13\" $IOTICSPACE_DOMAIN:$HTTPS_PORT" "Websocket Connection"
