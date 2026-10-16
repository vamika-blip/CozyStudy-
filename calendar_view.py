"""
calendar_view.py - Interactive Monthly Study Calendar & Daily Log Inspector.

Features:
- Monthly calendar grid with previous/next month navigation
- Glowing activity dots for days with focus sessions and task deadlines
- Day Inspector drawer: Click any day to see full list of focus cycles,
  time studied, tab-switch frequency, and completed tasks
"""

import calendar
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, List, Any

from fp_models import AppState, FocusSession, Task
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL


class CalendarView(tk.Frame):
    def __init__(self, parent, state: AppState):
        super().__init__(parent, bg='#FFFFFF')
        self.state = state

        now = datetime.now()
        self.view_year = now.year
        self.view_month = now.month
        self.selected_date_str = now.strftime('%Y-%m-%d')

        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])

        self._build_ui()

    def update_state(self, state: AppState):
        self.state = state
        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])
        self._refresh_calendar()
        self._inspect_day(self.selected_date_str)

    def _build_ui(self):
        self.configure(bg=self.theme['bg'])

        # Header Bar with Month Navigation
        header = tk.Frame(self, bg=self.theme['bg_card'], padx=16, pady=12, highlightthickness=1, highlightbackground=self.theme['border'])
        header.pack(fill=tk.X, padx=20, pady=(16, 8))

        btn_prev = tk.Button(header, text="◀", font=FONT_BODY_BOLD, bg=self.theme['bg_card_secondary'], fg=self.theme['text_primary'], relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self._prev_month)
        btn_prev.pack(side=tk.LEFT)

        self.lbl_month = tk.Label(header, text="", font=FONT_TITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary'])
        self.lbl_month.pack(side=tk.LEFT, padx=16)

        btn_next = tk.Button(header, text="▶", font=FONT_BODY_BOLD, bg=self.theme['bg_card_secondary'], fg=self.theme['text_primary'], relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self._next_month)
        btn_next.pack(side=tk.LEFT)

        # Split Layout: Left = Calendar Grid, Right = Day Inspector
        content_split = tk.Frame(self, bg=self.theme['bg'])
        content_split.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Calendar Frame
        self.cal_card = tk.Frame(content_split, bg=self.theme['bg_card'], padx=16, pady=14, highlightthickness=1, highlightbackground=self.theme['border'])
        self.cal_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Day Inspector Card
        self.inspector_card = tk.Frame(content_split, width=280, bg=self.theme['bg_card'], padx=16, pady=14, highlightthickness=1, highlightbackground=self.theme['border'])
        self.inspector_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.inspector_card.pack_propagate(False)

        self._refresh_calendar()
        self._inspect_day(self.selected_date_str)

    def _prev_month(self):
        if self.view_month == 1:
            self.view_month = 12
            self.view_year -= 1
        else:
            self.view_month -= 1
        self._refresh_calendar()

    def _next_month(self):
        if self.view_month == 12:
            self.view_month = 1
            self.view_year += 1
        else:
            self.view_month += 1
        self._refresh_calendar()

    def _refresh_calendar(self):
        for w in self.cal_card.winfo_children():
            w.destroy()

        month_name = calendar.month_name[self.view_month]
        self.lbl_month.configure(text=f"{month_name} {self.view_year}")

        # Day Headers (Mon, Tue, Wed...)
        headers_frame = tk.Frame(self.cal_card, bg=self.theme['bg_card'])
        headers_frame.pack(fill=tk.X, pady=(0, 6))

        for day_abbr in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            lbl = tk.Label(headers_frame, text=day_abbr, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary'], width=8)
            lbl.pack(side=tk.LEFT, expand=True)

        # Generate month matrix
        cal_matrix = calendar.monthcalendar(self.view_year, self.view_month)
        today_str = datetime.now().strftime('%Y-%m-%d')

        # Collect session and task dates
        session_dates = {s.start_time[:10] for s in self.state.sessions}
        task_due_dates = {t.due_date for t in self.state.tasks if t.due_date and t.status != 'completed'}

        for week in cal_matrix:
            week_row = tk.Frame(self.cal_card, bg=self.theme['bg_card'])
            week_row.pack(fill=tk.X, pady=2)

            for day_num in week:
                if day_num == 0:
                    empty_box = tk.Frame(week_row, bg=self.theme['bg_card'], width=44, height=44)
                    empty_box.pack(side=tk.LEFT, expand=True)
                else:
                    d_str = f"{self.view_year:04d}-{self.view_month:02d}-{day_num:02d}"
                    is_today = (d_str == today_str)
                    is_selected = (d_str == self.selected_date_str)
                    has_session = (d_str in session_dates)
                    has_due = (d_str in task_due_dates)

                    bg_col = self.theme['tab_active_bg'] if is_selected else (self.theme['bg_card_secondary'] if is_today else self.theme['bg_card'])
                    border_col = self.theme['accent'] if (is_selected or is_today) else self.theme['border']

                    cell = tk.Frame(
                        week_row,
                        bg=bg_col,
                        width=46,
                        height=46,
                        highlightthickness=1,
                        highlightbackground=border_col,
                        cursor="hand2"
                    )
                    cell.pack(side=tk.LEFT, expand=True, padx=2, pady=1)
                    cell.pack_propagate(False)

                    cell.bind("<Button-1>", lambda e, s=d_str: self._on_date_click(s))

                    day_lbl = tk.Label(cell, text=str(day_num), font=FONT_BODY_BOLD if is_today else FONT_SMALL, bg=bg_col, fg=self.theme['text_primary'])
                    day_lbl.pack(pady=(2, 0))
                    day_lbl.bind("<Button-1>", lambda e, s=d_str: self._on_date_click(s))

                    # Indicator dots (Green for session, Red for task deadline)
                    dots_frame = tk.Frame(cell, bg=bg_col)
                    dots_frame.pack(side=tk.BOTTOM, pady=2)
                    dots_frame.bind("<Button-1>", lambda e, s=d_str: self._on_date_click(s))

                    if has_session:
                        dot_s = tk.Label(dots_frame, text="●", font=("Helvetica", 6), bg=bg_col, fg=self.theme['success'])
                        dot_s.pack(side=tk.LEFT, padx=1)
                    if has_due:
                        dot_d = tk.Label(dots_frame, text="●", font=("Helvetica", 6), bg=bg_col, fg=self.theme['danger'])
                        dot_d.pack(side=tk.LEFT, padx=1)

    def _on_date_click(self, date_str: str):
        self.selected_date_str = date_str
        self._refresh_calendar()
        self._inspect_day(date_str)

    def _inspect_day(self, date_str: str):
        for w in self.inspector_card.winfo_children():
            w.destroy()

        try:
            d_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_title = d_obj.strftime('%A, %b %d')
        except Exception:
            date_title = date_str

        tk.Label(self.inspector_card, text=f"📅 {date_title}", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w")

        day_sessions = [s for s in self.state.sessions if s.start_time.startswith(date_str)]
        day_tasks_due = [t for t in self.state.tasks if t.due_date == date_str]

        summary_frame = tk.Frame(self.inspector_card, bg=self.theme['bg_card_secondary'], padx=10, pady=8, highlightthickness=1, highlightbackground=self.theme['border'])
        summary_frame.pack(fill=tk.X, pady=8)

        total_focus_secs = sum(s.active_focus_seconds for s in day_sessions)
        total_switches = sum(s.tab_switches for s in day_sessions)
        focus_mins = round(total_focus_secs / 60, 1)

        tk.Label(summary_frame, text=f"Active Focus: {focus_mins} mins", font=FONT_BODY_BOLD, bg=self.theme['bg_card_secondary'], fg=self.theme['success']).pack(anchor="w")
        tk.Label(summary_frame, text=f"Sessions: {len(day_sessions)} | Switches: {total_switches}", font=FONT_SMALL, bg=self.theme['bg_card_secondary'], fg=self.theme['text_secondary']).pack(anchor="w")

        tk.Label(self.inspector_card, text="Study Sessions:", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w", pady=(8, 4))

        if not day_sessions:
            tk.Label(self.inspector_card, text="No sessions recorded.", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(anchor="w")
        else:
            for s in day_sessions:
                s_card = tk.Frame(self.inspector_card, bg=self.theme['bg_card_secondary'], padx=8, pady=6, highlightthickness=1, highlightbackground=self.theme['border'])
                s_card.pack(fill=tk.X, pady=3)

                time_lbl = s.start_time[11:16] if len(s.start_time) >= 16 else "00:00"
                tk.Label(s_card, text=f"⏱️ {time_lbl} - {s.task_title}", font=FONT_SMALL, bg=self.theme['bg_card_secondary'], fg=self.theme['text_primary'], wraplength=240, justify="left").pack(anchor="w")

                sub_txt = f"{round(s.duration_seconds / 60)}m ({s.integrity_rate}% integrity | {s.tab_switches} switches)"
                tk.Label(s_card, text=sub_txt, font=("Helvetica", 8), bg=self.theme['bg_card_secondary'], fg=self.theme['text_secondary']).pack(anchor="w")

        if day_tasks_due:
            tk.Label(self.inspector_card, text="Deadlines on this Day:", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['danger']).pack(anchor="w", pady=(10, 4))
            for t in day_tasks_due:
                tk.Label(self.inspector_card, text=f"• {t.title}", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_primary'], wraplength=240, justify="left").pack(anchor="w")
