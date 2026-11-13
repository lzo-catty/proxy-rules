import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

from scripts.verify import wait_for_providers


class ProviderStartupTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"pr-direct": 10, "pr-custom-direct": 0}
        self.ready = {"providers": {name: {"ruleCount": count} for name, count in self.expected.items()}}
        self.running = SimpleNamespace(poll=lambda: None)

    def poll(self, replies, process=None):
        opener = Mock()
        opener.open.side_effect = [
            reply if isinstance(reply, Exception) else io.StringIO(json.dumps(reply))
            for reply in replies
        ]
        with patch("scripts.verify.time.sleep"):
            return wait_for_providers(opener, 1234, process or self.running,
                                      self.expected, attempts=len(replies))

    def test_null_then_empty_then_partial_then_ready(self):
        actual = self.poll([
            {"providers": None}, {"providers": {}},
            {"providers": {"pr-direct": {"ruleCount": 10}}}, self.ready,
        ])
        self.assertEqual(actual, self.expected)

    def test_waits_for_rule_counts_after_registry_exists(self):
        self.assertEqual(self.poll([
            {"providers": {"pr-direct": {"ruleCount": 0}, "pr-custom-direct": {"ruleCount": 0}}},
            self.ready,
        ]), self.expected)

    def test_permanently_null_registry_fails_instead_of_passing(self):
        with self.assertRaisesRegex(RuntimeError, "Providers not ready"):
            self.poll([{"providers": None}] * 3)

    def test_incorrect_counts_still_fail(self):
        with self.assertRaisesRegex(RuntimeError, "counts differ"):
            self.poll([{"providers": {"pr-direct": {"ruleCount": 9}, "pr-custom-direct": {"ruleCount": 0}}}])

    def test_unexpected_provider_still_fails(self):
        self.ready["providers"]["unexpected"] = {"ruleCount": 0}
        with self.assertRaisesRegex(RuntimeError, "counts differ"):
            self.poll([self.ready])

    def test_connection_refused_during_startup_retries(self):
        self.assertEqual(self.poll([URLError("connection refused"), TimeoutError(), self.ready]), self.expected)

    def test_process_exit_stops_polling(self):
        with self.assertRaisesRegex(RuntimeError, "process_exit=1"):
            self.poll([self.ready], SimpleNamespace(poll=lambda: 1))

    def test_malformed_response_is_not_silently_accepted(self):
        with self.assertRaises(KeyError):
            self.poll([{}])
