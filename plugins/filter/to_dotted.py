from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import (
    Mapping,
    MutableMapping,
)

from ansible_collections.cidrblock.dev.plugins.module_utils.dot_utils import (
    to_dotted,
)


def dotme(obj):
    return to_dotted(obj)


class FilterModule(object):
    """ Network filter """

    def filters(self):
        return {"to_dotted": dotme}
