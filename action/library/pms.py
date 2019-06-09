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
