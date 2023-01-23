# IOTICS PRECONDITIONS

In order to guarantee the functionality of IOTICS, we would need to ensure the following services, ports and protocols are supported. This will need to be verified in corporate environments where firewalls and Internet proxies may affect successful operations:

- REST | HTTP 1.1 | https://ganymede.iotics.space:443/qapi
- STOMP over Websocket | HTTP 1.1 | wss://ganymede.iotics.space/ws
- gRPC | HTTP 2 | https://ganymede.iotics.space:10001
- gRPC Web | HTTP 2 / HTTP 1.1 | https://ganymede.iotics.space:11000

To make these checks easy for you we have prepared a script that performs automatically all of the above tests.

## Linux/MacOS

Execute the `iotics_test.sh` in this folder. If all the tests are successful you will see the following return values:

```bash
IOTICSpace Domain ---> OK
Resolver Domain ---> OK
gRPC Port ---> OK
HTTP 2 with TLS>=v1.2 Enabled ---> OK
gRPC-Web Request Test ---> OK
Websocket Connection ---> OK
```

If any of the tests fail (return value = `ERROR`) reach out to us as soon as possible.

## Windows

Execute the `iotics_test.ps1` in this folder via Windows PowerShell. If all the tests are successful you will see the following return values:

```bash
ComputerName     : ganymede.iotics.space
RemoteAddress    : xxx.xxx.xxx.xxx
RemotePort       : 443
InterfaceAlias   : Wi-Fi
SourceAddress    : xxx.xxx.xxx.xxx
TcpTestSucceeded : True

ComputerName     : ganymede.iotics.space
RemoteAddress    : xxx.xxx.xxx.xxx
RemotePort       : 11000
InterfaceAlias   : Wi-Fi
SourceAddress    : xxx.xxx.xxx.xxx
TcpTestSucceeded : True

ComputerName     : ganymede.iotics.space
RemoteAddress    : xxx.xxx.xxx.xxx
RemotePort       : 10001
InterfaceAlias   : Wi-Fi
SourceAddress    : xxx.xxx.xxx.xxx
TcpTestSucceeded : True

ComputerName     : did.prd.iotics.com
RemoteAddress    : 108.138.217.124
RemotePort       : 443
InterfaceAlias   : Wi-Fi
SourceAddress    : xxx.xxx.xxx.xxx
TcpTestSucceeded : True
```

If any of the tests fail (`TcpTestSucceeded: False`) reach out to us as soon as possible.