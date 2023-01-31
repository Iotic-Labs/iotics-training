# IOTICS PRECONDITIONS

In order to guarantee the functionality of IOTICS, we would need to ensure the following services, ports and protocols are supported. This will need to be verified in corporate environments where firewalls and Internet proxies may affect successful operations:

- REST | HTTP 1.1
- Websocket Connection | HTTP 1.1
- gRPC | HTTP 2
- gRPC Web | HTTP 2 / HTTP 1.1
- TLS >= v1.2

To make these checks easy for you we have prepared a script that performs automatically all of the above tests.

## Linux/MacOS/WSL

Execute the `iotics_test.sh` in this folder. If all the tests are successful you will see the following return values:

```bash
IOTICSpace domain reacheable ---> PASSED
Resolver domain reacheable ---> PASSED
HTTP2 enabled ---> PASSED
TLS>=v1.2 enabled ---> PASSED
gRPC port unblocked ---> PASSED
gRPC-Web request test ---> PASSED
Websocket Connection ---> PASSED
```

A compressed folder called **results.tar.gz** will be automatically created with the tests' results.

If any of the tests fail (`NOT PASSED`) contact us at [support.iotics.com](https://support.iotics.com) with the `results` folder.
