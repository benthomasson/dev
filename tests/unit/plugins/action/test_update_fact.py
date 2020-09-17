# (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.ansible.netcommon.tests.unit.compat import unittest
from ansible_collections.ansible.netcommon.tests.unit.compat.mock import (
    MagicMock,
    patch,
)
from ansible_collections.ansible.netcommon.tests.unit.mock.loader import (
    DictDataLoader,
)
from ansible_collections.cidrblock.dev.plugins.action.update_fact import (
    ActionModule,
)

SPLIT_TESTS = [
    ('a.b["4.4"][0]["1"].5[\'foo\']', ["a", "b", "4.4", 0, "1", 5, "foo"]),
    ("a.b[4.4][0][\"1\"].5['foo']", ["a", "b", 4.4, 0, "1", 5, "foo"]),
    ("a.['127.0.0.1']", ["a", "127.0.0.1"]),
    ("a.'127.0.0.1'", ["a", "127.0.0.1"]),
    ("a.b.'4.4'.c.d.e", ["a", "b", 4.4, "c", "d", "e"]),
    ("a.b['4.4'].c.d.e", ["a", "b", "4.4", "c", "d", "e"]),
    ("a.b[4.4].c.d.e", ["a", "b", 4.4, "c", "d", "e"]),
]


class TestUpdate_Fact(unittest.TestCase):
    def setUp(self):
        task = MagicMock(Task)
        play_context = MagicMock()
        play_context.check_mode = False
        connection = MagicMock()
        fake_loader = DictDataLoader({})
        templar = Templar(loader=fake_loader)
        self._plugin = ActionModule(
            task=task,
            connection=connection,
            play_context=play_context,
            loader=fake_loader,
            templar=templar,
            shared_loader_obj=None,
        )
        self._plugin._task.action = "update_fact"

    def test_argspec_dict(self):
        """Check passing a list"""
        self._plugin._task.args = [1, 2, 3]
        with self.assertRaises(Exception) as error:
            self._plugin.run(task_vars=None)
        self.assertIn(
            "Update_facts requires a dictionary", str(error.exception)
        )

    def test_argspec_none(self):
        """Check passing a dict"""
        self._plugin._task.args = None
        with self.assertRaises(Exception) as error:
            self._plugin.run(task_vars=None)
        self.assertIn(
            "Update_facts requires a dictionary", str(error.exception)
        )

    def test_fields(self):
        """Check the parsing of a path into it's parts"""
        for path, expected in SPLIT_TESTS:
            result = self._plugin._field_split(path)
            self.assertEqual(result, expected)

    def test_missing_var(self):
        """Check for a missing fact"""
        self._plugin._task.args = {"a.b.c": 5}
        with self.assertRaises(Exception) as error:
            self._plugin.run(task_vars={"vars": {}})
        self.assertIn(
            "'a' was not found in the current facts.", str(error.exception)
        )

    def test_run_simple(self):
        """Confirm a valid argspec passes"""

        task_vars = {"vars": {"a": {"b": [1, 2, 3]}}}
        self._plugin._task.args = {"a.b": 5}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["b"] = 5
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_1(self):
        """Replace in list"""

        task_vars = {"vars": {"a": {"b": [1, 2, 3]}}}
        self._plugin._task.args = {"a.b.1": 5}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["b"][1] = 5
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_2(self):
        """Append to list"""
        task_vars = {"vars": {"a": {"b": [1, 2, 3]}}}
        self._plugin._task.args = {"a.b.3": 4}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["b"].append(4)
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_3(self):
        """Bracket notation sigle quote"""
        task_vars = {"vars": {"a": {"b": [1, 2, 3]}}}
        self._plugin._task.args = {"a['b'][3]": 4}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["b"].append(4)
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_4(self):
        """Bracket notation double quote"""
        task_vars = {"vars": {"a": {"b": [1, 2, 3]}}}
        self._plugin._task.args = {'a["b"][3]': 4}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["b"].append(4)
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_5(self):
        """Integer dict keys"""
        task_vars = {"vars": {"a": {0: [1, 2, 3]}}}
        self._plugin._task.args = {"a.0.0": 0}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"][0][0] = 0
        expected.update({"changed": True})
        self.assertEqual(result, expected)

    def test_run_6(self):
        """Integer dict keys as string"""
        task_vars = {"vars": {"a": {"0": [1, 2, 3]}}}
        self._plugin._task.args = {'a.["0"].0': 0}
        result = self._plugin.run(task_vars=task_vars)
        expected = task_vars["vars"]
        expected["a"]["0"][0] = 0
        expected.update({"changed": True})
        self.assertEqual(result, expected)
