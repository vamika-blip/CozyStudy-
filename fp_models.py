"""
fp_models.py - Immutable Domain Entities for CozyStudy.

All models are defined as frozen dataclasses to guarantee strict immutability,
a core principle of functional programming. Any state transition returns a
new instance with updated values rather than mutating existing state.
"""

from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True)
class Subject:
    id: str
    name: str
    code: str
    color: str
    icon: str


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    subject_id: str
    priority: str  # 'high' | 'medium' | 'low'
    due_date: str  # YYYY-MM-DD
    estimated_cycles: int
    completed_cycles: int = 0
    status: str = 'todo'  # 'todo' | 'in_progress' | 'completed'
    notes: str = ''
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def is_overdue(self, reference_date_str: Optional[str] = None) -> bool:
        ref = reference_date_str or datetime.now().strftime('%Y-%m-%d')
        return self.status != 'completed' and bool(self.due_date) and self.due_date < ref

    def is_due_today(self, reference_date_str: Optional[str] = None) -> bool:
        ref = reference_date_str or datetime.now().strftime('%Y-%m-%d')
        return self.status != 'completed' and self.due_date == ref


@dataclass(frozen=True)
class Charm:
    id: str
    name: str
    category: str  # 'desk' | 'wall' | 'pet' | 'floor'
    icon: str
    cost: int
    unlocked: bool = False
    equipped: bool = False
    description: str = ''


@dataclass(frozen=True)
class FocusSession:
    id: str
    task_id: Optional[str]
    task_title: str
    subject_id: str
    start_time: str
    duration_seconds: int
    active_focus_seconds: int
    distracted_seconds: int
    tab_switches: int
    integrity_rate: int  # 0 to 100 percentage
    mode: str = 'honest'  # 'honest' | 'strict'
    completed: bool = True
    charms_earned: int = 0


@dataclass(frozen=True)
class Settings:
    theme: str = 'sakura'  # 'sakura' | 'matcha' | 'lavender' | 'midnight'
    anti_cheat_mode: str = 'honest'  # 'honest' | 'strict'
    pomodoro_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    sound_enabled: bool = True
    grace_period_seconds: int = 5


@dataclass(frozen=True)
class UserStats:
    current_streak: int = 1
    best_streak: int = 1
    last_active_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))


@dataclass(frozen=True)
class AppState:
    coins: int
    subjects: Tuple[Subject, ...]
    charms: Tuple[Charm, ...]
    tasks: Tuple[Task, ...]
    sessions: Tuple[FocusSession, ...]
    active_task_id: Optional[str]
    settings: Settings
    stats: UserStats
