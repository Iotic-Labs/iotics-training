#!/bin/bash

CURRENT_DIR=$(pwd)
SPACE_NAME=${1:-"demo"}
IOTICSPACE_DOMAIN="https://$SPACE_NAME.iotics.space"
INDEX=$(curl -sL $IOTICSPACE_DOMAIN/index.json | tr , "\n" | grep ":")
GRPC_WEB=$(echo -e "$INDEX" | grep "grpc-web" | cut -d"\"" -f 4)
RESOLVER_DOMAIN=$(echo -e "$INDEX" | grep "resolver" | cut -d"\"" -f 4)
RESULTS_DIR="results.tar.gz"
GET_OK="HTTP/2 200"
CONNECTED_OK="Connected"

function_test() {
    local curl_cmd="curl -vs $1"
    echo "$curl_cmd" >$2
    local test=$($curl_cmd 2>>$2)
    if grep -q "$3" $2; then
        echo $4 "---> PASSED"
    else
        echo $4 "---> NOT PASSED"
    fi
}

function_test "$IOTICSPACE_DOMAIN" "ioticspace_domain.txt" "$CONNECTED_OK" "IOTICSpace domain reacheable"
function_test "$RESOLVER_DOMAIN" "resolver_domain.txt" "$CONNECTED_OK" "Resolver domain reacheable"
function_test "--http2-prior-knowledge $IOTICSPACE_DOMAIN" "http2.txt" "Using HTTP2" "HTTP2 enabled"
function_test "--tlsv1.3 $IOTICSPACE_DOMAIN" "tls.txt" "TLSv1.3 (OUT), TLS handshake, Finished" "TLS>=v1.3 enabled"
function_test "-H Content-Type:application/grpc-web+proto -X POST $GRPC_WEB/iotics.api.HostAPI/GetHostID" "grpc_web.txt" "$GET_OK" "gRPC-Web request test"
function_test "$IOTICSPACE_DOMAIN -H Connection:Upgrade -H Upgrade:websocket -H Host:${IOTICSPACE_DOMAIN#*//} -H Origin:$IOTICSPACE_DOMAIN -H Sec-WebSocket-Key:ub7NHQCl1doMcqj6TRfsJw== -H Sec-WebSocket-Version:13" "websocket.txt" "$GET_OK" "Websocket Connection"
tar -zcf $RESULTS_DIR *.txt
rm $CURRENT_DIR/*.txt
