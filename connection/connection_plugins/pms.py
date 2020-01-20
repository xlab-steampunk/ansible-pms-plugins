# coding: utf-8 -*-

# Copyright (c) 2019 XLAB d.o.o.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
author: Steampunk Team
connection: pms
short_description: Use pms to ping web services
description:
  - This connection plugin provides a connection to remote APIs over a HTTP(S).
version_added: null
options:
  address:
    description:
      - Specifies the web API address to establish the HTTP(S) connection to.
    required: true
    vars:
      - name: ansible_pms_address
  username:
    description:
      - The username used to authenticate to the API.
    vars:
      - name: ansible_pms_username
  password:
    description:
      - Configures the user password used to authenticate to the API.
    vars:
      - name: ansible_pms_password
  persistent_connect_timeout:
    type: int
    description:
      - Configures, in seconds, the amount of time to wait when trying to
        initially establish a persistent connection.  If this value expires
        before the connection to the remote device is completed, the connection
        will fail.
    default: 30
    env:
      - name: ANSIBLE_PERSISTENT_CONNECT_TIMEOUT
    vars:
      - name: ansible_connect_timeout
  persistent_command_timeout:
    type: int
    description:
      - Configures, in seconds, the amount of time to wait for a command to
        return from the remote device.  If this timer is exceeded before the
        command returns, the connection plugin will raise an exception and
        close.
    default: 30
    env:
      - name: ANSIBLE_PERSISTENT_COMMAND_TIMEOUT
    vars:
      - name: ansible_command_timeout
  persistent_log_messages:
    type: boolean
    description:
      - Log jsonrpc messages to log file
    default: False
    env:
      - name: ANSIBLE_PERSISTENT_LOG_MESSAGES
    vars:
      - name: ansible_persistent_log_messages
"""

import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.urls import Request, ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.plugins.connection import ConnectionBase, ensure_connect
from ansible.plugins.loader import connection_loader


class Connection(ConnectionBase):
    force_persistence = True
    transport = "pms"

    def __init__(self, play_context, *args, **kwargs):
        super(Connection, self).__init__(play_context, *args, **kwargs)
        self._messages = []
        self._sub_plugin = {}
        self._conn_closed = False

        # We are, for the most part, just a local connection that knows how to
        # perform HTTP requests.
        self._local = connection_loader.get("local", play_context, "/dev/null")
        self._local.set_options()

        self._headers = {}

    def _connect(self):
        if self._connected:
            return

        self._address = self.get_option("address").rstrip("/")
        self._client = Request()

        # Login
        status, headers, _ = self._request("POST", "/tokens", dict(
            username=self.get_option("username"),
            password=self.get_option("password"),
        ))
        self._headers["x-auth-token"] = headers["x-auth-token"]

        self._local._connect()
        self._connected = True

    def exec_command(self, *args, **kwargs):
        return self._local.exec_command(*args, **kwargs)

    def put_file(self, in_path, out_path):
        return self._local.put_file(in_path, out_path)

    def fetch_file(self, in_path, out_path):
        return self._local.fetch_file(in_path, out_path)

    def close(self):
        self._conn_closed = True
        if not self._connected:
            return

        self._local.close()
        if "x-auth-token" in self._headers:
            self.delete("/tokens/" + self._headers["x-auth-token"])
            del self._headers["x-auth-token"]
        self._connected = False

    def queue_message(self, level, message):
        self._messages.append((level, message))

    def pop_messages(self):
        messages, self._messages = self._messages, []
        return messages

    def _log_messages(self, data):
        pass

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

    @ensure_connect
    def get(self, path):
        return self._request("GET", path)

    @ensure_connect
    def post(self, path, payload=None):
        return self._request("POST", path, payload)

    @ensure_connect
    def delete(self, path):
        return self._request("DELETE", path)
