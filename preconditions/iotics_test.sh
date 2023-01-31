#!/bin/bash

CURRENT_DIR=$(pwd)
SPACE_NAME=${1:-ganymede}
HTTPS_PREFIX="https://"
IOTICSPACE_DOMAIN="$HTTPS_PREFIX$SPACE_NAME.iotics.space"
INDEX=$(curl -sL $IOTICSPACE_DOMAIN/index.json | tr , "\n" | grep ":")
GRPC_WEB=$(echo -e "$INDEX" | grep "grpc-web" | cut -d"\"" -f 4)
GRPC=$(echo -e "$INDEX" | grep "grpc" | cut -d"\"" -f 4)
RESOLVER_DOMAIN=$(echo -e "$INDEX" | grep "resolver" | cut -d"\"" -f 4)
HOST_ID="did:iotics:iotQYDB3DVsP1GpReFudw1NfqbVzni8czZKt"
RESULTS_DIR="results.tar.gz"

function_test() {
    local curl_cmd="curl -vs $1"
    echo "$curl_cmd" >$2
    local test=$($curl_cmd 2>>$2)
    if grep -q "Connected" $2; then
        echo $3 "---> PASSED"
    else
        echo $3 "---> NOT PASSED"
    fi
}

function_test "$IOTICSPACE_DOMAIN" "ioticspace_domain.txt" "IOTICSpace domain reacheable"
function_test "$RESOLVER_DOMAIN/1.0/discover/$HOST_ID" "resolver_domain.txt" "Resolver domain reacheable"
function_test "--http2-prior-knowledge $IOTICSPACE_DOMAIN" "http2.txt" "HTTP2 enabled"
function_test "--tlsv1.2 $IOTICSPACE_DOMAIN" "tls.txt" "TLS>=v1.2 enabled"
function_test "$HTTPS_PREFIX$GRPC" "grpc_port.txt" "gRPC port unblocked"
function_test "-X POST $HTTPS_PREFIX$GRPC_WEB/iotics.api.TwinAPI/GetHostId" "grpc_web.txt" "gRPC-Web request test"
function_test "--http1.1 $IOTICSPACE_DOMAIN -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Host: ${IOTICSPACE_DOMAIN#*//}' -H 'Origin: $IOTICSPACE_DOMAIN' -H 'Sec-WebSocket-Key: ub7NHQCl1doMcqj6TRfsJw==' -H 'Sec-WebSocket-Version: 13'" "websocket.txt" "Websocket Connection"
tar -zcf $RESULTS_DIR *.txt
rm $CURRENT_DIR/*.txt
