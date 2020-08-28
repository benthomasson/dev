#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
module: validate
author: Bradley Thornton (@cidrblock)
short_description: Validate
description:
- Validate
version_added: 0.0.1
options:
    vars:
        type: raw
        description:
        - A list or dict of vars
        required: True
    schema:
        type: dict
        description:
        - The schema
        required: True

notes:
- Some notes
"""


EXAMPLES = r"""
"""

RETURN = r"""

"""
