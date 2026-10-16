"""
fp_core package - Functional Programming Core for CozyStudy
"""
import sys
import os

# Ensure package path is resolved
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fp_core.models import Subject, Task, Charm, FocusSession, Settings, UserStats, AppState
from fp_core.fp_utils import pipe, compose, curry, map_tuple, filter_tuple, reduce_iterable, calculate_focus_integrity
from fp_core import reducers
from fp_core import analytics_fp
