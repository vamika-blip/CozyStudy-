"""
fp_reducers.py - Pure State Transitions and Event Reducers for CozyStudy.

Every function in this module is a pure function:
Given an immutable AppState and action parameters, it computes and returns
a brand-new AppState instance using dataclasses.replace and fp_utils.
Zero side effects, zero in-place mutations.
"""

from dataclasses import replace
from typing import Tuple, Optional
from datetime import datetime, timedelta

from fp_models import AppState, Task, FocusSession, Charm, UserStats, Settings
from fp_utils import update_in_tuple, remove_from_tuple, find_first, calculate_charm_reward


def add_task(state: AppState, task: Task) -> AppState:
    """Purely appends a task to state.tasks."""
    new_tasks = (task,) + state.tasks
    return replace(state, tasks=new_tasks)


def update_task(state: AppState, task_id: str, **updates) -> AppState:
    """Purely updates a task by ID."""
    new_tasks = update_in_tuple(
        state.tasks,
        lambda t: t.id == task_id,
        lambda t: replace(t, **updates)
    )
    return replace(state, tasks=new_tasks)


def delete_task(state: AppState, task_id: str) -> AppState:
    """Purely removes a task by ID."""
    new_tasks = remove_from_tuple(state.tasks, lambda t: t.id == task_id)
    new_active_task_id = None if state.active_task_id == task_id else state.active_task_id
    return replace(state, tasks=new_tasks, active_task_id=new_active_task_id)


def complete_task(state: AppState, task_id: str, today_str: Optional[str] = None) -> Tuple[AppState, int]:
    """
    Purely marks a task as completed, calculates on-time coin bonuses,
    and returns (new_state, coins_reward).
    """
    ref_date = today_str or datetime.now().strftime('%Y-%m-%d')
    task = find_first(lambda t: t.id == task_id, state.tasks)
    if not task:
        return state, 0

    bonus = 20
    if task.due_date and task.due_date >= ref_date:
        bonus += 15  # On-time / early bonus!
    if task.priority == 'high':
        bonus += 10

    now_iso = datetime.now().isoformat()
    new_tasks = update_in_tuple(
        state.tasks,
        lambda t: t.id == task_id,
        lambda t: replace(t, status='completed', completed_at=now_iso)
    )

    new_state = replace(
        state,
        tasks=new_tasks,
        coins=state.coins + bonus
    )
    return new_state, bonus


def unlock_charm(state: AppState, charm_id: str) -> Tuple[AppState, bool]:
    """
    Purely attempts to unlock a charm if the user has enough Star Charms.
    Returns (new_state, success_boolean).
    """
    charm = find_first(lambda c: c.id == charm_id, state.charms)
    if not charm or charm.unlocked or state.coins < charm.cost:
        return state, False

    new_coins = state.coins - charm.cost
    new_charms = update_in_tuple(
        state.charms,
        lambda c: c.id == charm_id,
        lambda c: replace(c, unlocked=True, equipped=True)
    )
    return replace(state, coins=new_coins, charms=new_charms), True


def toggle_equip_charm(state: AppState, charm_id: str) -> AppState:
    """Purely toggles whether an unlocked charm is equipped in the room."""
    charm = find_first(lambda c: c.id == charm_id, state.charms)
    if not charm or not charm.unlocked:
        return state

    new_charms = update_in_tuple(
        state.charms,
        lambda c: c.id == charm_id,
        lambda c: replace(c, equipped=not c.equipped)
    )
    return replace(state, charms=new_charms)


def add_session(state: AppState, session: FocusSession) -> AppState:
    """
    Purely records a completed focus session.
    Automatically increments associated task cycles, updates daily streak,
    and credits earned charms.
    """
    new_sessions = (session,) + state.sessions
    new_coins = state.coins + session.charms_earned

    # Pure task cycle increment
    new_tasks = state.tasks
    if session.task_id:
        new_tasks = update_in_tuple(
            state.tasks,
            lambda t: t.id == session.task_id,
            lambda t: replace(
                t,
                completed_cycles=t.completed_cycles + 1,
                status='in_progress' if t.status == 'todo' else t.status
            )
        )

    # Pure streak update
    today_str = datetime.now().strftime('%Y-%m-%d')
    new_stats = _compute_streak(state.stats, today_str)

    return replace(
        state,
        sessions=new_sessions,
        coins=new_coins,
        tasks=new_tasks,
        stats=new_stats
    )


def _compute_streak(stats: UserStats, today_str: str) -> UserStats:
    """Pure helper for calculating streak progression."""
    if stats.last_active_date == today_str:
        return stats

    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    if stats.last_active_date == yesterday_str:
        curr = stats.current_streak + 1
    else:
        curr = 1

    best = max(stats.best_streak, curr)
    return replace(stats, current_streak=curr, best_streak=best, last_active_date=today_str)


def set_active_task(state: AppState, task_id: Optional[str]) -> AppState:
    """Purely sets the task bound to the Pomodoro timer."""
    return replace(state, active_task_id=task_id)


def update_settings(state: AppState, **setting_updates) -> AppState:
    """Purely updates application settings."""
    new_settings = replace(state.settings, **setting_updates)
    return replace(state, settings=new_settings)
