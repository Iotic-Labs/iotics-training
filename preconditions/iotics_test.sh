#!/bin/bash

IOTICSPACE_DOMAIN="https://ganymede.iotics.space"
RESOLVER_DOMAIN="did.prd.iotics.com"
GRPC_WEB_PORT="11000"
GRPC_PORT="10001"
HTTPS_PORT="443"

function_test_port() {
    if [[ $(nc -vz ${IOTICSPACE_DOMAIN#*//} $2 2>&1 | grep -c succeeded) -eq 1 ]]; then
        echo $3 "---> OK"
    else
        echo $3 "---> ERROR"
    fi
}

function_test_http2() {
    if [[ $(curl -vso --http2-prior-knowledge $1 2>&1 | grep -c "HTTP/2 200") -eq 1 ]]; then
        echo $2 "---> OK"
    else
        echo $2 "---> ERROR"
    fi
}

function_test_port $IOTICSPACE_DOMAIN $HTTPS_PORT "https"
function_test_port $IOTICSPACE_DOMAIN $GRPC_WEB_PORT "grpc-web"
function_test_port $IOTICSPACE_DOMAIN $GRPC_PORT "gRPC"
function_test_port $RESOLVER_DOMAIN $HTTPS_PORT "Resolver"
function_test_http2 $IOTICSPACE_DOMAIN "HTTP2"
