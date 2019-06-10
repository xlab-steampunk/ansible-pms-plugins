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
  - This module uses pms connection!
author: Steampunk Team

options:
  endpoint:
    required: true
    description:
      - Endpoint location that we should ping.
"""

EXAMPLES = """
- name: Ping service
  pms:
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


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(type="str", required=True),
        ),
        supports_check_mode=False,
    )

    conn = Connection(module._socket_path)
    status, _, data = conn.get(module.params["endpoint"])
    module.exit_json(changed=True, status=status, response=str(data))


if __name__ == "__main__":
    main()
