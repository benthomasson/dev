from __future__ import absolute_import, division, print_function

__metaclass__ = type
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
        pattern = re.compile(r"\.(?![^[]*\])|\]\[|\[|\]")
        splitted = list(filter(None, pattern.split(path)))
        result = []
        for part in splitted:
            if part.isnumeric():
                result.append(int(part))
            else:
                result.append(re.sub("['\"]", "", part))
        return result

    def set_value(self, obj, path, val):
        first, rest = path[0], path[1:]
        if rest:
            new_obj = obj[first]
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
            parts = self._field_split(key)
            if len(parts) <= 1:
                msg = "update_fact requires a path in dot or bracket notation Found '{key}'".format(
                    key=key
                )
                raise AnsibleModuleError(msg)

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
