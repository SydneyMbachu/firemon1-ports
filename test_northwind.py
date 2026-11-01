import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from northwind import assess

ROOT = Path(__file__).resolve().parent


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((ROOT / 'case.json').read_text())

    def decisions(self, scenario):
        return [row[3] for row in assess(self.case, scenario)]

    def test_current_blocks_api_and_ssh(self):
        self.assertEqual(self.decisions('current'), [False, False])

    def test_broad_allows_api_and_unwanted_ssh(self):
        self.assertEqual(self.decisions('broad'), [True, True])

    def test_scoped_allows_only_api(self):
        self.assertEqual(self.decisions('scoped'), [True, False])

    def test_firewall_permission_alone_is_insufficient(self):
        self.case['security_group']['allowed_tcp_ports'] = []
        self.assertEqual(self.decisions('broad'), [False, False])

    def test_security_group_permission_alone_is_insufficient(self):
        rows = assess(self.case, 'current')
        self.assertTrue(all(row[2] for row in rows))
        self.assertTrue(all(not row[3] for row in rows))

    def test_decisions_follow_modified_input_not_hardcoded_table(self):
        self.case['security_group']['allowed_tcp_ports'] = [22]
        self.assertEqual(self.decisions('scoped'), [False, False])
        self.assertEqual(self.decisions('broad'), [False, True])

    def test_scoped_preserves_existing_firewall_permission(self):
        self.case['checks'].append({'name': 'Legacy', 'port': 8080, 'should_allow': True})
        self.case['security_group']['allowed_tcp_ports'].append(8080)
        self.assertTrue(self.decisions('scoped')[2])

    def test_evaluation_preserves_input_and_file(self):
        before = copy.deepcopy(self.case)
        disk = (ROOT / 'case.json').read_bytes()
        for scenario in ['current', 'broad', 'scoped']:
            assess(self.case, scenario)
        self.assertEqual(before, self.case)
        self.assertEqual(disk, (ROOT / 'case.json').read_bytes())

    def test_cli_runs_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            for scenario, failures in [('current', 1), ('broad', 1), ('scoped', 0)]:
                result = subprocess.run(
                    [sys.executable, str(ROOT / 'northwind.py'), scenario],
                    cwd=directory, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.count('FAIL'), failures)

    def test_invalid_scenario_is_rejected(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'northwind.py'), 'typo'],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_main_script_is_under_50_lines(self):
        self.assertLess(len((ROOT / 'northwind.py').read_text().splitlines()), 50)


if __name__ == '__main__':
    unittest.main()
