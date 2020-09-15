import re
import sys
from ansible.module_utils.basic import missing_required_lib
from ansible.errors import AnsibleModuleError
from ansible.module_utils._text import to_native

try:
    from lxml.etree import tostring, fromstring, XMLSyntaxError
except ImportError:
    from xml.etree.ElementTree import tostring, fromstring

    if sys.version_info < (2, 7):
        from xml.parsers.expat import ExpatError as XMLSyntaxError
    else:
        from xml.etree.ElementTree import ParseError as XMLSyntaxError


try:
    import xmltodict

    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False


def ensure_xml_or_str(data, field):
    if not data:
        tipe = None
    else:
        tipe = "str"
    result = data
    if isinstance(data, str) and (re.match(r"^<.+>$", data)):
        try:
            fromstring(filter)
            tipe = "xml"
        except XMLSyntaxError:
            pass
        except Exception as exc:
            error = "'{field}' recognized as XML but was not valid. ".format(
                field=field
            )
            raise AnsibleModuleError(error + to_native(exc))
    if isinstance(data, dict):
        if not HAS_XMLTODICT:
            msg = "{field} was provided as a dictionary, conversion to XML requires 'xmltodict'. ".format(
                field=field
            )
            raise AnsibleModuleError(msg + missing_required_lib("xmltodict"))
        try:
            result = xmltodict.unparse(data, full_document=False)
            tipe = "xml"
        except Exception as exc:
            error = "'{field}' was dictionary but conversion to XML failed. ".format(
                field=field
            )
            raise AnsibleModuleError(error + to_native(exc))
    return result, tipe


def xml_to_native(obj, field, full_doc=False, pretty=False):
    if not HAS_XMLTODICT:
        msg = "{field} was set to 'native, conversion from XML requires 'xmltodict'. ".format(
            field=field
        )
        raise AnsibleModuleError(msg + missing_required_lib("xmltodict"))
    try:
        return xmltodict.parse(obj, dict_constructor=dict)
    except Exception as exc:
        error = "'xmltodict' returned the following error when converting {field} from XML. ".format(
            field=field
        )
        raise AnsibleModuleError(error + to_native(exc))
