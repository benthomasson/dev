import json
from ansible.errors import AnsibleFilterError
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import missing_required_lib


try:
    import xmltodict

    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False


def _check_reqs(filter_name):
    if not HAS_XMLTODICT:
        msg = (
            "Filter plugin `{filter_name}` returned the following error: {err}".format(
                filter_name=filter_name, err=missing_required_lib("xmltodict")
            )
        )
        raise AnsibleFilterError(msg)


def from_xml(obj):
    filter_name = "from_xml"
    _check_reqs(filter_name)
    try:
        dyct = xmltodict.parse(obj, dict_constructor=dict)
    except Exception as exc:
        msg = "'xmltodict' returned the following error in the '{filter_name}' filter plugin: {err}".format(
            filter_name=filter_name, err=to_native(exc)
        )
        raise AnsibleFilterError(msg)
    try:
        return dyct
    except Exception as exc:
        msg = "Error after xml conversion in the '{filter_name}' filter plugin: {err}".format(
            filter_name=filter_name, err=to_native(exc)
        )
        raise AnsibleFilterError(msg)


def to_xml(obj, full_doc=False, pretty=False):
    filter_name = "to_xml"
    _check_reqs(filter_name)

    errors = []
    for param in [full_doc, pretty]:
        if not isinstance(param, bool):
            msg = "The value passed to {filter_name} for {param} is required to be a boolean".format(
                filter_name=filter_name, param=param
            )
            errors.append(msg)
    if errors:
        raise AnsibleFilterError(msg)

    if not isinstance(full_doc, bool):
        msg = "The value passed to {filter_name} for 'full_doc' is required to be a boolean".format(
            filter_name=filter_name
        )
        raise AnsibleFilterError(msg)

    try:
        xmlstr = xmltodict.unparse(obj, full_document=full_doc, pretty=pretty)
        return xmlstr
    except Exception as exc:
        msg = "'xmltodict' returned the following error in the '{filter_name}' filter plugin: {err}".format(
            filter_name=filter_name, err=to_native(exc)
        )
        raise AnsibleFilterError(msg)


class FilterModule(object):
    """ XML conversion filters """

    def filters(self):
        return {"to_xml": to_xml, "from_xml": from_xml}
