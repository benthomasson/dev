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
options:
  updates:
    description:
      - A list of dictionaries, each a desired update to make
    type: list
    elements: dict
    required: True
    suboptions:
      path:
        description:
        - The path in a currently set variable to update
        - The path can be in dot or bracket notation
        - It should be a valid jinja reference
        type: str
        required: True
      value:
        description:
        - The value to be set at the path
        - Can be a simple or complex data structure
        type: raw
        required: True
  

notes:
  
author:
- Bradley Thornton (@cidrblock)
"""

EXAMPLES = r"""

# Update, use valid jinja dot or bracket notation
- name: Set a fact
  set_fact:
    a:
      b:
        c:
        - 1
        - 2

- name: Update the fact
  update_fact:
    a.b.c.0: 10
    a['b']['c'][1]: 20
  register: updated

# updated:
#   a:
#     b:
#       c:
#       - 10
#       - 20
#   changed: true

# Update and append to list, add new key
- name: Set a fact
  set_fact:
    a:
      b:
        b1:
        - 1
        - 2
          
- name: Update, add to list, add new key
  update_fact:
    a.b.b1.2: 3
    a.b.b2:
    - 10
    - 20
    - 30
  register: updated

# updated:
#   a:
#     b:
#       b1:
#       - 1
#       - 2
#       - 3
#       b2:
#       - 10
#       - 20
#       - 30
#   changed: true

# Retrieve, update, and apply interface description change

- name: Get the config interface config
  cisco.nxos.nxos_interfaces:
    state: gathered
  register: current

- name: Rekey the interface list using the interface name
  set_fact:
    current: "{{ current['gathered']|rekey_on_member('name') }}"

- name: Update the description of Ethernet1/1
  update_fact:
    current.Ethernet1/1.description: "Configured by ansible"
  register: updated

- name: Update the configuration
  cisco.nxos.nxos_interfaces:
    config: "{{ updated.current.values()|list }}"
    state: overridden
  register: result

- name: Show the commands issued
  debug:
    msg: "{{ result['commands'] }}"

# ok: [rtr01] => {
#     "msg": [
#         "interface Ethernet1/1",
#         "description Configured by ansible"
#     ]
# }

# Retrieve, update, and apply an ipv4 ACL change

- name: Get the config acls
  arista.eos.eos_acls:
    state: gathered
  register: current

- name: Extract the ipv4 acls
  set_fact:
    ipv4_acls: "{{ current['gathered']|selectattr('afi', 'equalto', 'ipv4')|list }}"

- name: Rekey the ACLs by name
  set_fact:
    ipv4_acls: "{{ ipv4_acls[0]['acls']|rekey_on_member('name') }}"

- name: Rekey the test1 ACL by sequence number
  set_fact:
    aces: "{{ ipv4_acls['test1']['aces']|rekey_on_member('sequence') }}"

- name: Update the source
  update_fact:
    aces.10.source:
      subnet_address: 192.168.1.0/24
  register: updated

- name: Update the device config
  arista.eos.eos_acls:
    config:
    - afi: ipv4
      acls:
      - name: test1
        aces: "{{ updated['aces'].values()|list }}"
    state: replaced
  register: changes

- debug:
    msg: "{{ changes['commands'] }}"

# ok: [eos101] => {
#     "msg": [
#         "ip access-list test1",
#         "no 10",
#         "10 permit ip 192.168.1.0/24 host 10.1.1.2"
#     ]
# }
 
"""
