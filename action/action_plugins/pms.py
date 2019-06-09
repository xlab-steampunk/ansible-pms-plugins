# coding: utf-8 -*-

# Copyright (c) 2019 XLAB d.o.o.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.urls import Request, ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.plugins.action import ActionBase


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


class ActionModule(ActionBase):
    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._supports_check_mode = False

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        result["changed"] = True

        conn = Connection(self._task.args["auth"]["address"])
        conn.login(self._task.args["auth"]["username"],
                   self._task.args["auth"]["password"])
        status, _, data = conn.get(self._task.args["endpoint"])
        conn.logout()

        result.update(status=status, response=str(data))
        return result
