"""
charts_canvas.py - Vector Canvas Graphical Representation of Focus Cycles & Anti-Cheat Analytics.

Renders:
1. Focus Integrity Donut / Ring Chart (Pure Focus vs Off-Screen Distraction Time)
2. Daily Focus Cycles Timeline (Visual chronological study blocks with integrity ratings)
3. 7-Day Trend Bar Chart (Daily focus minutes vs off-tab distraction minutes)
4. Key Productivity Summary Cards
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List

from fp_models import AppState
import fp_analytics
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL


class ChartsCanvas(tk.Frame):
    def __init__(self, parent, state: AppState):
        super().__init__(parent, bg='#FFFFFF')
        self.state = state

        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])

        self._build_ui()

    def update_state(self, state: AppState):
        self.state = state
        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])
        self.configure(bg=self.theme['bg'])
        self.redraw_all()

    def _build_ui(self):
        self.configure(bg=self.theme['bg'])

        # Header
        header = tk.Frame(self, bg=self.theme['bg_card'], padx=16, pady=12, highlightthickness=1, highlightbackground=self.theme['border'])
        header.pack(fill=tk.X, padx=20, pady=(16, 8))

        tk.Label(header, text="📊 Focus Cycle Analytics & Anti-Cheat Reports", font=FONT_TITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

        # Scrollable Canvas container for all graphs
        self.main_canvas = tk.Canvas(self, bg=self.theme['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.scrollable_content = tk.Frame(self.main_canvas, bg=self.theme['bg'])

        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=8)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=8)

        # 1. Summary KPI Cards Row
        self.kpi_frame = tk.Frame(self.scrollable_content, bg=self.theme['bg'])
        self.kpi_frame.pack(fill=tk.X, pady=(0, 14))

        # 2. Split Charts Row: Left = Integrity Donut, Right = 7-Day Trend Bar Chart
        self.charts_row = tk.Frame(self.scrollable_content, bg=self.theme['bg'])
        self.charts_row.pack(fill=tk.X, pady=8)

        # Donut card
        self.donut_card = tk.Frame(self.charts_row, bg=self.theme['bg_card'], padx=16, pady=14, highlightthickness=1, highlightbackground=self.theme['border'])
        self.donut_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        tk.Label(self.donut_card, text="Focus vs Distraction Split", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w")

        self.donut_canvas = tk.Canvas(self.donut_card, width=280, height=210, bg=self.theme['bg_card'], highlightthickness=0)
        self.donut_canvas.pack(pady=6)

        # 7-Day Trend Bar card
        self.trend_card = tk.Frame(self.charts_row, bg=self.theme['bg_card'], padx=16, pady=14, highlightthickness=1, highlightbackground=self.theme['border'])
        self.trend_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        tk.Label(self.trend_card, text="7-Day Focus & Tab-Switch Trends", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(anchor="w")

        self.trend_canvas = tk.Canvas(self.trend_card, width=340, height=210, bg=self.theme['bg_card'], highlightthickness=0)
        self.trend_canvas.pack(pady=6)

        # 3. Focus Cycles Timeline Container
        self.timeline_card = tk.Frame(self.scrollable_content, bg=self.theme['bg_card'], padx=16, pady=14, highlightthickness=1, highlightbackground=self.theme['border'])
        self.timeline_card.pack(fill=tk.X, pady=8)

        tl_hdr = tk.Frame(self.timeline_card, bg=self.theme['bg_card'])
        tl_hdr.pack(fill=tk.X, pady=(0, 8))

        tk.Label(tl_hdr, text="Today's Focus Cycles Chronometer", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        tk.Label(tl_hdr, text="Color-coded by Anti-Cheat Integrity", font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.RIGHT)

        self.timeline_list_frame = tk.Frame(self.timeline_card, bg=self.theme['bg_card'])
        self.timeline_list_frame.pack(fill=tk.X)

        self.redraw_all()

    def redraw_all(self):
        self._render_kpis()
        self._render_donut_chart()
        self._render_trend_bar_chart()
        self._render_timeline()

    def _render_kpis(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        agg = fp_analytics.compute_aggregate_integrity(self.state.sessions)
        total_hours = round(agg['active_focus_mins'] / 60, 1)

        kpis = [
            ("Pure Focus Time", f"{total_hours} hrs", "✨ Undistracted", self.theme['success']),
            ("Focus Integrity", f"{agg['overall_integrity']}%", f"{agg['tab_switches']} tab switches", self.theme['accent']),
            ("Completed Cycles", f"{agg['count']}", "🍅 Pomodoros", self.theme['warning']),
            ("Study Streak", f"{self.state.stats.current_streak} days", f"Best: {self.state.stats.best_streak}", self.theme['charm_coin'])
        ]

        for title, val, sub, color in kpis:
            card = tk.Frame(self.kpi_frame, bg=self.theme['bg_card'], padx=14, pady=10, highlightthickness=1, highlightbackground=self.theme['border'])
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            tk.Label(card, text=title, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(anchor="w")
            tk.Label(card, text=val, font=FONT_TITLE, bg=self.theme['bg_card'], fg=color).pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=sub, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(anchor="w")

    def _render_donut_chart(self):
        self.donut_canvas.delete("all")
        w = 280
        h = 210
        cx = 100
        cy = 105
        radius = 70
        stroke_w = 26

        agg = fp_analytics.compute_aggregate_integrity(self.state.sessions)
        focus_mins = agg['active_focus_mins']
        dist_mins = agg['distracted_mins']
        total = focus_mins + dist_mins

        if total <= 0:
            self.donut_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=self.theme['border'], width=stroke_w)
            self.donut_canvas.create_text(cx, cy, text="No Data", font=FONT_SMALL, fill=self.theme['text_secondary'])
            return

        focus_extent = (focus_mins / total) * 360
        dist_extent = 360 - focus_extent

        # Background track
        self.donut_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=self.theme['border'], width=stroke_w)

        # Distracted slice (danger/coral)
        self.donut_canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius, start=90, extent=-360, style=tk.ARC, outline=self.theme['danger'], width=stroke_w)

        # Active Focus slice (success/mint)
        if focus_extent > 0:
            self.donut_canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius, start=90, extent=-focus_extent, style=tk.ARC, outline=self.theme['success'], width=stroke_w)

        # Center Text
        int_pct = agg['overall_integrity']
        self.donut_canvas.create_text(cx, cy - 8, text=f"{int_pct}%", font=FONT_SUBTITLE, fill=self.theme['text_primary'])
        self.donut_canvas.create_text(cx, cy + 12, text="Pure Focus", font=FONT_SMALL, fill=self.theme['text_secondary'])

        # Legend on the right
        lx = 190
        ly = 75
        # Focus legend
        self.donut_canvas.create_rectangle(lx, ly, lx + 12, ly + 12, fill=self.theme['success'], outline="")
        self.donut_canvas.create_text(lx + 18, ly + 6, text=f"Focus: {focus_mins}m", font=FONT_SMALL, fill=self.theme['text_primary'], anchor="w")

        # Distracted legend
        self.donut_canvas.create_rectangle(lx, ly + 28, lx + 12, ly + 40, fill=self.theme['danger'], outline="")
        self.donut_canvas.create_text(lx + 18, ly + 34, text=f"Off-tab: {dist_mins}m", font=FONT_SMALL, fill=self.theme['text_primary'], anchor="w")

        # Tab switches count
        self.donut_canvas.create_text(lx, ly + 62, text=f"Switches: {agg['tab_switches']}", font=FONT_SMALL, fill=self.theme['text_secondary'], anchor="w")

    def _render_trend_bar_chart(self):
        self.trend_canvas.delete("all")
        w = 340
        h = 210

        trends = fp_analytics.compute_7_day_trends(self.state.sessions)
        if not trends:
            return

        max_mins = max([d['focus_mins'] + d['distracted_mins'] for d in trends] + [60])
        plot_h = 140
        baseline_y = 175
        col_w = 26
        spacing = 42
        start_x = 28

        for idx, day in enumerate(trends):
            x = start_x + idx * spacing
            tot = day['focus_mins'] + day['distracted_mins']

            if tot > 0:
                bar_h = (tot / max_mins) * plot_h
                focus_h = (day['focus_mins'] / max_mins) * plot_h
                dist_h = bar_h - focus_h

                # Distracted portion (top)
                if dist_h > 0:
                    self.trend_canvas.create_rectangle(
                        x, baseline_y - bar_h, x + col_w, baseline_y - focus_h,
                        fill=self.theme['danger'], outline=""
                    )

                # Focus portion (bottom)
                self.trend_canvas.create_rectangle(
                    x, baseline_y - focus_h, x + col_w, baseline_y,
                    fill=self.theme['success'], outline=""
                )

                # Minutes label on top of bar
                self.trend_canvas.create_text(
                    x + col_w / 2, baseline_y - bar_h - 8,
                    text=f"{int(day['focus_mins'])}m",
                    font=("Helvetica", 8),
                    fill=self.theme['text_secondary']
                )
            else:
                # Empty bar placeholder
                self.trend_canvas.create_rectangle(
                    x, baseline_y - 4, x + col_w, baseline_y,
                    fill=self.theme['border'], outline=""
                )

            # Day label (e.g. Mon, Tue)
            self.trend_canvas.create_text(
                x + col_w / 2, baseline_y + 14,
                text=day['day_label'],
                font=FONT_SMALL,
                fill=self.theme['text_primary']
            )

    def _render_timeline(self):
        for w in self.timeline_list_frame.winfo_children():
            w.destroy()

        timeline_blocks = fp_analytics.compute_daily_timeline(self.state.sessions)
        if not timeline_blocks:
            empty_lbl = tk.Label(
                self.timeline_list_frame,
                text="🌱 No study sessions recorded today yet. Start the Pomodoro timer to see live cycles!",
                font=FONT_BODY,
                bg=self.theme['bg_card'],
                fg=self.theme['text_secondary'],
                pady=16
            )
            empty_lbl.pack()
            return

        for b in timeline_blocks:
            row = tk.Frame(
                self.timeline_list_frame,
                bg=self.theme['bg_card_secondary'],
                padx=12,
                pady=8,
                highlightthickness=1,
                highlightbackground=self.theme['border']
            )
            row.pack(fill=tk.X, pady=4)

            # Left color indicator pill
            ind = tk.Frame(row, width=6, bg=b['color'])
            ind.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

            # Time & Task Info
            info_frame = tk.Frame(row, bg=self.theme['bg_card_secondary'])
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            title_row = tk.Frame(info_frame, bg=self.theme['bg_card_secondary'])
            title_row.pack(fill=tk.X)

            tk.Label(title_row, text=f"{b['time_label']} - {b['title']}", font=FONT_BODY_BOLD, bg=self.theme['bg_card_secondary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

            # Anti-Cheat details subtitle
            detail_str = f"{b['focus_mins']}m focused | {b['distracted_mins']}m distracted | {b['tab_switches']} tab switches"
            tk.Label(info_frame, text=detail_str, font=FONT_SMALL, bg=self.theme['bg_card_secondary'], fg=self.theme['text_secondary']).pack(anchor="w")

            # Right Badge with Integrity
            int_badge = tk.Label(
                row,
                text=f"{b['integrity']}% Integrity",
                font=FONT_BODY_BOLD,
                bg='#FFFFFF',
                fg=b['color'],
                padx=10,
                pady=3,
                highlightthickness=1,
                highlightbackground=b['color']
            )
            int_badge.pack(side=tk.RIGHT)
