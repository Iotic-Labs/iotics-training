$IOTICSPACE_DOMAIN="ganymede.iotics.space"
$RESOLVER_DOMAIN="did.prd.iotics.com"
$GRPC_WEB_PORT="11000"
$GRPC_PORT="10001"
$HTTPS_PORT="443"

Test-NetConnection -ComputerName $IOTICSPACE_DOMAIN -Port $HTTPS_PORT
Test-NetConnection -ComputerName $IOTICSPACE_DOMAIN -Port $GRPC_WEB_PORT
Test-NetConnection -ComputerName $IOTICSPACE_DOMAIN -Port $GRPC_PORT
Test-NetConnection -ComputerName $RESOLVER_DOMAIN -Port $HTTPS_PORT

pause
