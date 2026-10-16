"""
timer_view.py - Anti-Cheat Pomodoro Focus Timer Engine.

Features:
- Dual Anti-Cheat Modes:
  1. Honest Tracking Mode (Default): Timer continues ticking when switching tabs/windows,
     accurately logging in-window active focus seconds vs off-window distracted seconds,
     recording tab switches, and calculating Focus Integrity %.
  2. Strict Guardian Mode: Automatically sounds warning and pauses if you leave the window.
- Real-time Focus Integrity Gauge.
- Vector Canvas Circular Progress Ring with live status colors.
- Task selection binding (increments task completed cycles upon session finish).
- Awards Star Charms (✨) based on integrity rate.
"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Callable, Optional

from fp_models import AppState, FocusSession
from fp_utils import calculate_focus_integrity, format_seconds_to_min_sec, calculate_charm_reward, find_first
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_TIMER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL


class TimerView(tk.Frame):
    def __init__(self, parent, state: AppState, on_session_complete: Callable[[FocusSession], None]):
        super().__init__(parent, bg='#FFFFFF')
        self.state = state
        self.on_session_complete = on_session_complete

        # Timer States
        self.is_running = False
        self.timer_mode = 'focus'  # 'focus' | 'short_break' | 'long_break'
        self.total_duration_seconds = self.state.settings.pomodoro_minutes * 60
        self.remaining_seconds = self.total_duration_seconds
        self.active_focus_seconds = 0
        self.distracted_seconds = 0
        self.tab_switches = 0
        self.is_window_focused = True
        self.session_start_time: Optional[datetime] = None

        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])

        self._build_ui()
        self._timer_tick_loop()

    def _build_ui(self):
        self.configure(bg=self.theme['bg'])

        # Top Control Bar (Anti-Cheat Mode Selector & Active Task)
        top_bar = tk.Frame(self, bg=self.theme['bg_card'], padx=16, pady=12, highlightthickness=1, highlightbackground=self.theme['border'])
        top_bar.pack(fill=tk.X, padx=20, pady=(16, 8))

        # Mode Switcher (Focus vs Breaks)
        mode_btn_frame = tk.Frame(top_bar, bg=self.theme['bg_card'])
        mode_btn_frame.pack(side=tk.LEFT)

        self.btn_focus_mode = tk.Button(
            mode_btn_frame, text="🍅 Pomodoro (25m)", font=FONT_SMALL,
            bg=self.theme['tab_active_bg'], fg=self.theme['tab_active_fg'],
            relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
            command=lambda: self._switch_timer_mode('focus', self.state.settings.pomodoro_minutes * 60)
        )
        self.btn_focus_mode.pack(side=tk.LEFT, padx=2)

        self.btn_short_break = tk.Button(
            mode_btn_frame, text="☕ Short Break (5m)", font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'], fg=self.theme['text_secondary'],
            relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
            command=lambda: self._switch_timer_mode('short_break', self.state.settings.short_break_minutes * 60)
        )
        self.btn_short_break.pack(side=tk.LEFT, padx=2)

        self.btn_long_break = tk.Button(
            mode_btn_frame, text="🌿 Long Break (15m)", font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'], fg=self.theme['text_secondary'],
            relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
            command=lambda: self._switch_timer_mode('long_break', self.state.settings.long_break_minutes * 60)
        )
        self.btn_long_break.pack(side=tk.LEFT, padx=2)

        # Anti-Cheat Setting Badge / Toggle
        anti_cheat_frame = tk.Frame(top_bar, bg=self.theme['bg_card'])
        anti_cheat_frame.pack(side=tk.RIGHT)

        tk.Label(anti_cheat_frame, text="Anti-Cheat:", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT, padx=(0, 4))

        self.anti_cheat_var = tk.StringVar(value=self.state.settings.anti_cheat_mode)
        mode_cb = ttk.Combobox(
            anti_cheat_frame,
            textvariable=self.anti_cheat_var,
            values=['honest', 'strict'],
            state="readonly",
            width=10,
            font=FONT_SMALL
        )
        mode_cb.pack(side=tk.LEFT)
        mode_cb.bind("<<ComboboxSelected>>", self._on_anti_cheat_change)

        # Main Center Container
        center_frame = tk.Frame(self, bg=self.theme['bg'])
        center_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Task Binding Row
        task_row = tk.Frame(center_frame, bg=self.theme['bg'])
        task_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(task_row, text="Target Task:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(side=tk.LEFT, padx=(0, 8))

        self.task_selector_var = tk.StringVar()
        self.task_selector = ttk.Combobox(task_row, textvariable=self.task_selector_var, state="readonly", font=FONT_BODY, width=38)
        self.task_selector.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._refresh_task_selector_options()

        # Canvas for Circular Progress Ring
        self.canvas_size = 280
        self.canvas = tk.Canvas(
            center_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.theme['bg'],
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Anti-Cheat Live Status Pill
        self.status_pill = tk.Label(
            center_frame,
            text="● Present & Focused",
            font=FONT_BODY_BOLD,
            bg=self.theme['accent_light'],
            fg=self.theme['success'],
            padx=14,
            pady=4
        )
        self.status_pill.pack(pady=4)

        # Live Focus Integrity Meter
        integrity_frame = tk.Frame(center_frame, bg=self.theme['bg_card'], padx=14, pady=8, highlightthickness=1, highlightbackground=self.theme['border'])
        integrity_frame.pack(fill=tk.X, padx=40, pady=8)

        int_row = tk.Frame(integrity_frame, bg=self.theme['bg_card'])
        int_row.pack(fill=tk.X)

        tk.Label(int_row, text="Focus Integrity:", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

        self.lbl_integrity = tk.Label(int_row, text="100%", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['success'])
        self.lbl_integrity.pack(side=tk.RIGHT)

        # Integrity progress bar
        self.progress_canvas = tk.Canvas(integrity_frame, height=8, bg=self.theme['border'], highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X, pady=(6, 4))

        self.lbl_switches = tk.Label(
            integrity_frame,
            text="0 tab/window switches | 0s distracted",
            font=FONT_SMALL,
            bg=self.theme['bg_card'],
            fg=self.theme['text_secondary']
        )
        self.lbl_switches.pack(anchor="w")

        # Control Buttons (Start / Pause / Reset)
        btn_frame = tk.Frame(center_frame, bg=self.theme['bg'])
        btn_frame.pack(pady=12)

        self.btn_toggle = tk.Button(
            btn_frame,
            text="▶ Start Focus Session",
            font=FONT_SUBTITLE,
            bg=self.theme['accent'],
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._toggle_timer
        )
        self.btn_toggle.pack(side=tk.LEFT, padx=6)

        self.btn_reset = tk.Button(
            btn_frame,
            text="↺ Reset",
            font=FONT_SUBTITLE,
            bg=self.theme['bg_card'],
            fg=self.theme['text_secondary'],
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._reset_timer
        )
        self.btn_reset.pack(side=tk.LEFT, padx=6)

        self._draw_timer_ring()

    def update_state(self, state: AppState):
        self.state = state
        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])
        self._refresh_task_selector_options()
        self._draw_timer_ring()

    def set_active_task(self, task_id: str):
        self._refresh_task_selector_options()
        for idx, task in enumerate(self.state.tasks):
            if task.id == task_id:
                self.task_selector.current(idx + 1)
                break

    def _refresh_task_selector_options(self):
        active_tasks = [t for t in self.state.tasks if t.status != 'completed']
        options = ["✨ General Study (No Specific Task)"] + [f"[{t.priority.upper()}] {t.title}" for t in active_tasks]
        self.task_selector['values'] = options
        if not self.task_selector_var.get() or self.task_selector_var.get() not in options:
            self.task_selector.current(0)

    def _on_anti_cheat_change(self, event=None):
        mode = self.anti_cheat_var.get()
        # In functional architecture, this is captured by parent controller
        pass

    def on_window_focus_in(self):
        """Called by root window when CozyStudy regains focus."""
        if not self.is_window_focused:
            self.is_window_focused = True
            if self.is_running and self.timer_mode == 'focus':
                self.status_pill.configure(
                    text="● Present & Focused",
                    bg=self.theme['accent_light'],
                    fg=self.theme['success']
                )

    def on_window_focus_out(self):
        """
        Anti-Cheat detector: Called when CozyStudy loses window focus
        (e.g., user switched to another app, browser tab, or minimized).
        """
        if self.is_window_focused:
            self.is_window_focused = False
            if self.is_running and self.timer_mode == 'focus':
                self.tab_switches += 1
                self.status_pill.configure(
                    text=f"⚠️ Tabbed Away! ({self.distracted_seconds}s off-focus)",
                    bg='#FEE2E2',
                    fg=self.theme['danger']
                )
                self._play_sound_alert()

                # In Strict Guardian Mode, automatically pause
                if self.anti_cheat_var.get() == 'strict':
                    self.is_running = False
                    self.btn_toggle.configure(text="▶ Resume (Paused by Anti-Cheat)", bg=self.theme['warning'])
                    messagebox.showwarning(
                        "Anti-Cheat Alert",
                        "Strict Guardian Mode paused your session because you switched away from your study desk!"
                    )

    def _play_sound_alert(self):
        if not self.state.settings.sound_enabled:
            return
        try:
            # Native macOS pleasant glass sound
            if os.path.exists("/System/Library/Sounds/Tink.aiff"):
                subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.bell()
        except Exception:
            self.bell()

    def _play_completion_sound(self):
        if not self.state.settings.sound_enabled:
            return
        try:
            if os.path.exists("/System/Library/Sounds/Glass.aiff"):
                subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.bell()
        except Exception:
            self.bell()

    def _switch_timer_mode(self, mode: str, duration_seconds: int):
        self.is_running = False
        self.timer_mode = mode
        self.total_duration_seconds = duration_seconds
        self.remaining_seconds = duration_seconds
        self.active_focus_seconds = 0
        self.distracted_seconds = 0
        self.tab_switches = 0
        self.session_start_time = None

        self.btn_focus_mode.configure(bg=self.theme['tab_active_bg'] if mode == 'focus' else self.theme['bg_card_secondary'])
        self.btn_short_break.configure(bg=self.theme['tab_active_bg'] if mode == 'short_break' else self.theme['bg_card_secondary'])
        self.btn_long_break.configure(bg=self.theme['tab_active_bg'] if mode == 'long_break' else self.theme['bg_card_secondary'])

        self.btn_toggle.configure(text="▶ Start Focus Session" if mode == 'focus' else "▶ Start Break", bg=self.theme['accent'])
        self._draw_timer_ring()

    def _toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.btn_toggle.configure(text="▶ Resume Focus", bg=self.theme['accent'])
        else:
            self.is_running = True
            if not self.session_start_time:
                self.session_start_time = datetime.now()
            self.btn_toggle.configure(text="⏸ Pause", bg=self.theme['warning'])

    def _reset_timer(self):
        self.is_running = False
        self.remaining_seconds = self.total_duration_seconds
        self.active_focus_seconds = 0
        self.distracted_seconds = 0
        self.tab_switches = 0
        self.session_start_time = None
        self.btn_toggle.configure(text="▶ Start Focus Session", bg=self.theme['accent'])
        self.status_pill.configure(text="● Ready to Focus", bg=self.theme['accent_light'], fg=self.theme['success'])
        self._draw_timer_ring()

    def _timer_tick_loop(self):
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            if self.timer_mode == 'focus':
                if self.is_window_focused:
                    self.active_focus_seconds += 1
                else:
                    self.distracted_seconds += 1
                    self.status_pill.configure(
                        text=f"⚠️ Tabbed Away! ({self.distracted_seconds}s off-focus)",
                        bg='#FEE2E2',
                        fg=self.theme['danger']
                    )

            if self.remaining_seconds <= 0:
                self._handle_timer_completed()

            self._draw_timer_ring()

        self.after(1000, self._timer_tick_loop)

    def _handle_timer_completed(self):
        self.is_running = False
        self.btn_toggle.configure(text="▶ Start Another Session", bg=self.theme['accent'])
        self._play_completion_sound()

        if self.timer_mode == 'focus':
            total_elapsed = self.active_focus_seconds + self.distracted_seconds
            integrity = calculate_focus_integrity(self.active_focus_seconds, total_elapsed)
            is_strict = self.anti_cheat_var.get() == 'strict'
            earned_charms = calculate_charm_reward(integrity, total_elapsed, is_strict)

            # Find selected task
            selected_task_id = None
            selected_task_title = "General Study"
            selected_subject_id = "cs101"

            sel_text = self.task_selector_var.get()
            active_tasks = [t for t in self.state.tasks if t.status != 'completed']
            for t in active_tasks:
                if t.title in sel_text:
                    selected_task_id = t.id
                    selected_task_title = t.title
                    selected_subject_id = t.subject_id
                    break

            # Create immutable session object
            session = FocusSession(
                id=f"sess_{int(datetime.now().timestamp())}",
                task_id=selected_task_id,
                task_title=selected_task_title,
                subject_id=selected_subject_id,
                start_time=(self.session_start_time or datetime.now()).isoformat(),
                duration_seconds=total_elapsed,
                active_focus_seconds=self.active_focus_seconds,
                distracted_seconds=self.distracted_seconds,
                tab_switches=self.tab_switches,
                integrity_rate=integrity,
                mode=self.anti_cheat_var.get(),
                completed=True,
                charms_earned=earned_charms
            )

            # Notify parent to update pure AppState
            self.on_session_complete(session)

            msg = (
                f"🎉 Study Cycle Finished!\n\n"
                f"• Active Focus Time: {round(self.active_focus_seconds / 60, 1)} mins\n"
                f"• Off-Tab Time: {self.distracted_seconds}s ({self.tab_switches} switches)\n"
                f"• Focus Integrity: {integrity}%\n"
                f"• Reward Earned: +{earned_charms} ✨ Star Charms!"
            )
            messagebox.showinfo("Session Completed ✨", msg)
        else:
            messagebox.showinfo("Break Over ☕", "Break is complete! Ready to begin another focused study session?")

    def _draw_timer_ring(self):
        self.canvas.delete("all")
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2
        radius = self.canvas_size * 0.40
        stroke_w = 12

        # Background track
        self.canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline=self.theme['border'],
            width=stroke_w
        )

        # Progress Arc
        if self.total_duration_seconds > 0:
            fraction = (self.total_duration_seconds - self.remaining_seconds) / self.total_duration_seconds
            extent = -360 * fraction
        else:
            extent = 0

        # Ring color depends on Anti-Cheat status
        if self.timer_mode != 'focus':
            ring_color = self.theme['accent']
        elif not self.is_window_focused and self.is_running:
            ring_color = self.theme['danger']
        else:
            ring_color = self.theme['success']

        if extent != 0:
            self.canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=90,
                extent=extent,
                style=tk.ARC,
                outline=ring_color,
                width=stroke_w
            )

        # Center Time Text (MM:SS)
        time_str = format_seconds_to_min_sec(self.remaining_seconds)
        self.canvas.create_text(cx, cy - 10, text=time_str, font=FONT_TIMER, fill=self.theme['text_primary'])

        # Mode Subtitle Text
        sub_text = "FOCUS TIME" if self.timer_mode == 'focus' else "BREAK TIME"
        self.canvas.create_text(cx, cy + 30, text=sub_text, font=FONT_SMALL, fill=self.theme['text_secondary'])

        # Update Integrity Display
        total_time = self.active_focus_seconds + self.distracted_seconds
        int_val = calculate_focus_integrity(self.active_focus_seconds, total_time)
        int_color = self.theme['success'] if int_val >= 85 else (self.theme['warning'] if int_val >= 70 else self.theme['danger'])
        self.lbl_integrity.configure(text=f"{int_val}%", fg=int_color)

        self.lbl_switches.configure(
            text=f"{self.tab_switches} tab/window switches | {self.distracted_seconds}s off-focus"
        )

        # Progress bar fill
        pw = self.progress_canvas.winfo_width() or 200
        self.progress_canvas.delete("all")
        fill_w = (int_val / 100) * pw
        self.progress_canvas.create_rectangle(0, 0, fill_w, 8, fill=int_color, outline="")
