#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2019 XLAB d.o.o.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community"
}

DOCUMENTATION = """
---
module: pms
short_description: Checks for web service availability
description:
  - Ping a remote endpoint via HTTP.
author: Steampunk Team

options:
  auth:
    required: true
    description:
      - Authentication data
    suboptions:
      address:
        description:
          - Base address of the service.
      username:
        description:
          - Username to use when logging in.
      password:
        description:
          - Password to use when logging in.
  endpoint:
    required: true
    description:
      - Endpoint location that we should ping.
"""

EXAMPLES = """
- name: Ping service
  pms:
    auth:
      address: http://my.servi.ce
      username: user
      password: pass
    endpoint: /some/api/endpoint
"""

RETURN = """
status:
  description: Service status
  type: int
response:
  description: Response data from service
  type: string
"""


import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import Request, ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError


class Connection:
    def __init__(self, address):
        self._address = address.rstrip("/")
        self._headers = {}
        self._client = Request()

    def _request(self, method, path, payload=None):
        headers = self._headers.copy()
        data = None
        if payload:
            data = json.dumps(payload)
            headers["Content-Type"] = "application/json"

        url = self._address + path
        try:
            r = self._client.open(method, url, data=data, headers=headers)
            r_status = r.getcode()
            r_headers = dict(r.headers)
            data = r.read().decode("utf-8")
            r_data = json.loads(data) if data else {}
        except HTTPError as e:
            r_status = e.code
            r_headers = {}
            r_data = dict(msg=str(e.reason))
        except (ConnectionError, URLError) as e:
            raise AnsibleConnectionFailure(
                "Could not connect to {0}: {1}".format(url, e.reason)
            )
        return r_status, r_headers, r_data

    def get(self, path):
        return self._request("GET", path)

    def post(self, path, payload=None):
        return self._request("POST", path, payload)

    def delete(self, path):
        return self._request("DELETE", path)

    def login(self, username, password):
        status, headers, _ = self.post(
            "/tokens", dict(username=username, password=password),
        )
        self._headers["x-auth-token"] = headers["x-auth-token"]

    def logout(self):
        if "x-auth-token" in self._headers:
            self.delete("/tokens/" + self._headers["x-auth-token"])
            del self._headers["x-auth-token"]


def main():
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type="dict", required=True),
            endpoint=dict(type="str", required=True),
        ),
        supports_check_mode=False,
    )

    conn = Connection(module.params["auth"]["address"])
    conn.login(module.params["auth"]["username"],
               module.params["auth"]["password"])
    status, _, data = conn.get(module.params["endpoint"])
    conn.logout()
    module.exit_json(changed=True, status=status, response=str(data))


if __name__ == "__main__":
    main()
