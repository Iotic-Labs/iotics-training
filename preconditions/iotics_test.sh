#!/bin/bash

CURRENT_DIR=$(pwd)
SPACE_NAME=${1:-"demo"}
HOST_ID=${2:-"did:iotics:iotF4bijjsnZJNaEYZJFXKqiDWBjPEFPWddr"}
IOTICSPACE_DOMAIN="https://$SPACE_NAME.iotics.space"
INDEX=$(curl -sL $IOTICSPACE_DOMAIN/index.json | tr , "\n" | grep ":")
GRPC_WEB=$(echo -e "$INDEX" | grep "grpc-web" | cut -d"\"" -f 4)
RESOLVER_DOMAIN=$(echo -e "$INDEX" | grep "resolver" | cut -d"\"" -f 4)
RESULTS_DIR="results.tar.gz"
TEST_OK="HTTP/2 200"

function_test() {
    local curl_cmd="curl -vs $1"
    echo "$curl_cmd" >$2
    local test=$($curl_cmd 2>>$2)
    if grep -q "$TEST_OK" $2; then
        echo $3 "---> PASSED"
    else
        echo $3 "---> NOT PASSED"
    fi
}

function_test "$IOTICSPACE_DOMAIN" "ioticspace_domain.txt" "IOTICSpace domain reacheable"
function_test "$RESOLVER_DOMAIN/1.0/discover/$HOST_ID" "resolver_domain.txt" "Resolver domain reacheable"
function_test "--http2-prior-knowledge $IOTICSPACE_DOMAIN" "http2.txt" "HTTP2 enabled"
function_test "--tlsv1.3 $IOTICSPACE_DOMAIN" "tls.txt" "TLS>=v1.3 enabled"
function_test "-H Content-Type:application/grpc-web+proto -X POST $GRPC_WEB/iotics.api.HostAPI/GetHostID" "grpc_web.txt" "gRPC-Web request test"
function_test "$IOTICSPACE_DOMAIN -H Connection:Upgrade -H Upgrade:websocket -H Host:${IOTICSPACE_DOMAIN#*//} -H Origin:$IOTICSPACE_DOMAIN -H Sec-WebSocket-Key:ub7NHQCl1doMcqj6TRfsJw== -H Sec-WebSocket-Version:13" "websocket.txt" "Websocket Connection"
tar -zcf $RESULTS_DIR *.txt
rm $CURRENT_DIR/*.txt
