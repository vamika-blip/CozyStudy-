"""
analytics_fp.py - Pure Higher-Order Selectors and Functional Pipelines for Focus Cycles.

Demonstrates functional aggregation pipelines:
- Transforming collections with map, filter, and fold (reduce)
- Function composition pipelines (pipe)
- Pure metric calculation for focus integrity, timelines, and trends
"""

from typing import Tuple, Dict, Any, List
from datetime import datetime, timedelta
from functools import reduce
from collections import defaultdict

from fp_core.models import AppState, FocusSession, Task
from fp_core.fp_utils import pipe, filter_tuple, map_tuple, calculate_focus_integrity


def get_today_sessions(sessions: Tuple[FocusSession, ...], today_str: str = None) -> Tuple[FocusSession, ...]:
    """Pure filter returning sessions started today."""
    ref_date = today_str or datetime.now().strftime('%Y-%m-%d')
    return filter_tuple(lambda s: s.start_time.startswith(ref_date), sessions)


def get_sessions_in_days(sessions: Tuple[FocusSession, ...], days: int = 7) -> Tuple[FocusSession, ...]:
    """Pure filter returning sessions from the past N days."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    return filter_tuple(lambda s: s.start_time >= cutoff, sessions)


def compute_aggregate_integrity(sessions: Tuple[FocusSession, ...]) -> Dict[str, Any]:
    """
    Pure pipeline computing total focus seconds, distracted seconds, and aggregate integrity.
    Uses reduce_iterable (fold) to accumulate time metrics.
    """
    def fold_fn(acc: Dict[str, int], s: FocusSession) -> Dict[str, int]:
        return {
            'active_focus_secs': acc['active_focus_secs'] + s.active_focus_seconds,
            'distracted_secs': acc['distracted_secs'] + s.distracted_seconds,
            'tab_switches': acc['tab_switches'] + s.tab_switches,
            'total_secs': acc['total_secs'] + s.duration_seconds,
            'count': acc['count'] + 1
        }

    initial = {'active_focus_secs': 0, 'distracted_secs': 0, 'tab_switches': 0, 'total_secs': 0, 'count': 0}
    totals = reduce(fold_fn, sessions, initial)

    integrity = calculate_focus_integrity(totals['active_focus_secs'], totals['total_secs'])

    return {
        **totals,
        'overall_integrity': integrity,
        'active_focus_mins': round(totals['active_focus_secs'] / 60, 1),
        'distracted_mins': round(totals['distracted_secs'] / 60, 1)
    }


def compute_daily_timeline(sessions: Tuple[FocusSession, ...], target_date_str: str = None) -> List[Dict[str, Any]]:
    """
    Purely transforms today's sessions into chronological cycle blocks for timeline charting.
    Color codes blocks based on focus integrity:
    - >= 90%: Mint Green (Pure Focus)
    - 75% - 89%: Warm Amber (Mild Distractions)
    - < 75%: Soft Rose (Cheated / Distracted Session)
    """
    ref_date = target_date_str or datetime.now().strftime('%Y-%m-%d')
    day_sessions = filter_tuple(lambda s: s.start_time.startswith(ref_date), sessions)
    # Sort chronologically
    sorted_sessions = sorted(day_sessions, key=lambda s: s.start_time)

    def to_timeline_block(s: FocusSession) -> Dict[str, Any]:
        time_label = s.start_time[11:16] if len(s.start_time) >= 16 else "00:00"
        if s.integrity_rate >= 90:
            color = "#88B04B"  # Mint/green
            status_text = "Flawless Focus"
        elif s.integrity_rate >= 75:
            color = "#F4A261"  # Amber
            status_text = "Mild Distraction"
        else:
            color = "#E76F51"  # Red/Rose
            status_text = "Tab Switching Alert"

        return {
            'id': s.id,
            'title': s.task_title or "General Focus Session",
            'time_label': time_label,
            'duration_mins': round(s.duration_seconds / 60, 1),
            'focus_mins': round(s.active_focus_seconds / 60, 1),
            'distracted_mins': round(s.distracted_seconds / 60, 1),
            'tab_switches': s.tab_switches,
            'integrity': s.integrity_rate,
            'color': color,
            'status_text': status_text
        }

    return [to_timeline_block(s) for s in sorted_sessions]


def compute_7_day_trends(sessions: Tuple[FocusSession, ...]) -> List[Dict[str, Any]]:
    """
    Pure pipeline grouping past 7 days into daily focus vs distracted minutes for bar graphs.
    """
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in reversed(range(7))]

    # Group sessions by date string
    grouped = defaultdict(list)
    for s in sessions:
        date_part = s.start_time[:10]
        grouped[date_part].append(s)

    def day_to_metric(d) -> Dict[str, Any]:
        d_str = d.strftime('%Y-%m-%d')
        day_sess = tuple(grouped.get(d_str, []))
        agg = compute_aggregate_integrity(day_sess)
        return {
            'date_str': d_str,
            'day_label': d.strftime('%a'),  # Mon, Tue, ...
            'focus_mins': agg['active_focus_mins'],
            'distracted_mins': agg['distracted_mins'],
            'tab_switches': agg['tab_switches'],
            'integrity': agg['overall_integrity'],
            'session_count': agg['count']
        }

    return [day_to_metric(d) for d in days]


def compute_task_statistics(tasks: Tuple[Task, ...]) -> Dict[str, Any]:
    """Pure pipeline calculating completed, pending, overdue, and completion rates."""
    total = len(tasks)
    completed = len(filter_tuple(lambda t: t.status == 'completed', tasks))
    overdue = len(filter_tuple(lambda t: t.is_overdue(), tasks))
    due_today = len(filter_tuple(lambda t: t.is_due_today(), tasks))
    high_priority = len(filter_tuple(lambda t: t.priority == 'high' and t.status != 'completed', tasks))

    completion_rate = int(round((completed / total) * 100)) if total > 0 else 0

    return {
        'total': total,
        'completed': completed,
        'overdue': overdue,
        'due_today': due_today,
        'high_priority': high_priority,
        'completion_rate': completion_rate
    }
