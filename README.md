# Ping my service Ansible plugins

This repository contains source code for various Ansible plugins that
demonstrate various ways of interacting with web APIs using Ansible.

The `server.py` file contains a mock web service that the plugins can be
tested against. We can start the server by running:

    $ python3 server.py

To login into the service, we must send a `POST` request to the `/tokens`
enspoint. The returned `x-auth-token` header can then be used to authenticate
all subsequent requests. When we are done, we should terminate the session by
sending a `DELETE` request to the `/tokens/<token>` endpoint.

    $ curl -v -X POST -H "content-type: application/json" \
        -d '{"username": "user", "password": "pass"}' \
        localhost:8000/tokens \
      2>&1 | grep x-auth-token
    $ curl -H "x-auth-token: 123" localhost:8000/test/me
    $ curl -X DELETE -H "x-auth-token: 123" localhost:8000/tokens/123
