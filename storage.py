"""
storage.py - Persistence and Data Serialization for CozyStudy.

Translates between JSON file storage and immutable AppState models.
Provides fallback to vibrant default seed data.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

# Ensure current workspace root is in python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fp_models import Subject, Task, Charm, FocusSession, Settings, UserStats, AppState


STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cozystudy_data.json")


def get_default_subjects() -> Tuple[Subject, ...]:
    return (
        Subject(id='cs101', name='Data Structures & Algorithms', code='CS 201', color='#88B04B', icon='💻'),
        Subject(id='math', name='Linear Algebra & Calculus', code='MATH 150', color='#92A8D1', icon='📐'),
        Subject(id='bio', name='Molecular Biology', code='BIO 110', color='#F7CAC9', icon='🧬'),
        Subject(id='lit', name='World Literature & Essay', code='LIT 102', color='#E0BBE4', icon='📖'),
        Subject(id='art', name='Digital Art & Design', code='ART 210', color='#FFD3B6', icon='🎨')
    )


def get_default_charms() -> Tuple[Charm, ...]:
    return (
        Charm(id='charm_matcha', name='Steaming Matcha Latte', category='desk', icon='🍵', cost=0, unlocked=True, equipped=True, description='Warm ceramic mug of freshly whisked matcha'),
        Charm(id='charm_lamp', name='Pastel Desk Lamp', category='desk', icon='💡', cost=0, unlocked=True, equipped=True, description='Soft warm amber glow for late night focus'),
        Charm(id='charm_calico', name='Sleeping Calico Cat (Mochi)', category='pet', icon='🐱', cost=0, unlocked=True, equipped=True, description='Purrs peacefully on the rug when focus is high'),
        Charm(id='charm_succulent', name='Baby Succulent Pot', category='desk', icon='🪴', cost=30, unlocked=True, equipped=True, description='Loves steady daily study consistency'),
        Charm(id='charm_fairylights', name='Twinkling Fairy Lights', category='wall', icon='✨', cost=50, unlocked=True, equipped=True, description='Cozy warm sparkles hanging across the window'),
        Charm(id='charm_radio', name='Vintage Lo-Fi Cassette Radio', category='desk', icon='📻', cost=75, unlocked=False, equipped=False, description='Plays nostalgic lo-fi study beats'),
        Charm(id='charm_bunny', name='Fluffy Mochi Bunny', category='pet', icon='🐰', cost=90, unlocked=False, equipped=False, description='Hops near the bookshelf during break times'),
        Charm(id='charm_crystal', name='Amethyst Focus Crystal', category='desk', icon='🔮', cost=120, unlocked=False, equipped=False, description='Radiates serene energy and dispels distractions'),
        Charm(id='charm_polaroids', name='Polaroid Memory Board', category='wall', icon='📸', cost=80, unlocked=False, equipped=False, description='Memories of completed milestones and cafe dates'),
        Charm(id='charm_monstera', name='Giant Monstera Deliciosa', category='floor', icon='🌿', cost=100, unlocked=False, equipped=False, description='Lush tropical plant standing proudly in the corner'),
        Charm(id='charm_beanbag', name='Velvet Cloud Beanbag', category='floor', icon='🛋️', cost=110, unlocked=False, equipped=False, description='The softest reading spot in the whole room'),
        Charm(id='charm_globe', name='Floating Moon Globe', category='desk', icon='🌙', cost=160, unlocked=False, equipped=False, description='Glows in synchrony with lunar focus cycles')
    )


def get_default_tasks() -> Tuple[Task, ...]:
    now = datetime.now()
    return (
        Task(
            id='task-1',
            title='Implement Red-Black Tree Balanced Insert',
            subject_id='cs101',
            priority='high',
            due_date=(now + timedelta(days=2)).strftime('%Y-%m-%d'),
            estimated_cycles=3,
            completed_cycles=1,
            status='in_progress',
            notes='Implement left-rotate, right-rotate, and re-coloring fixes.'
        ),
        Task(
            id='task-2',
            title='Linear Algebra Problem Set 4 (Eigenvalues)',
            subject_id='math',
            priority='high',
            due_date=(now + timedelta(days=1)).strftime('%Y-%m-%d'),
            estimated_cycles=2,
            completed_cycles=0,
            status='todo',
            notes='Problems 5.1 through 5.3 on characteristic polynomials.'
        ),
        Task(
            id='task-3',
            title='Literature Comparative Synthesis Essay',
            subject_id='lit',
            priority='medium',
            due_date=(now + timedelta(days=4)).strftime('%Y-%m-%d'),
            estimated_cycles=4,
            completed_cycles=2,
            status='in_progress',
            notes='Draft 1,500 words comparing Woolf to Joyce on stream of consciousness.'
        ),
        Task(
            id='task-4',
            title='Review Cellular Respiration Diagram & Enzymes',
            subject_id='bio',
            priority='low',
            due_date=(now + timedelta(days=6)).strftime('%Y-%m-%d'),
            estimated_cycles=1,
            completed_cycles=1,
            status='completed',
            completed_at=(now - timedelta(hours=3)).isoformat(),
            notes='Memorize ATP synthase mechanism and Krebs cycle intermediates.'
        ),
        Task(
            id='task-5',
            title='Design Pastel Palette & Room Moodboard',
            subject_id='art',
            priority='medium',
            due_date=(now + timedelta(days=3)).strftime('%Y-%m-%d'),
            estimated_cycles=2,
            completed_cycles=0,
            status='todo',
            notes='Pick 6 matching pastel swatches for the cozy room.'
        )
    )


def get_default_sessions() -> Tuple[FocusSession, ...]:
    now = datetime.now()
    return (
        FocusSession(
            id='sess-1',
            task_id='task-1',
            task_title='Implement Red-Black Tree Balanced Insert',
            subject_id='cs101',
            start_time=(now - timedelta(hours=2)).isoformat(),
            duration_seconds=1500,
            active_focus_seconds=1420,
            distracted_seconds=80,
            tab_switches=2,
            integrity_rate=95,
            mode='honest',
            completed=True,
            charms_earned=15
        ),
        FocusSession(
            id='sess-2',
            task_id='task-3',
            task_title='Literature Comparative Synthesis Essay',
            subject_id='lit',
            start_time=(now - timedelta(hours=4)).isoformat(),
            duration_seconds=1500,
            active_focus_seconds=1310,
            distracted_seconds=190,
            tab_switches=4,
            integrity_rate=87,
            mode='honest',
            completed=True,
            charms_earned=12
        ),
        FocusSession(
            id='sess-3',
            task_id='task-4',
            task_title='Review Cellular Respiration Diagram & Enzymes',
            subject_id='bio',
            start_time=(now - timedelta(days=1, hours=3)).isoformat(),
            duration_seconds=1500,
            active_focus_seconds=1480,
            distracted_seconds=20,
            tab_switches=1,
            integrity_rate=99,
            mode='honest',
            completed=True,
            charms_earned=20
        ),
        FocusSession(
            id='sess-4',
            task_id='task-1',
            task_title='Implement Red-Black Tree Balanced Insert',
            subject_id='cs101',
            start_time=(now - timedelta(days=1, hours=6)).isoformat(),
            duration_seconds=1500,
            active_focus_seconds=1120,
            distracted_seconds=380,
            tab_switches=6,
            integrity_rate=75,
            mode='honest',
            completed=True,
            charms_earned=8
        ),
        FocusSession(
            id='sess-5',
            task_id='task-3',
            task_title='Literature Comparative Synthesis Essay',
            subject_id='lit',
            start_time=(now - timedelta(days=2, hours=4)).isoformat(),
            duration_seconds=1800,
            active_focus_seconds=1720,
            distracted_seconds=80,
            tab_switches=2,
            integrity_rate=96,
            mode='honest',
            completed=True,
            charms_earned=18
        ),
        FocusSession(
            id='sess-6',
            task_id=None,
            task_title='Morning Mindful Study & Reading',
            subject_id='cs101',
            start_time=(now - timedelta(days=3, hours=2)).isoformat(),
            duration_seconds=1500,
            active_focus_seconds=1450,
            distracted_seconds=50,
            tab_switches=1,
            integrity_rate=97,
            mode='honest',
            completed=True,
            charms_earned=15
        )
    )


def get_default_state() -> AppState:
    return AppState(
        coins=85,
        subjects=get_default_subjects(),
        charms=get_default_charms(),
        tasks=get_default_tasks(),
        sessions=get_default_sessions(),
        active_task_id=None,
        settings=Settings(),
        stats=UserStats(current_streak=3, best_streak=5)
    )


def state_to_dict(state: AppState) -> Dict[str, Any]:
    """Pure serialization of AppState into JSON-compatible dict."""
    return {
        'coins': state.coins,
        'active_task_id': state.active_task_id,
        'subjects': [s.__dict__ for s in state.subjects],
        'charms': [c.__dict__ for c in state.charms],
        'tasks': [t.__dict__ for t in state.tasks],
        'sessions': [sess.__dict__ for sess in state.sessions],
        'settings': state.settings.__dict__,
        'stats': state.stats.__dict__
    }


def dict_to_state(data: Dict[str, Any]) -> AppState:
    """Pure deserialization with defensive fallback."""
    defaults = get_default_state()
    try:
        coins = data.get('coins', defaults.coins)
        active_task_id = data.get('active_task_id', None)

        subjects = tuple(Subject(**s) for s in data.get('subjects', [])) or defaults.subjects
        charms = tuple(Charm(**c) for c in data.get('charms', [])) or defaults.charms
        tasks = tuple(Task(**t) for t in data.get('tasks', []))
        sessions = tuple(FocusSession(**sess) for sess in data.get('sessions', []))

        settings_dict = data.get('settings', {})
        settings = Settings(**{k: v for k, v in settings_dict.items() if hasattr(Settings, k)})

        stats_dict = data.get('stats', {})
        stats = UserStats(**{k: v for k, v in stats_dict.items() if hasattr(UserStats, k)})

        return AppState(
            coins=coins,
            subjects=subjects,
            charms=charms,
            tasks=tasks,
            sessions=sessions,
            active_task_id=active_task_id,
            settings=settings,
            stats=stats
        )
    except Exception as e:
        print(f"Error restoring state from dict: {e}, falling back to defaults")
        return defaults


def load_state() -> AppState:
    """Loads state from JSON storage file or initializes default seed data."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return dict_to_state(data)
        except Exception as e:
            print(f"Failed to read {STORAGE_FILE}: {e}")
    default_st = get_default_state()
    save_state(default_st)
    return default_st


def save_state(state: AppState) -> bool:
    """Saves AppState to JSON storage file."""
    try:
        data = state_to_dict(state)
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save state to {STORAGE_FILE}: {e}")
        return False
