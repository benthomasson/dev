#
# Copyright 2020 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
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

# Update an exisitng fact, dot or bracket notation
- name: Set a fact
  set_fact:
    a:
      b:
        c:
        - 1
        - 2

- name: Update the fact
  update_fact:
    updates:
    - path: a.b.c.0
      value: 10
    - path: "a['b']['c'][1]"
      value: 20
  register: updated

- debug:
    var: updated.a

# updated:
#   a:
#     b:
#       c:
#       - 10
#       - 20
#   changed: true


# Lists can be appended, new keys added to dictionaries

- name: Set a fact
  set_fact:
    a:
      b:
        b1:
        - 1
        - 2

- name: Update, add to list, add new key
  update_fact:
    updates:
    - path: a.b.b1.2
      value: 3
    - path: a.b.b2
      value:
      - 10
      - 20
      - 30
  register: updated

- debug:
    var: updated.a

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

- name: Get the current interface config
  cisco.nxos.nxos_interfaces:
    state: gathered
  register: current

- name: Rekey the interface list using the interface name
  set_fact:
    current: "{{ current['gathered']|rekey_on_member('name') }}"

- name: Update the description of Ethernet1/1
  ansible.netcommon.update_fact:
    updates:
    - path: current.Ethernet1/1.description
      value: "Configured by ansible"
  register: updated

- name: Update the configuration
  cisco.nxos.nxos_interfaces:
    config: "{{ updated.current.values()|list }}"
    state: overridden
  register: result

- name: Show the commands issued
  debug:
    msg: "{{ result['commands'] }}"

# TASK [Show the commands issued] *********
# ok: [sw01] =>
#   msg:
#   - interface Ethernet1/1
#   - description Configured by ansible


# Retrieve, update, and apply an ipv4 ACL change

- name: Retrieve the current acls
  arista.eos.eos_acls:
    state: gathered
  register: current

- name: Retrieve the index of the ipv4 acls
  set_fact:
    afi_index: "{{ idx }}"
  loop: "{{ current.gathered }}"
  loop_control:
    index_var: idx
  when: item.afi == 'ipv4'

- name: Retrieve the index of the test1 acl
  set_fact:
    acl_index: "{{ idx }}"
  loop: "{{ current.gathered[afi_index].acls }}"
  loop_control:
    index_var: idx
  when: item.name == 'test1'

- name: Retrieve the index of sequence 10
  set_fact:
    ace_index: "{{ idx }}"
  loop: "{{ current.gathered[afi_index].acls[acl_index].aces }}"
  loop_control:
    index_var: idx
  when: item.sequence == 10

- name: Update the fact
  ansible.netcommon.update_fact:
    updates:
    - path: current.gathered[{{ afi_index }}].acls[{{ acl_index }}].aces[{{ ace_index }}].source
      value:
        subnet_address: "192.168.1.0/24"
  register: updated

- name: Apply the changes
  arista.eos.eos_acls:
    config: "{{ updated.current.gathered }}"
    state: overridden
  register: changes

- name: Show the commands issued
  debug:
    var: changes.commands

# TASK [Show the commands issued] ***************
# ok: [eos101] =>
#   changes.commands:
#   - ip access-list test1
#   - no 10
#   - ip access-list test1
#   - 10 permit ip 192.168.20.0/24 host 10.1.1.2


# Disable ip_redirects on any layer3 interface

- name: Get the current interface config
  cisco.nxos.nxos_facts:
    gather_network_resources:
    - interfaces
    - l3_interfaces

- name: Rekey the interface lists using the interface name
  set_fact:
    l3_interfaces: "{{ ansible_network_resources['l3_interfaces']|rekey_on_member('name') }}"
    update_list: []

- name: Build the update list for any layer3 interface
  set_fact:
    update_list: "{{ update_list + update }}"
  loop: "{{ ansible_network_resources['interfaces'] }}"
  vars:
    update:
    - path: "l3_interfaces[{{ item['name'] }}]['redirects']"
      value: True
  when: item['mode']|default() == 'layer3'
  register: updates

- name: Apply the updates
  update_fact:
    updates: "{{ update_list }}"
  register: updated

- name: Update the configuration
  cisco.nxos.nxos_l3_interfaces:
    config: "{{ updated.l3_interfaces.values()|list }}"
    state: overridden
  register: result
  when: updated['changed']

- name: Show the commands issued
  debug:
    msg: "{{ result['commands'] }}"
  when: updated['changed']

# TASK [Show the commands issued] *******
# ok: [sw01] =>
#   msg:
#   - interface Ethernet1/10
#   - no ip redirects
"""
