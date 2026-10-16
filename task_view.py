"""
task_view.py - Priority Task & Assignment Manager for CozyStudy.

Features:
- Priority matrix & filtering (High, Medium, Low)
- Subject / course categorization with pastel badges
- Deadline tracker with automatic "Overdue", "Due Today", "In N Days" highlights
- Quick "Focus Now" action binding task directly to the Pomodoro Anti-Cheat timer
- Task completion with on-time Star Charm bonuses
- Add/Edit/Delete task dialogs
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Callable, Optional

from fp_models import AppState, Task, Subject
from fp_utils import find_first
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL


class TaskView(tk.Frame):
    def __init__(
        self,
        parent,
        state: AppState,
        on_add_task: Callable[[dict], None],
        on_complete_task: Callable[[str], None],
        on_delete_task: Callable[[str], None],
        on_focus_task: Callable[[str], None]
    ):
        super().__init__(parent, bg='#FFFFFF')
        self.state = state
        self.on_add_task = on_add_task
        self.on_complete_task = on_complete_task
        self.on_delete_task = on_delete_task
        self.on_focus_task = on_focus_task

        self.current_priority_filter = 'all'
        self.current_status_filter = 'pending'

        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])

        self._build_ui()

    def update_state(self, state: AppState):
        self.state = state
        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])
        self._refresh_tasks_list()

    def _build_ui(self):
        self.configure(bg=self.theme['bg'])

        # Top Action Bar
        header = tk.Frame(self, bg=self.theme['bg_card'], padx=16, pady=12, highlightthickness=1, highlightbackground=self.theme['border'])
        header.pack(fill=tk.X, padx=20, pady=(16, 8))

        title_lbl = tk.Label(header, text="📝 Priority Study Tasks & Deadlines", font=FONT_TITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary'])
        title_lbl.pack(side=tk.LEFT)

        btn_add = tk.Button(
            header,
            text="+ Add New Task",
            font=FONT_SMALL,
            bg=self.theme['accent'],
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._open_add_task_dialog
        )
        btn_add.pack(side=tk.RIGHT)

        # Filters Row
        filter_bar = tk.Frame(self, bg=self.theme['bg'], padx=4, pady=4)
        filter_bar.pack(fill=tk.X, padx=20, pady=4)

        tk.Label(filter_bar, text="Filter:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_filter_all = tk.Button(filter_bar, text="All Active", font=FONT_SMALL, bg=self.theme['tab_active_bg'], fg=self.theme['tab_active_fg'], relief=tk.FLAT, padx=8, pady=2, command=lambda: self._set_filter('pending', 'all'))
        self.btn_filter_all.pack(side=tk.LEFT, padx=2)

        self.btn_filter_high = tk.Button(filter_bar, text="🔴 High Priority", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['danger'], relief=tk.FLAT, padx=8, pady=2, command=lambda: self._set_filter('pending', 'high'))
        self.btn_filter_high.pack(side=tk.LEFT, padx=2)

        self.btn_filter_medium = tk.Button(filter_bar, text="🟡 Medium", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['warning'], relief=tk.FLAT, padx=8, pady=2, command=lambda: self._set_filter('pending', 'medium'))
        self.btn_filter_medium.pack(side=tk.LEFT, padx=2)

        self.btn_filter_low = tk.Button(filter_bar, text="🟢 Low", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['success'], relief=tk.FLAT, padx=8, pady=2, command=lambda: self._set_filter('pending', 'low'))
        self.btn_filter_low.pack(side=tk.LEFT, padx=2)

        self.btn_filter_completed = tk.Button(filter_bar, text="✓ Completed", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary'], relief=tk.FLAT, padx=8, pady=2, command=lambda: self._set_filter('completed', 'all'))
        self.btn_filter_completed.pack(side=tk.LEFT, padx=8)

        # Scrollable Task List
        self.canvas = tk.Canvas(self, bg=self.theme['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.task_list_frame = tk.Frame(self.canvas, bg=self.theme['bg'])

        self.task_list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.task_list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=8)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=8)

        self._refresh_tasks_list()

    def _set_filter(self, status: str, priority: str):
        self.current_status_filter = status
        self.current_priority_filter = priority

        self.btn_filter_all.configure(bg=self.theme['tab_active_bg'] if status == 'pending' and priority == 'all' else self.theme['bg_card'])
        self.btn_filter_high.configure(bg=self.theme['tab_active_bg'] if priority == 'high' else self.theme['bg_card'])
        self.btn_filter_medium.configure(bg=self.theme['tab_active_bg'] if priority == 'medium' else self.theme['bg_card'])
        self.btn_filter_low.configure(bg=self.theme['tab_active_bg'] if priority == 'low' else self.theme['bg_card'])
        self.btn_filter_completed.configure(bg=self.theme['tab_active_bg'] if status == 'completed' else self.theme['bg_card'])

        self._refresh_tasks_list()

    def _refresh_tasks_list(self):
        for w in self.task_list_frame.winfo_children():
            w.destroy()

        filtered_tasks = []
        for t in self.state.tasks:
            # Status check
            if self.current_status_filter == 'pending' and t.status == 'completed':
                continue
            if self.current_status_filter == 'completed' and t.status != 'completed':
                continue
            # Priority check
            if self.current_priority_filter != 'all' and t.priority != self.current_priority_filter:
                continue
            filtered_tasks.append(t)

        if not filtered_tasks:
            empty_msg = "🎉 All caught up! No tasks found for this filter." if self.current_status_filter == 'pending' else "No completed tasks yet."
            tk.Label(self.task_list_frame, text=empty_msg, font=FONT_BODY, bg=self.theme['bg'], fg=self.theme['text_secondary'], pady=30).pack()
            return

        for task in filtered_tasks:
            self._render_task_card(task)

    def _render_task_card(self, task: Task):
        card = tk.Frame(
            self.task_list_frame,
            bg=self.theme['bg_card'],
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=self.theme['border']
        )
        card.pack(fill=tk.X, padx=4, pady=6)

        # Subject & Priority badge row
        top_row = tk.Frame(card, bg=self.theme['bg_card'])
        top_row.pack(fill=tk.X)

        subject = find_first(lambda s: s.id == task.subject_id, self.state.subjects)
        sub_name = subject.name if subject else "General"
        sub_icon = subject.icon if subject else "📚"

        tk.Label(
            top_row,
            text=f"{sub_icon} {sub_name}",
            font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'],
            fg=self.theme['text_secondary'],
            padx=6,
            pady=2
        ).pack(side=tk.LEFT)

        # Priority Badge
        prio_colors = {
            'high': (self.theme['danger'], '#FEE2E2'),
            'medium': (self.theme['warning'], '#FEF3C7'),
            'low': (self.theme['success'], '#DCFCE7')
        }
        p_fg, p_bg = prio_colors.get(task.priority, (self.theme['accent'], self.theme['accent_light']))

        prio_lbl = tk.Label(
            top_row,
            text=f"{task.priority.upper()} PRIORITY",
            font=("Helvetica", 8, "bold"),
            bg=p_bg,
            fg=p_fg,
            padx=6,
            pady=1
        )
        prio_lbl.pack(side=tk.LEFT, padx=8)

        # Deadline indicator
        if task.due_date:
            today_str = datetime.now().strftime('%Y-%m-%d')
            if task.status == 'completed':
                due_text = f"Completed"
                due_col = self.theme['text_secondary']
            elif task.due_date < today_str:
                due_text = f"⚠️ Overdue ({task.due_date})"
                due_col = self.theme['danger']
            elif task.due_date == today_str:
                due_text = "⚡ Due Today!"
                due_col = self.theme['warning']
            else:
                due_text = f"📅 Due {task.due_date}"
                due_col = self.theme['text_secondary']

            tk.Label(top_row, text=due_text, font=FONT_SMALL, bg=self.theme['bg_card'], fg=due_col).pack(side=tk.RIGHT)

        # Title
        title_style = (FONT_BODY_BOLD[0], FONT_BODY_BOLD[1], "overstrike") if task.status == 'completed' else FONT_BODY_BOLD
        title_fg = self.theme['text_secondary'] if task.status == 'completed' else self.theme['text_primary']
        tk.Label(card, text=task.title, font=title_style, bg=self.theme['bg_card'], fg=title_fg, wraplength=450, justify="left").pack(anchor="w", pady=(6, 2))

        # Notes if any
        if task.notes:
            tk.Label(card, text=task.notes, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary'], wraplength=450, justify="left").pack(anchor="w")

        # Bottom row: Completed cycles & Actions
        bot_row = tk.Frame(card, bg=self.theme['bg_card'])
        bot_row.pack(fill=tk.X, pady=(8, 0))

        # Cycles count (e.g. 1 / 3 🍅)
        cycle_str = f"🍅 {task.completed_cycles} / {task.estimated_cycles} cycles completed"
        tk.Label(bot_row, text=cycle_str, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT)

        # Action Buttons
        actions_frame = tk.Frame(bot_row, bg=self.theme['bg_card'])
        actions_frame.pack(side=tk.RIGHT)

        if task.status != 'completed':
            btn_focus = tk.Button(
                actions_frame,
                text="⏱️ Focus Now",
                font=FONT_SMALL,
                bg=self.theme['accent_light'],
                fg=self.theme['accent_hover'],
                relief=tk.FLAT,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda tid=task.id: self.on_focus_task(tid)
            )
            btn_focus.pack(side=tk.LEFT, padx=4)

            btn_complete = tk.Button(
                actions_frame,
                text="✓ Done (+20 ✨)",
                font=FONT_SMALL,
                bg=self.theme['success'],
                fg='#FFFFFF',
                relief=tk.FLAT,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda tid=task.id: self.on_complete_task(tid)
            )
            btn_complete.pack(side=tk.LEFT, padx=4)

        btn_del = tk.Button(
            actions_frame,
            text="✕",
            font=FONT_SMALL,
            bg=self.theme['bg_card_secondary'],
            fg=self.theme['text_secondary'],
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            command=lambda tid=task.id: self._confirm_delete(tid)
        )
        btn_del.pack(side=tk.LEFT, padx=4)

    def _confirm_delete(self, task_id: str):
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?"):
            self.on_delete_task(task_id)

    def _open_add_task_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Study Task")
        dialog.geometry("450x420")
        dialog.configure(bg=self.theme['bg'])
        dialog.transient(self)
        dialog.grab_set()

        content = tk.Frame(dialog, bg=self.theme['bg'], padx=20, pady=16)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text="Task Title:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        ent_title = tk.Entry(content, font=FONT_BODY)
        ent_title.pack(fill=tk.X, pady=(4, 12))
        ent_title.focus_set()

        tk.Label(content, text="Subject / Course:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        sub_cb = ttk.Combobox(content, state="readonly", values=[s.name for s in self.state.subjects], font=FONT_BODY)
        sub_cb.current(0)
        sub_cb.pack(fill=tk.X, pady=(4, 12))

        prio_row = tk.Frame(content, bg=self.theme['bg'])
        prio_row.pack(fill=tk.X, pady=(0, 12))

        # Priority & Due Date side by side
        p_col = tk.Frame(prio_row, bg=self.theme['bg'])
        p_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(p_col, text="Priority:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        prio_cb = ttk.Combobox(p_col, state="readonly", values=['high', 'medium', 'low'], font=FONT_BODY)
        prio_cb.current(1)
        prio_cb.pack(fill=tk.X, pady=(4, 0))

        d_col = tk.Frame(prio_row, bg=self.theme['bg'])
        d_col.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(d_col, text="Due Date (YYYY-MM-DD):", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        ent_due = tk.Entry(d_col, font=FONT_BODY)
        ent_due.insert(0, (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'))
        ent_due.pack(fill=tk.X, pady=(4, 0))

        tk.Label(content, text="Estimated Pomodoros (25m cycles):", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        ent_cycles = tk.Spinbox(content, from_=1, to=10, font=FONT_BODY)
        ent_cycles.pack(anchor="w", pady=(4, 12))

        tk.Label(content, text="Notes / Key Steps:", font=FONT_BODY_BOLD, bg=self.theme['bg'], fg=self.theme['text_primary']).pack(anchor="w")
        ent_notes = tk.Entry(content, font=FONT_BODY)
        ent_notes.pack(fill=tk.X, pady=(4, 16))

        def save():
            title = ent_title.get().strip()
            if not title:
                messagebox.showerror("Missing Title", "Please enter a task title.")
                return

            sel_idx = sub_cb.current()
            subject_id = self.state.subjects[sel_idx].id if sel_idx >= 0 else 'cs101'

            task_data = {
                'id': f"task_{int(datetime.now().timestamp())}",
                'title': title,
                'subject_id': subject_id,
                'priority': prio_cb.get(),
                'due_date': ent_due.get().strip(),
                'estimated_cycles': int(ent_cycles.get() or 1),
                'completed_cycles': 0,
                'status': 'todo',
                'notes': ent_notes.get().strip()
            }
            self.on_add_task(task_data)
            dialog.destroy()

        btn_save = tk.Button(
            content,
            text="Save Task ✨",
            font=FONT_SUBTITLE,
            bg=self.theme['accent'],
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=save
        )
        btn_save.pack(anchor="e")
