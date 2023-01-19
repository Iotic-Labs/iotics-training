# IOTICS PRECONDITIONS

In order to guarantee the full streaming functionality of IOTICS, we would need:
- **HTTP2** to be enabled with your environment;
- web traffic to be allowed on ports **10001** (gRPC) and **11000** (gRPC-Web).
- We would also need to ensure the domains `.iotics.space` and `did.prd.iotics.com` will not be blocked

To make these checks easy for you we have prepared a script that performs automatically all of the above tests.

## Linux/MacOS

Execute the `iotics_test.sh` in this folder. If all the tests are successful you will see the following return values:

```bash
https ---> OK
grpc-web ---> OK
gRPC ---> OK
Resolver ---> OK
HTTP2 ---> OK
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