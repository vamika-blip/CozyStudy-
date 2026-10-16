"""
room_canvas.py - Aesthetic Cozy Study Room Diorama with Vector Canvas Graphics.

Renders an interactive, pastel diorama of a student's study room.
Dynamically displays unlocked and equipped charms:
- Steaming matcha latte
- Desk lamp with warm cone of light
- Sleeping calico cat (Mochi) with breathing & sleep particles
- Fairy lights, bookshelf, monstera, polaroids, lo-fi radio, moon globe
- Dynamic window view with day/night sky and animated rain/stars
"""

import math
import random
import tkinter as tk
from datetime import datetime
from typing import Dict, Any, Callable

from fp_models import AppState, Charm
from theme import THEMES, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_SMALL


class RoomCanvas(tk.Frame):
    def __init__(self, parent, state: AppState, on_open_wardrobe: Callable[[], None]):
        super().__init__(parent, bg='#FFFFFF')
        self.state = state
        self.on_open_wardrobe = on_open_wardrobe
        self.animation_step = 0
        self.lamp_on = True
        self.pet_message = ""
        self.pet_msg_time = 0

        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])

        self._build_ui()
        self._start_animation_loop()

    def _build_ui(self):
        # Header banner for the room
        header = tk.Frame(self, bg=self.theme['bg_card'], padx=16, pady=10, highlightthickness=1, highlightbackground=self.theme['border'])
        header.pack(fill=tk.X)

        title_frame = tk.Frame(header, bg=self.theme['bg_card'])
        title_frame.pack(side=tk.LEFT)

        tk.Label(title_frame, text="🌸 Cozy Study Sanctuary", font=FONT_SUBTITLE, bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)

        streak_badge = tk.Label(
            title_frame,
            text=f"🔥 {self.state.stats.current_streak} Day Streak",
            font=FONT_SMALL,
            bg=self.theme['accent_light'],
            fg=self.theme['accent_hover'],
            padx=8,
            pady=2
        )
        streak_badge.pack(side=tk.LEFT, padx=12)

        # Wardrobe Decorator Button
        self.btn_decor = tk.Button(
            header,
            text=f"✨ Decorate Room ({self.state.coins} Charms)",
            font=FONT_SMALL,
            bg=self.theme['accent'],
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.on_open_wardrobe
        )
        self.btn_decor.pack(side=tk.RIGHT)

        # The Main Drawing Canvas
        self.canvas = tk.Canvas(self, bg=self.theme['room_wall'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

    def update_state(self, state: AppState):
        self.state = state
        self.theme_key = state.settings.theme
        self.theme = THEMES.get(self.theme_key, THEMES['sakura'])
        self.btn_decor.configure(
            text=f"✨ Decorate Room ({self.state.coins} Charms)",
            bg=self.theme['accent']
        )
        self.redraw()

    def _on_resize(self, event):
        self.redraw()

    def _start_animation_loop(self):
        self.animation_step += 1
        if self.pet_msg_time > 0 and (self.animation_step - self.pet_msg_time) > 40:
            self.pet_message = ""
        self.redraw()
        self.after(100, self._start_animation_loop)

    def _adjust_color(self, hex_color: str, delta: int) -> str:
        """Helper to adjust color lightness."""
        try:
            h = hex_color.lstrip('#')
            if len(h) != 6:
                return hex_color
            r = max(0, min(255, int(h[0:2], 16) + delta))
            g = max(0, min(255, int(h[2:4], 16) + delta))
            b = max(0, min(255, int(h[4:6], 16) + delta))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def is_charm_equipped(self, charm_id: str) -> bool:
        for c in self.state.charms:
            if c.id == charm_id and c.equipped:
                return True
        return False

    def redraw(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return

        self.canvas.delete("all")

        # 1. Base Room Geometry (Wall & Floor)
        floor_y = h * 0.62
        # Wall background
        self.canvas.create_rectangle(0, 0, w, floor_y, fill=self.theme['room_wall'], outline="")
        # Floor
        self.canvas.create_rectangle(0, floor_y, w, h, fill=self.theme['room_floor'], outline="")
        # Baseboard
        baseboard_h = 14
        self.canvas.create_rectangle(0, floor_y - baseboard_h, w, floor_y, fill=self.theme['room_baseboard'], outline="")

        # Floor wooden planks pattern
        plank_spacing = 45
        for px in range(0, w + 100, plank_spacing):
            self.canvas.create_line(px, floor_y, px - 60, h, fill=self._adjust_color(self.theme['room_floor'], -15), width=1)

        # 2. Cozy Rug in center floor
        rug_cx = w * 0.48
        rug_cy = floor_y + (h - floor_y) * 0.48
        rug_rx = min(w * 0.35, 220)
        rug_ry = min((h - floor_y) * 0.38, 70)
        self.canvas.create_oval(
            rug_cx - rug_rx, rug_cy - rug_ry,
            rug_cx + rug_rx, rug_cy + rug_ry,
            fill=self.theme['bg_card_secondary'],
            outline=self.theme['border'],
            width=2
        )
        # Inner decorative ring on rug
        self.canvas.create_oval(
            rug_cx - rug_rx * 0.85, rug_cy - rug_ry * 0.85,
            rug_cx + rug_rx * 0.85, rug_cy + rug_ry * 0.85,
            fill="",
            outline=self.theme['accent_light'],
            width=1,
            dash=(4, 4)
        )

        # 3. Cozy Window View
        self._draw_window(w, h, floor_y)

        # 4. Bookshelf on the Left Wall
        self._draw_bookshelf(w, h, floor_y)

        # 5. Study Desk & Chair in Center-Right
        self._draw_desk_and_chair(w, h, floor_y)

        # 6. Draw Equipped Charms
        self._draw_equipped_charms(w, h, floor_y, rug_cx, rug_cy)

        # 7. Pet interaction message bubble if clicked
        if self.pet_message:
            self.canvas.create_rectangle(rug_cx - 90, rug_cy - 65, rug_cx + 90, rug_cy - 30, fill='#FFFFFF', outline=self.theme['accent'], width=2)
            self.canvas.create_polygon(rug_cx, rug_cy - 30, rug_cx - 8, rug_cy - 20, rug_cx + 8, rug_cy - 30, fill='#FFFFFF', outline=self.theme['accent'])
            self.canvas.create_text(rug_cx, rug_cy - 48, text=self.pet_message, font=FONT_SMALL, fill=self.theme['text_primary'])

    def _draw_window(self, w, h, floor_y):
        win_w = min(160, w * 0.28)
        win_h = min(180, floor_y * 0.65)
        win_x = w * 0.70
        win_y = floor_y * 0.15

        # Window sky
        sky_color = self.theme['room_window_sky_day'] if self.theme_key != 'midnight' else self.theme['room_window_sky_night']
        self.canvas.create_rectangle(win_x, win_y, win_x + win_w, win_y + win_h, fill=sky_color, outline="")

        # Celestial body (Sun or Moon)
        if self.theme_key == 'midnight':
            # Crescent Moon
            moon_x = win_x + win_w * 0.75
            moon_y = win_y + win_h * 0.25
            self.canvas.create_oval(moon_x - 12, moon_y - 12, moon_x + 12, moon_y + 12, fill='#FFF275', outline="")
            self.canvas.create_oval(moon_x - 7, moon_y - 14, moon_x + 15, moon_y + 10, fill=sky_color, outline="")
            # Twinkling stars
            for i, (sx, sy) in enumerate([(0.2, 0.2), (0.4, 0.35), (0.3, 0.6), (0.8, 0.55), (0.6, 0.15)]):
                alpha = 0.5 + 0.5 * math.sin((self.animation_step + i * 2) * 0.4)
                star_color = '#FFFFFF' if alpha > 0.6 else '#A6ADC8'
                self.canvas.create_text(win_x + win_w * sx, win_y + win_h * sy, text="✦", font=("Helvetica", 8), fill=star_color)
        else:
            # Gentle daytime sun & cloud
            sun_x = win_x + win_w * 0.8
            sun_y = win_y + win_h * 0.25
            self.canvas.create_oval(sun_x - 14, sun_y - 14, sun_x + 14, sun_y + 14, fill='#FFE066', outline="")
            # Soft fluffy cloud
            cx = win_x + win_w * 0.3 + (self.animation_step % 120) * 0.1
            cy = win_y + win_h * 0.4
            self.canvas.create_oval(cx - 15, cy - 8, cx + 15, cy + 8, fill='#FFFFFF', outline="")
            self.canvas.create_oval(cx - 6, cy - 14, cx + 18, cy + 6, fill='#FFFFFF', outline="")

        # Window Frame & Grid Cross
        frame_color = '#FFFFFF' if self.theme_key != 'midnight' else '#383454'
        self.canvas.create_rectangle(win_x, win_y, win_x + win_w, win_y + win_h, outline=frame_color, width=6)
        self.canvas.create_line(win_x + win_w / 2, win_y, win_x + win_w / 2, win_y + win_h, fill=frame_color, width=3)
        self.canvas.create_line(win_x, win_y + win_h / 2, win_x + win_w, win_y + win_h / 2, fill=frame_color, width=3)

        # Window sill
        self.canvas.create_rectangle(win_x - 8, win_y + win_h, win_x + win_w + 8, win_y + win_h + 8, fill=frame_color, outline=self.theme['border'])

        # Fairy lights charm check
        if self.is_charm_equipped('charm_fairylights'):
            points = []
            for i in range(7):
                t = i / 6
                lx = win_x + win_w * t
                ly = win_y - 4 + math.sin(t * math.pi) * 8
                points.append((lx, ly))
                # Bulb
                glow = "#FFE066" if (self.animation_step + i) % 3 != 0 else "#FFF9A6"
                self.canvas.create_oval(lx - 4, ly - 4, lx + 4, ly + 4, fill=glow, outline="")
            # Wire
            wire_pts = [coord for pt in points for coord in pt]
            self.canvas.create_line(wire_pts, fill='#8A7A80', width=1, smooth=True)

    def _draw_bookshelf(self, w, h, floor_y):
        shelf_x = w * 0.08
        shelf_y = floor_y * 0.22
        shelf_w = min(110, w * 0.2)
        shelf_h = 8

        # Top shelf
        self.canvas.create_rectangle(shelf_x, shelf_y, shelf_x + shelf_w, shelf_y + shelf_h, fill='#D9C5AA', outline='#B8A489')
        # Books on shelf
        book_colors = ['#E79AAB', '#92A8D1', '#88B04B', '#9A86C4', '#F4A261']
        bx = shelf_x + 8
        for i, col in enumerate(book_colors):
            bw = 8
            bh = 22 + (i % 3) * 6
            self.canvas.create_rectangle(bx, shelf_y - bh, bx + bw, shelf_y, fill=col, outline="")
            bx += bw + 2

        # Second shelf
        shelf2_y = shelf_y + 48
        self.canvas.create_rectangle(shelf_x, shelf2_y, shelf_x + shelf_w, shelf2_y + shelf_h, fill='#D9C5AA', outline='#B8A489')
        # Trailing plant on second shelf
        self.canvas.create_oval(shelf_x + 12, shelf2_y - 12, shelf_x + 28, shelf2_y, fill='#E79AAB', outline="")  # Pot
        # Vines
        self.canvas.create_text(shelf_x + 20, shelf2_y - 10, text="🪴", font=("Helvetica", 14))

    def _draw_desk_and_chair(self, w, h, floor_y):
        desk_w = min(240, w * 0.42)
        desk_h = 16
        desk_x = w * 0.45
        desk_y = floor_y * 0.72

        # Chair behind/near desk
        chair_x = desk_x + desk_w * 0.28
        chair_y = desk_y - 20
        self.canvas.create_rectangle(chair_x, chair_y, chair_x + 50, chair_y + 42, fill=self.theme['accent_light'], outline=self.theme['border'], width=2)
        self.canvas.create_line(chair_x + 25, chair_y + 42, chair_x + 25, floor_y + 25, fill='#777777', width=4)
        # Chair cushion
        self.canvas.create_oval(chair_x - 4, chair_y + 28, chair_x + 54, chair_y + 44, fill=self.theme['accent'], outline="")

        # Desk Surface
        desk_col = '#FDF0E6' if self.theme_key != 'midnight' else '#36344E'
        desk_edge = '#E0CAB5' if self.theme_key != 'midnight' else '#26243D'
        self.canvas.create_rectangle(desk_x, desk_y, desk_x + desk_w, desk_y + desk_h, fill=desk_col, outline=desk_edge, width=2)

        # Desk Legs
        leg_color = '#B8A489' if self.theme_key != 'midnight' else '#222034'
        self.canvas.create_rectangle(desk_x + 10, desk_y + desk_h, desk_x + 18, floor_y + 22, fill=leg_color, outline="")
        self.canvas.create_rectangle(desk_x + desk_w - 18, desk_y + desk_h, desk_x + desk_w - 10, floor_y + 22, fill=leg_color, outline="")

        # Desk Mat
        mat_x = desk_x + desk_w * 0.18
        mat_w = desk_w * 0.55
        self.canvas.create_rectangle(mat_x, desk_y - 2, mat_x + mat_w, desk_y + 2, fill=self.theme['accent_light'], outline="")

        # Laptop open on desk
        lap_x = mat_x + (mat_w - 46) / 2
        lap_y = desk_y - 32
        # Screen
        screen_bg = '#FFFFFF' if self.theme_key != 'midnight' else '#1E1E2E'
        self.canvas.create_rectangle(lap_x, lap_y, lap_x + 46, lap_y + 30, fill=screen_bg, outline='#B8B8C8', width=2)
        # Tiny code lines on screen
        self.canvas.create_line(lap_x + 6, lap_y + 8, lap_x + 28, lap_y + 8, fill=self.theme['accent'], width=2)
        self.canvas.create_line(lap_x + 6, lap_y + 14, lap_x + 36, lap_y + 14, fill=self.theme['success'], width=2)
        self.canvas.create_line(lap_x + 6, lap_y + 20, lap_x + 22, lap_y + 20, fill=self.theme['warning'], width=2)
        # Keyboard base
        self.canvas.create_polygon(lap_x - 4, lap_y + 30, lap_x + 50, lap_y + 30, lap_x + 46, lap_y + 35, lap_x, lap_y + 35, fill='#D6D6E0', outline="")

    def _draw_equipped_charms(self, w, h, floor_y, rug_cx, rug_cy):
        desk_w = min(240, w * 0.42)
        desk_x = w * 0.45
        desk_y = floor_y * 0.72

        # 1. Steaming Matcha Latte
        if self.is_charm_equipped('charm_matcha'):
            mx = desk_x + desk_w * 0.8
            my = desk_y - 12
            # Cup
            self.canvas.create_rectangle(mx, my, mx + 16, my + 14, fill='#7A9A60', outline='#5E7947', width=1)
            self.canvas.create_arc(mx + 12, my + 2, mx + 20, my + 10, start=-90, extent=180, style=tk.ARC, outline='#5E7947', width=2)
            # Animated Steam Particles
            s_offset = (self.animation_step % 20) * 0.8
            self.canvas.create_line(mx + 6, my - 2 - s_offset, mx + 4, my - 8 - s_offset, fill='#D3DFCC', width=1.5, smooth=True)
            self.canvas.create_line(mx + 11, my - 4 - s_offset, mx + 13, my - 10 - s_offset, fill='#D3DFCC', width=1.5, smooth=True)

        # 2. Desk Lamp with Light Cone
        if self.is_charm_equipped('charm_lamp'):
            lx = desk_x + 18
            ly = desk_y - 45
            # Lamp pole & shade
            self.canvas.create_line(lx, desk_y, lx, ly + 16, fill='#666666', width=3)
            self.canvas.create_polygon(lx - 12, ly + 16, lx + 12, ly + 16, lx + 8, ly, lx - 8, ly, fill=self.theme['accent'], outline="")
            # Lamp Light Cone (translucent yellow stipple)
            if self.lamp_on:
                self.canvas.create_polygon(
                    lx - 10, ly + 16, lx + 10, ly + 16,
                    lx + 45, desk_y + 14, lx - 30, desk_y + 14,
                    fill='#FFE885', outline="", stipple='gray25'
                )

        # 3. Sleeping Calico Cat (Mochi)
        if self.is_charm_equipped('charm_calico'):
            cx = rug_cx + 10
            cy = rug_cy + 8
            # Breathing expansion
            breath = math.sin(self.animation_step * 0.25) * 1.5
            # Cat body
            self.canvas.create_oval(cx - 20, cy - 14 - breath, cx + 20, cy + 14, fill='#F7DCB4', outline='#D4A373', width=1.5)
            # Calico patches
            self.canvas.create_oval(cx - 14, cy - 10 - breath, cx - 2, cy + 4, fill='#C86D51', outline="")
            self.canvas.create_oval(cx + 4, cy - 6 - breath, cx + 16, cy + 8, fill='#4A3B40', outline="")
            # Head & sleeping eyes
            self.canvas.create_oval(cx - 24, cy - 8 - breath, cx - 8, cy + 8, fill='#F7DCB4', outline='#D4A373')
            self.canvas.create_arc(cx - 20, cy - 1, cx - 12, cy + 3, start=0, extent=-180, style=tk.ARC, width=1.5)
            # Ears
            self.canvas.create_polygon(cx - 22, cy - 6, cx - 26, cy - 15, cx - 18, cy - 10, fill='#C86D51')
            self.canvas.create_polygon(cx - 14, cy - 8, cx - 10, cy - 16, cx - 6, cy - 8, fill='#F7DCB4')
            # Tail
            tail_wag = math.sin(self.animation_step * 0.18) * 3
            self.canvas.create_line(cx + 18, cy, cx + 28, cy - 6 + tail_wag, fill='#C86D51', width=3, smooth=True)

            # Floating Z z z particles
            z_step = self.animation_step % 30
            zx = cx - 24 - z_step * 0.6
            zy = cy - 15 - z_step * 1.2
            self.canvas.create_text(zx, zy, text="z", font=("Helvetica", 9), fill=self.theme['accent_hover'])

        # 4. Fluffy Mochi Bunny
        if self.is_charm_equipped('charm_bunny'):
            bx = rug_cx - 80
            by = rug_cy - 10
            self.canvas.create_oval(bx - 14, by - 10, bx + 14, by + 10, fill='#FFFFFF', outline='#E0D7D7', width=1.5)
            # Long Ears
            self.canvas.create_oval(bx - 8, by - 24, bx - 2, by - 8, fill='#FFFFFF', outline='#E0D7D7')
            self.canvas.create_oval(bx + 2, by - 24, bx + 8, by - 8, fill='#FFFFFF', outline='#E0D7D7')
            # Pink inside ears
            self.canvas.create_oval(bx - 6, by - 20, bx - 4, by - 10, fill='#FFD1DC', outline="")
            self.canvas.create_oval(bx + 4, by - 20, bx + 6, by - 10, fill='#FFD1DC', outline="")
            # Cute face
            self.canvas.create_text(bx, by, text="• ᆺ •", font=("Helvetica", 8), fill='#7A6C6C')

        # 5. Baby Succulent Pot
        if self.is_charm_equipped('charm_succulent'):
            sx = desk_x + desk_w * 0.12
            sy = desk_y - 12
            self.canvas.create_text(sx, sy, text="🪴", font=("Helvetica", 16))

        # 6. Vintage Lo-Fi Radio
        if self.is_charm_equipped('charm_radio'):
            rx = desk_x + desk_w * 0.9
            ry = desk_y - 28
            self.canvas.create_rectangle(rx, ry, rx + 24, ry + 16, fill='#D9A066', outline='#8F563B', width=1)
            self.canvas.create_oval(rx + 4, ry + 4, rx + 12, ry + 12, fill='#4A3B40')
            # Antenna
            self.canvas.create_line(rx + 2, ry, rx - 6, ry - 12, fill='#4A3B40', width=1)
            # Musical note floating
            note_y = ry - 14 - (self.animation_step % 20) * 0.5
            self.canvas.create_text(rx + 14, note_y, text="♫", font=("Helvetica", 9), fill=self.theme['accent'])

        # 7. Amethyst Focus Crystal
        if self.is_charm_equipped('charm_crystal'):
            cryst_x = desk_x + desk_w * 0.04
            cryst_y = desk_y - 14
            self.canvas.create_text(cryst_x, cryst_y, text="🔮", font=("Helvetica", 16))

        # 8. Polaroid Memory Wall
        if self.is_charm_equipped('charm_polaroids'):
            px = w * 0.32
            py = floor_y * 0.2
            # Hanging string
            self.canvas.create_line(px - 30, py - 5, px + 50, py + 5, fill='#A6ADC8', width=1)
            # 2 Polaroids
            for idx, (ox, rot) in enumerate([(0, -5), (32, 4)]):
                self.canvas.create_rectangle(px + ox, py, px + ox + 22, py + 28, fill='#FFFFFF', outline='#C0C0C0', width=1)
                self.canvas.create_rectangle(px + ox + 2, py + 2, px + ox + 20, py + 18, fill=self.theme['accent_light'], outline="")
                # Tiny clothespin
                self.canvas.create_rectangle(px + ox + 8, py - 3, px + ox + 14, py + 2, fill='#C89F65', outline="")

        # 9. Monstera Plant on floor
        if self.is_charm_equipped('charm_monstera'):
            mx = w * 0.05
            my = floor_y + 15
            self.canvas.create_text(mx + 20, my, text="🌿", font=("Helvetica", 32))
            self.canvas.create_oval(mx + 10, my + 14, mx + 30, my + 30, fill='#B08968', outline="")  # Pot

        # 10. Velvet Cloud Beanbag
        if self.is_charm_equipped('charm_beanbag'):
            bx = w * 0.92
            by = floor_y + 35
            self.canvas.create_oval(bx - 35, by - 24, bx + 35, by + 24, fill=self.theme['accent_light'], outline=self.theme['border'], width=2)
            self.canvas.create_oval(bx - 20, by - 12, bx + 20, by + 12, fill=self.theme['bg_card_secondary'], outline="")

        # 11. Floating Moon Globe
        if self.is_charm_equipped('charm_globe'):
            gx = desk_x + desk_w * 0.7
            gy = desk_y - 32 + math.sin(self.animation_step * 0.2) * 2
            self.canvas.create_text(gx, gy, text="🌙", font=("Helvetica", 14))

    def _on_click(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        floor_y = h * 0.62
        rug_cx = w * 0.48
        rug_cy = floor_y + (h - floor_y) * 0.48

        # Click on Cat?
        dist_to_cat = math.hypot(event.x - rug_cx, event.y - rug_cy)
        if dist_to_cat < 45 and self.is_charm_equipped('charm_calico'):
            pet_quotes = [
                "Purrr... Mochi believes in you! 🐾",
                "Mochi stretches his paws! Keep focusing! ✨",
                "Mochi snores peacefully beside you. 💤",
                "Meow! You are making great progress today! 🌸"
            ]
            self.pet_message = random.choice(pet_quotes)
            self.pet_msg_time = self.animation_step
            self.redraw()
            return

        # Click on Desk Lamp?
        desk_x = w * 0.45
        desk_y = floor_y * 0.72
        lamp_x = desk_x + 18
        lamp_y = desk_y - 45
        if math.hypot(event.x - lamp_x, event.y - lamp_y) < 30 and self.is_charm_equipped('charm_lamp'):
            self.lamp_on = not self.lamp_on
            self.redraw()
            return
