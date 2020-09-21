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
import ast
import re
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleModuleError
from ansible.module_utils.common._collections_compat import (
    MutableMapping,
    MutableSequence,
)
from ansible.module_utils._text import to_native
from jinja2 import Template, TemplateSyntaxError


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._supports_async = True
        self._updates = None
        self._result = None

    def _check_argspec(self):
        if not isinstance(self._task.args, dict):
            msg = "Update_facts requires a dictionary of key value pairs"
            raise AnsibleModuleError(msg)

    def _ensure_valid_jinja(self):
        errors = []
        for key, _value in self._task.args.items():
            try:
                Template("{{" + key + "}}")
            except TemplateSyntaxError as exc:
                error = (
                    "While processing '{key}' found malformed key reference."
                    " Ensure syntax follows valid jinja format. The error was:"
                    " {error}"
                ).format(key=key, error=to_native(exc))
                errors.append(error)
        if errors:
            raise AnsibleModuleError(" ".join(errors))

    @staticmethod
    def _field_split(path):
        que = list(path)
        val = que.pop(0)
        fields = []
        try:
            while True:
                field = ""
                # found a '.', move to the next character
                if val == ".":
                    val = que.pop(0)
                # found a '[', pop until ']' and then get the next
                if val == "[":
                    val = que.pop(0)
                    while val != "]":
                        field += val
                        val = que.pop(0)
                    val = que.pop(0)
                else:
                    while val not in [".", "["]:
                        field += val
                        val = que.pop(0)
                try:
                    # make numbers numbers
                    fields.append(ast.literal_eval(field))
                except Exception:
                    # or strip the quotes
                    fields.append(re.sub("['\"]", "", field))
        except IndexError:
            # pop'ed past the end of the que
            # so add the final field
            try:
                fields.append(ast.literal_eval(field))
            except Exception:
                fields.append(re.sub("['\"]", "", field))
        return fields

    def set_value(self, obj, path, val):
        first, rest = path[0], path[1:]
        if rest:
            try:
                new_obj = obj[first]
            except (KeyError, TypeError):
                msg = (
                    "Error: the key '{first}' was not found "
                    "in {obj}.".format(obj=obj, first=first)
                )
                raise AnsibleModuleError(msg)
            self.set_value(new_obj, rest, val)
        else:
            if isinstance(obj, MutableMapping):
                if obj.get(first) != val:
                    self._result["changed"] = True
                    obj[first] = val
            elif isinstance(obj, MutableSequence):
                if not isinstance(first, int):
                    msg = (
                        "Error: {obj} is a list, "
                        "but index provided was not an integer: '{first}'"
                    ).format(obj=obj, first=first)
                    raise AnsibleModuleError(msg)
                if first > len(obj):
                    msg = "Error: {obj} not long enough for item #{first} to be set.".format(
                        obj=obj, first=first
                    )
                    raise AnsibleModuleError(msg)
                if first == len(obj):
                    obj.append(val)
                    self._result["changed"] = True
                else:
                    if obj[first] != val:
                        obj[first] = val
                        self._result["changed"] = True
            else:
                msg = "update_fact can only modify mutable objects."
                raise AnsibleModuleError(msg)

    def run(self, tmp=None, task_vars=None):
        self._task.diff = False
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._result["changed"] = False
        # self._check_argspec()
        results = set()
        self._ensure_valid_jinja()
        for entry in self._task.args['updates']:
            parts = self._field_split(entry['path'])
            if len(parts) == 1:
                obj = parts[0]
                results.add(obj)
                if obj not in task_vars["vars"]:
                    msg = "'{obj}' was not found in the current facts.".format(
                        obj=obj
                    )
                    raise AnsibleModuleError(msg)
                retrieved = task_vars["vars"].get(obj)
                if retrieved != entry['value']:
                    task_vars["vars"][obj] = entry['value']
                    self._result["changed"] = True
            else:
                obj, path = parts[0], parts[1:]
                results.add(obj)
                if obj not in task_vars["vars"]:
                    msg = "'{obj}' was not found in the current facts.".format(
                        obj=obj
                    )
                    raise AnsibleModuleError(msg)
                retrieved = task_vars["vars"].get(obj)
                self.set_value(retrieved, path, entry['value'])

        for key in results:
            value = task_vars["vars"].get(key)
            self._result[key] = value
        return self._result
