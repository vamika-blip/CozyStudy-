"""
wardrobe_dialog.py - Aesthetic Charm Wardrobe & Room Decor Shop.

Allows the user to:
- View current Star Charm balance (✨)
- Browse room charms by category (Desk, Wall, Pet, Floor)
- Unlock new charms using earned coins
- Equip / unequip charms in their cozy room diorama
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from fp_models import AppState, Charm
from fp_utils import find_first
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL


class WardrobeDialog(tk.Toplevel):
    def __init__(self, parent, state: AppState, on_unlock: Callable[[str], None], on_toggle_equip: Callable[[str], None]):
        super().__init__(parent)
        self.state = state
        self.on_unlock = on_unlock
        self.on_toggle_equip = on_toggle_equip

        theme_key = state.settings.theme
        self.theme = THEMES.get(theme_key, THEMES['sakura'])

        self.title("✨ Cozy Room Charm Wardrobe")
        self.geometry("640x520")
        self.minsize(550, 450)
        self.configure(bg=self.theme['bg'])

        # Center relative to parent
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=self.theme['bg_card'], padx=20, pady=16, highlightthickness=1, highlightbackground=self.theme['border'])
        header.pack(fill=tk.X)

        title_lbl = tk.Label(header, text="✨ Charm Wardrobe & Decor Shop", font=FONT_TITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary'])
        title_lbl.pack(side=tk.LEFT)

        self.coin_badge = tk.Label(
            header,
            text=f"✨ {self.state.coins} Star Charms",
            font=FONT_SUBTITLE,
            bg=self.theme['accent_light'],
            fg=self.theme['accent_hover'],
            padx=12,
            pady=4
        )
        self.coin_badge.pack(side=tk.RIGHT)

        subtitle_lbl = tk.Label(
            self,
            text="Earn charms by completing focus sessions with high integrity and finishing tasks before deadlines!",
            font=FONT_SMALL,
            bg=self.theme['bg'],
            fg=self.theme['text_secondary'],
            pady=8
        )
        subtitle_lbl.pack(fill=tk.X)

        # Category notebook / tabs
        style = ttk.Style()
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        categories = [
            ('desk', '🍵 Desk Decor'),
            ('wall', '🖼️ Wall & Lights'),
            ('pet', '🐾 Companions'),
            ('floor', '🛋️ Floor & Plants')
        ]

        for cat_key, cat_name in categories:
            frame = tk.Frame(notebook, bg=self.theme['bg'])
            notebook.add(frame, text=cat_name)
            self._populate_category(frame, cat_key)

    def _populate_category(self, parent_frame: tk.Frame, category: str):
        canvas = tk.Canvas(parent_frame, bg=self.theme['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        cat_charms = [c for c in self.state.charms if c.category == category]
        if not cat_charms:
            empty_lbl = tk.Label(scrollable_frame, text="No items in this category yet.", bg=self.theme['bg'], fg=self.theme['text_secondary'])
            empty_lbl.pack(pady=20)
            return

        for charm in cat_charms:
            self._render_charm_card(scrollable_frame, charm)

    def _render_charm_card(self, parent: tk.Frame, charm: Charm):
        card = tk.Frame(
            parent,
            bg=self.theme['bg_card'],
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=self.theme['border']
        )
        card.pack(fill=tk.X, padx=8, pady=6)

        # Icon
        icon_lbl = tk.Label(card, text=charm.icon, font=("Helvetica", 24), bg=self.theme['bg_card'])
        icon_lbl.pack(side=tk.LEFT, padx=(0, 12))

        # Details
        info_frame = tk.Frame(card, bg=self.theme['bg_card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        name_row = tk.Frame(info_frame, bg=self.theme['bg_card'])
        name_row.pack(fill=tk.X)

        name_lbl = tk.Label(name_row, text=charm.name, font=FONT_BODY_BOLD, bg=self.theme['bg_card'], fg=self.theme['text_primary'])
        name_lbl.pack(side=tk.LEFT)

        if charm.equipped:
            equipped_tag = tk.Label(
                name_row,
                text="In Room",
                font=FONT_SMALL,
                bg=self.theme['success'],
                fg='#FFFFFF',
                padx=6,
                pady=1
            )
            equipped_tag.pack(side=tk.LEFT, padx=8)

        desc_lbl = tk.Label(info_frame, text=charm.description, font=FONT_SMALL, bg=self.theme['bg_card'], fg=self.theme['text_secondary'])
        desc_lbl.pack(anchor="w", pady=(2, 0))

        # Action Button (Unlock or Equip / Unequip)
        action_frame = tk.Frame(card, bg=self.theme['bg_card'])
        action_frame.pack(side=tk.RIGHT)

        if not charm.unlocked:
            can_afford = self.state.coins >= charm.cost
            btn_text = f"Unlock ({charm.cost} ✨)"
            btn = tk.Button(
                action_frame,
                text=btn_text,
                font=FONT_SMALL,
                bg=self.theme['accent'] if can_afford else self.theme['border'],
                fg='#FFFFFF' if can_afford else self.theme['text_secondary'],
                relief=tk.FLAT,
                padx=10,
                pady=4,
                cursor="hand2" if can_afford else "arrow",
                command=lambda cid=charm.id: self._handle_unlock(cid)
            )
            btn.pack()
        else:
            equip_text = "Equipped ✓" if charm.equipped else "Equip"
            btn = tk.Button(
                action_frame,
                text=equip_text,
                font=FONT_SMALL,
                bg=self.theme['tab_active_bg'] if charm.equipped else self.theme['bg_card_secondary'],
                fg=self.theme['tab_active_fg'] if charm.equipped else self.theme['text_primary'],
                relief=tk.FLAT,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda cid=charm.id: self._handle_toggle(cid)
            )
            btn.pack()

    def _handle_unlock(self, charm_id: str):
        charm = find_first(lambda c: c.id == charm_id, self.state.charms)
        if not charm:
            return
        if self.state.coins < charm.cost:
            messagebox.showinfo("Need More Charms", f"You need {charm.cost} Star Charms to unlock {charm.name}. Keep studying!")
            return

        self.on_unlock(charm_id)
        self.destroy()

    def _handle_toggle(self, charm_id: str):
        self.on_toggle_equip(charm_id)
        self.destroy()
