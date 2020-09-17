from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: update_fact
short_description: Update currently set facts
version_added: "1.2"
description:
    - This module allows updating existing variables.
    - Variables are updated on a host-by-host basis.
    - Variable are not modified in place, instead they are returned by the module
    - This module is also supported for Windows targets.
options:
  key_value:
    description:
      - The C(set_fact) module takes key=value pairs as variables to update
      - The key should be in dot or bracket notation, indicating the path to update
      - Exisiting keys or list entries will be replaced by the value provided.
    required: true

notes:

author:
- Bradley Thornton (@cidrblock)
"""

EXAMPLES = r"""

"""
