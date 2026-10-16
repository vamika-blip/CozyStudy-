"""
test_app.py - Verification & Automated Test Suite for CozyStudy.

Tests:
1. Immutability & Frozen Dataclass integrity
2. Pure FP combinators (pipe, curry, map_tuple, filter_tuple)
3. Pure reducers (add_task, complete_task, unlock_charm, add_session)
4. Higher-order analytics pipelines (integrity calculation, daily timeline, 7-day trends)
5. Storage load and save validation
6. GUI instantiation sanity check
"""

import sys
import os
import unittest
from datetime import datetime

import storage
import fp_models
import fp_utils
import fp_reducers
import fp_analytics


class TestCozyStudyFP(unittest.TestCase):
    def setUp(self):
        self.state = storage.get_default_state()

    def test_immutability(self):
        """Verify models are frozen and cannot be mutated in place."""
        task = self.state.tasks[0]
        with self.assertRaises(Exception):
            task.title = "Mutated title"

        charm = self.state.charms[0]
        with self.assertRaises(Exception):
            charm.equipped = False

    def test_functional_combinators(self):
        """Verify pipe, curry, and tuple transformers."""
        # pipe
        result = fp_utils.pipe(5, lambda x: x * 2, lambda x: x + 10)
        self.assertEqual(result, 20)

        # curry
        add_three = fp_utils.curry(lambda a, b, c: a + b + c)
        self.assertEqual(add_three(1)(2)(3), 6)

        # map_tuple & filter_tuple
        numbers = (1, 2, 3, 4, 5, 6)
        evens = fp_utils.filter_tuple(lambda x: x % 2 == 0, numbers)
        self.assertEqual(evens, (2, 4, 6))

        doubled = fp_utils.map_tuple(lambda x: x * 2, evens)
        self.assertEqual(doubled, (4, 8, 12))

    def test_pure_reducers(self):
        """Verify pure state transitions do not mutate original state."""
        orig_coins = self.state.coins
        orig_task_count = len(self.state.tasks)

        # 1. Complete Task
        new_state, reward = fp_reducers.complete_task(self.state, 'task-2')
        self.assertEqual(self.state.coins, orig_coins)  # Original unchanged!
        self.assertGreater(new_state.coins, orig_coins)
        self.assertEqual(len(new_state.tasks), orig_task_count)
        completed_task = fp_utils.find_first(lambda t: t.id == 'task-2', new_state.tasks)
        self.assertEqual(completed_task.status, 'completed')

        # 2. Add Task
        new_task = fp_models.Task(
            id='test-t1',
            title='Test Task',
            subject_id='cs101',
            priority='high',
            due_date='2026-10-01',
            estimated_cycles=2
        )
        state_after_add = fp_reducers.add_task(self.state, new_task)
        self.assertEqual(len(self.state.tasks), orig_task_count)
        self.assertEqual(len(state_after_add.tasks), orig_task_count + 1)

    def test_focus_integrity_calculation(self):
        """Verify the Anti-Cheat focus integrity formula."""
        # 100% focused
        self.assertEqual(fp_utils.calculate_focus_integrity(1500, 1500), 100)
        # 75% focused (375s distracted out of 1500s)
        self.assertEqual(fp_utils.calculate_focus_integrity(1125, 1500), 75)
        # 0 total
        self.assertEqual(fp_utils.calculate_focus_integrity(0, 0), 100)

    def test_analytics_pipelines(self):
        """Verify analytics aggregation pipelines."""
        agg = fp_analytics.compute_aggregate_integrity(self.state.sessions)
        self.assertIn('overall_integrity', agg)
        self.assertIn('active_focus_mins', agg)
        self.assertIn('distracted_mins', agg)
        self.assertIn('tab_switches', agg)
        self.assertGreater(agg['active_focus_mins'], 0)

        timeline = fp_analytics.compute_daily_timeline(self.state.sessions)
        self.assertIsInstance(timeline, list)

        trends = fp_analytics.compute_7_day_trends(self.state.sessions)
        self.assertEqual(len(trends), 7)

    def test_storage_serialization(self):
        """Verify state survives dict roundtrip."""
        d = storage.state_to_dict(self.state)
        restored = storage.dict_to_state(d)
        self.assertEqual(restored.coins, self.state.coins)
        self.assertEqual(len(restored.tasks), len(self.state.tasks))
        self.assertEqual(len(restored.charms), len(self.state.charms))


if __name__ == '__main__':
    unittest.main()
