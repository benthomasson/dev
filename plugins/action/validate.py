from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from ansible.plugins.action import ActionBase
from ansible.module_utils.basic import missing_required_lib
from ansible.errors import AnsibleActionFail
from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic

from ..modules.validate import DOCUMENTATION

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    convert_doc_to_ansible_module_kwargs,
)

try:
    from jsonschema import Draft7Validator
    from jsonschema.exceptions import ValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class ActionModule(ActionBase):
    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = {}

    @staticmethod
    def generate_argspec():
        """Generate an argspec"""
        argspec = convert_doc_to_ansible_module_kwargs(DOCUMENTATION)
        # argspec = dict_merge(argspec, ARGSPEC_CONDITIONALS)
        return argspec

    def _fail_json(self, msg):
        """Replace the AnsibleModule fai_json here

        :param msg: The message for the failure
        :type msg: str
        """
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _check_argspec(self):
        """Load the doc and convert
        Add the root conditionals to what was returned from the conversion
        and instantiate an AnsibleModule to validate
        """
        argspec = self.generate_argspec()
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": self._task.args})
        )
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**argspec)

    def _check_reqs(self):
        """Check the prerequisites"""
        errors = []
        if not HAS_JSONSCHEMA:
            errors.append(missing_required_lib("jsonschema"))

        if errors:
            self._result["failed"] = True
            self._result["msg"] = " ".join(errors)

    @staticmethod
    def _to_path(fpath):
        return ".".join(str(index) for index in fpath)

    def _validate(self, schema, data):
        validator = Draft7Validator(schema)
        validation_errors = sorted(
            validator.iter_errors(data), key=lambda e: e.path
        )
        if validation_errors:
            self._result["failed"] = True
            self._result["msg"] = "Validation errors were found. "
            self._result["errors"] = []
            for validation_error in validation_errors:
                if isinstance(validation_error, ValidationError):
                    error = {
                        "message": validation_error.message,
                        "var_path": self._to_path(
                            validation_error.relative_path
                        ),
                        "schema_path": self._to_path(
                            validation_error.relative_schema_path
                        ),
                        "relative_schema": validation_error.schema,
                        "expected": validation_error.validator_value,
                        "validator": validation_error.validator,
                        "found": validation_error.instance,
                    }

                    self._result["errors"].append(error)
                    var_path = error["var_path"] or "root"
                    error_msg = "At '{var_path}' {ve}. ".format(
                        var_path=var_path, ve=validation_error.message
                    )
                    self._result["msg"] += error_msg

    def run(self, tmp=None, task_vars=None):
        self._check_argspec()
        self._check_reqs()
        if self._result.get("failed"):
            return self._result

        self._validate(
            schema=self._task.args["schema"], data=self._task.args["vars"]
        )
        if self._result.get("failed"):
            return self._result

        return self._result
