#!/usr/bin/env python3
"""
main.py - Entry point for CozyStudy (Python Functional Desktop Edition).

An aesthetic, gamified study sanctuary built in Python Tkinter:
- Interactive Cozy Room Diorama with customizable unlockable charms & pets
- Anti-Cheat Pomodoro Focus Engine tracking in-window active focus vs distracted tab time
- Vector Canvas Focus Cycle Analytics (Donut, Timeline, 7-Day Trend)
- Priority Task Manager with Eisenhower badges and on-time bonuses
- Monthly Study Calendar & Daily Log Inspector
- 100% Functional Programming Core (pure reducers, immutable models, higher-order pipelines)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

# Ensure current workspace root is in python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import storage
from fp_models import AppState, Task, FocusSession
import fp_reducers
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
from room_canvas import RoomCanvas
from timer_view import TimerView
from charts_canvas import ChartsCanvas
from task_view import TaskView
from calendar_view import CalendarView
from wardrobe_dialog import WardrobeDialog


class CozyStudyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Load initial immutable state
        self.state = storage.load_state()

        self.title("CozyStudy ✨ Aesthetic Study Sanctuary")
        self.geometry("980x680")
        self.minsize(850, 580)

        theme_key = self.state.settings.theme
        self.theme = THEMES.get(theme_key, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])

        # Active tab state
        self.active_tab = 'room'

        self._build_shell()
        self._bind_global_events()

    def _build_shell(self):
        # 1. Top Navbar / Header
        self.navbar = tk.Frame(
            self,
            bg=self.theme['bg_card'],
            padx=16,
            pady=8,
            highlightthickness=1,
            highlightbackground=self.theme['border']
        )
        self.navbar.pack(fill=tk.X)

        # Brand / Logo
        brand_frame = tk.Frame(self.navbar, bg=self.theme['bg_card'])
        brand_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            brand_frame,
            text="🌸 CozyStudy",
            font=FONT_TITLE,
            bg=self.theme['bg_card'],
            fg=self.theme['accent_hover']
        ).pack(side=tk.LEFT)

        # Navigation Tabs
        self.tabs_frame = tk.Frame(self.navbar, bg=self.theme['bg_card'])
        self.tabs_frame.pack(side=tk.LEFT)

        self.tab_buttons = {}
        tab_defs = [
            ('room', '🏠 Room'),
            ('timer', '⏱️ Focus Timer'),
            ('analytics', '📊 Analytics'),
            ('tasks', '📝 Tasks'),
            ('calendar', '📅 Calendar'),
            ('settings', '⚙️ Settings')
        ]

        for tab_id, tab_label in tab_defs:
            btn = tk.Button(
                self.tabs_frame,
                text=tab_label,
                font=FONT_BODY_BOLD,
                relief=tk.FLAT,
                padx=10,
                pady=5,
                cursor="hand2",
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.tab_buttons[tab_id] = btn

        # Right status badge & wardrobe shortcut
        right_frame = tk.Frame(self.navbar, bg=self.theme['bg_card'])
        right_frame.pack(side=tk.RIGHT)

        self.coin_pill = tk.Label(
            right_frame,
            text=f"✨ {self.state.coins} Charms",
            font=FONT_BODY_BOLD,
            bg=self.theme['accent_light'],
            fg=self.theme['accent_hover'],
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.coin_pill.pack(side=tk.LEFT, padx=6)
        self.coin_pill.bind("<Button-1>", lambda e: self.open_wardrobe())

        self.btn_wardrobe = tk.Button(
            right_frame,
            text="Wardrobe",
            font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'],
            fg=self.theme['text_primary'],
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.open_wardrobe
        )
        self.btn_wardrobe.pack(side=tk.LEFT)

        # 2. Main Content Area
        self.content_area = tk.Frame(self, bg=self.theme['bg'])
        self.content_area.pack(fill=tk.BOTH, expand=True)

        # Instantiate View Components
        self.views = {
            'room': RoomCanvas(self.content_area, self.state, self.open_wardrobe),
            'timer': TimerView(self.content_area, self.state, self._on_session_complete),
            'analytics': ChartsCanvas(self.content_area, self.state),
            'tasks': TaskView(
                self.content_area,
                self.state,
                on_add_task=self._on_add_task,
                on_complete_task=self._on_complete_task,
                on_delete_task=self._on_delete_task,
                on_focus_task=self._on_focus_task
            ),
            'calendar': CalendarView(self.content_area, self.state),
            'settings': self._build_settings_view(self.content_area)
        }

        self.switch_tab('room')

    def _build_settings_view(self, parent):
        frame = tk.Frame(parent, bg=self.theme['bg'], padx=30, pady=20)

        card = tk.Frame(frame, bg=self.theme['bg_card'], padx=24, pady=20, highlightthickness=1, highlightbackground=self.theme['border'])
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="⚙️ CozyStudy Settings & Preferences", font=FONT_TITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w", pady=(0, 16))

        # Theme Selector
        theme_row = tk.Frame(card, bg=self.theme['bg_card'])
        theme_row.pack(fill=tk.X, pady=8)

        tk.Label(theme_row, text="Aesthetic Theme Palette:", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(value=self.state.settings.theme)
        theme_cb = ttk.Combobox(
            theme_row,
            textvariable=self.theme_var,
            values=['sakura', 'matcha', 'lavender', 'midnight'],
            state="readonly",
            font=FONT_BODY,
            width=14
        )
        theme_cb.pack(side=tk.LEFT, padx=12)
        theme_cb.bind("<<ComboboxSelected>>", self._on_theme_change)

        # Anti-Cheat Mode
        cheat_row = tk.Frame(card, bg=self.theme['bg_card'])
        cheat_row.pack(fill=tk.X, pady=8)

        tk.Label(cheat_row, text="Anti-Cheat Detection Mode:", font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

        self.cheat_var = tk.StringVar(value=self.state.settings.anti_cheat_mode)
        cheat_cb = ttk.Combobox(
            cheat_row,
            textvariable=self.cheat_var,
            values=['honest', 'strict'],
            state="readonly",
            font=FONT_BODY,
            width=14
        )
        cheat_cb.pack(side=tk.LEFT, padx=12)
        cheat_cb.bind("<<ComboboxSelected>>", self._on_cheat_mode_change)

        cheat_hint = tk.Label(
            card,
            text="• Honest Mode: Timer continues ticking while accurately tracking off-tab distraction minutes & tab switches in graphs.\n• Strict Mode: Pauses session and chimes alert when you switch away from the window.",
            font=FONT_SMALL,
            bg=self.theme['bg_card'],
            fg=self.theme['text_secondary'],
            justify="left"
        )
        cheat_hint.pack(anchor="w", pady=(0, 16))

        # Sound Toggle
        sound_row = tk.Frame(card, bg=self.theme['bg_card'])
        sound_row.pack(fill=tk.X, pady=8)

        self.sound_var = tk.BooleanVar(value=self.state.settings.sound_enabled)
        chk_sound = tk.Checkbutton(
            sound_row,
            text="Enable Alert Chimes & Notifications",
            variable=self.sound_var,
            font=FONT_BODY_BOLD,
            bg=self.theme['bg_card'],
            fg=self.theme['text_primary'],
            command=self._on_sound_toggle
        )
        chk_sound.pack(side=tk.LEFT)

        # Backup & Reset Actions
        sep = tk.Frame(card, height=1, bg=self.theme['border'])
        sep.pack(fill=tk.X, pady=16)

        tk.Label(card, text="Data Management & Backup", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w", pady=(0, 8))

        actions_row = tk.Frame(card, bg=self.theme['bg_card'])
        actions_row.pack(fill=tk.X, pady=8)

        tk.Button(
            actions_row,
            text="Export Backup (JSON)",
            font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'],
            fg=self.theme['text_primary'],
            padx=10,
            pady=4,
            command=self._export_backup
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            actions_row,
            text="Reset to Starter Demo Data",
            font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'],
            fg=self.theme['danger'],
            padx=10,
            pady=4,
            command=self._reset_demo
        ).pack(side=tk.LEFT, padx=4)

        return frame

    def _bind_global_events(self):
        # Anti-Cheat window focus tracking
        self.bind("<FocusIn>", self._on_global_focus_in)
        self.bind("<FocusOut>", self._on_global_focus_out)

        # Quick keyboard shortcuts (1-5 to switch tabs)
        self.bind("<KeyPress-1>", lambda e: self.switch_tab('room'))
        self.bind("<KeyPress-2>", lambda e: self.switch_tab('timer'))
        self.bind("<KeyPress-3>", lambda e: self.switch_tab('analytics'))
        self.bind("<KeyPress-4>", lambda e: self.switch_tab('tasks'))
        self.bind("<KeyPress-5>", lambda e: self.switch_tab('calendar'))

    def _on_global_focus_in(self, event):
        if event.widget == self:
            self.views['timer'].on_window_focus_in()

    def _on_global_focus_out(self, event):
        if event.widget == self:
            self.views['timer'].on_window_focus_out()

    def switch_tab(self, tab_id: str):
        self.active_tab = tab_id
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(
                    bg=self.theme['tab_active_bg'],
                    fg=self.theme['tab_active_fg']
                )
            else:
                btn.configure(
                    bg=self.theme['bg_card'],
                    fg=self.theme['text_secondary']
                )

        for tid, view in self.views.items():
            view.pack_forget()

        self.views[tab_id].pack(fill=tk.BOTH, expand=True)

        # Refresh view with latest state
        if hasattr(self.views[tab_id], 'update_state'):
            self.views[tab_id].update_state(self.state)

    def open_wardrobe(self):
        WardrobeDialog(
            self,
            self.state,
            on_unlock=self._on_unlock_charm,
            on_toggle_equip=self._on_toggle_equip_charm
        )

    # --- Pure State Reducer Callbacks ---

    def _on_session_complete(self, session: FocusSession):
        # Pure state transition
        self.state = fp_reducers.add_session(self.state, session)
        storage.save_state(self.state)
        self._sync_state_to_all_views()

    def _on_add_task(self, task_data: dict):
        new_task = Task(**task_data)
        self.state = fp_reducers.add_task(self.state, new_task)
        storage.save_state(self.state)
        self._sync_state_to_all_views()

    def _on_complete_task(self, task_id: str):
        self.state, coins_earned = fp_reducers.complete_task(self.state, task_id)
        storage.save_state(self.state)
        self._sync_state_to_all_views()
        messagebox.showinfo("Task Complete ✨", f"Great job! You earned +{coins_earned} Star Charms!")

    def _on_delete_task(self, task_id: str):
        self.state = fp_reducers.delete_task(self.state, task_id)
        storage.save_state(self.state)
        self._sync_state_to_all_views()

    def _on_focus_task(self, task_id: str):
        self.state = fp_reducers.set_active_task(self.state, task_id)
        self.views['timer'].set_active_task(task_id)
        self.switch_tab('timer')

    def _on_unlock_charm(self, charm_id: str):
        self.state, success = fp_reducers.unlock_charm(self.state, charm_id)
        if success:
            storage.save_state(self.state)
            self._sync_state_to_all_views()
            messagebox.showinfo("Charm Unlocked! ✨", "Your new charm has been unlocked and placed in your room!")

    def _on_toggle_equip_charm(self, charm_id: str):
        self.state = fp_reducers.toggle_equip_charm(self.state, charm_id)
        storage.save_state(self.state)
        self._sync_state_to_all_views()

    def _on_theme_change(self, event=None):
        new_theme = self.theme_var.get()
        self.state = fp_reducers.update_settings(self.state, theme=new_theme)
        storage.save_state(self.state)
        self.theme = THEMES.get(new_theme, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])
        self.navbar.configure(bg=self.theme['bg_card'])
        self._sync_state_to_all_views()

    def _on_cheat_mode_change(self, event=None):
        new_mode = self.cheat_var.get()
        self.state = fp_reducers.update_settings(self.state, anti_cheat_mode=new_mode)
        storage.save_state(self.state)
        self._sync_state_to_all_views()

    def _on_sound_toggle(self):
        enabled = self.sound_var.get()
        self.state = fp_reducers.update_settings(self.state, sound_enabled=enabled)
        storage.save_state(self.state)

    def _export_backup(self):
        fpath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="cozystudy_backup.json"
        )
        if fpath:
            import json
            data = storage.state_to_dict(self.state)
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Backup Exported", f"Successfully exported backup to {fpath}")

    def _reset_demo(self):
        if messagebox.askyesno("Reset Data", "Reset all data to default demo state?"):
            self.state = storage.get_default_state()
            storage.save_state(self.state)
            self._sync_state_to_all_views()
            messagebox.showinfo("Reset Complete", "Reset to starter demo data.")

    def _sync_state_to_all_views(self):
        self.coin_pill.configure(text=f"✨ {self.state.coins} Charms")
        for view in self.views.values():
            if hasattr(view, 'update_state'):
                view.update_state(self.state)


def main():
    app = CozyStudyApp()
    app.mainloop()


if __name__ == '__main__':
    main()
