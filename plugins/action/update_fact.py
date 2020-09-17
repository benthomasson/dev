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

    @staticmethod
    def _field_split(path):
        que = list(path)
        val = que.pop(0)
        fields = []
        try:
            while que:
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
                # found a ", pop until " and then get the next
                elif val == "'":
                    val = que.pop(0)
                    while val != "'":
                        field += val
                        val = que.pop(0)
                    val = que.pop(0)
                # found a ', pop until ' and then get the next
                elif val == '"':
                    val = que.pop(0)
                    while val != '"':
                        field += val
                        val = que.pop(0)
                    val = que.pop(0)
                # in a field, pop unitl ' or [, which indicates next field
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
            except KeyError:
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
                    obj[first] = val
                    self._result["changed"] = True

    def run(self, tmp=None, task_vars=None):
        self._task.diff = False
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._check_argspec()
        results = set()
        for key, value in self._task.args.items():
            print(key, value)
            parts = self._field_split(key)
            if len(parts) == 1:
                obj = parts[0]
                results.add(obj)
                retrieved = task_vars["vars"].get(obj)
                if not retrieved:
                    msg = "'{obj}' was not found in the current facts.".format(
                        obj=obj
                    )
                    raise AnsibleModuleError(msg)
                if retrieved != value:
                    task_vars["vars"][obj] = value
                    self._result["changed"] = True
            else:
                obj, path = parts[0], parts[1:]
                results.add(obj)
                retrieved = task_vars["vars"].get(obj)
                if not retrieved:
                    msg = "'{obj}' was not found in the current facts.".format(
                        obj=obj
                    )
                    raise AnsibleModuleError(msg)
                self.set_value(retrieved, path, value)

        for key in results:
            value = task_vars["vars"].get(key)
            self._result[key] = value
        return self._result
