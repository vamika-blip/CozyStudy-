# 🌸 CozyStudy - Aesthetic Gamified Study Sanctuary

> A 100% Python Native Desktop GUI application (Tkinter + Canvas) built with **Functional Programming** paradigms. Featuring an interactive cozy room diorama, an anti-cheating focus timer with window/tab-switch tracking, vector canvas focus cycle analytics, calendar logs, and a deadline-driven priority task manager.

---

## ✨ Key Features

1. **Anti-Cheat Focus Engine (`timer_view.py`)**:
   - **Honest Tracking Mode (Default)**: The timer keeps running seamlessly when you switch tabs, apps, or windows (*"like yk how you open other tabs but it still goes on"*), while accurately clocking your exact **Active Focus Time** vs **Off-Screen Distracted Time**, logging tab switches, and computing your live **Focus Integrity Rate (%)**.
   - **Strict Guardian Mode**: Automatically sounds an alert chime and pauses the session if you switch away from the window.
   - Earns **Star Charms (✨)** when you finish sessions with $\ge 80\%$ integrity!

2. **Aesthetic Cozy Room Diorama (`room_canvas.py`)**:
   - Interactive Canvas-drawn study sanctuary featuring:
     - Desk with pastel laptop, open notebook, desk mat.
     - Dynamic window (daytime sun/clouds or nighttime crescent moon and twinkling stars).
     - Bookshelf with pastel book stacks and trailing plants.
     - **Mochi the Calico Cat**: Sleeps on the rug with breathing animations and "z z Z" sleep particles; click Mochi for encouraging purrs!
     - **Steaming Matcha Latte**: Animated rising steam particles.
     - **Desk Lamp**: Interactive toggleable warm amber light cone.
   - **Charm Wardrobe & Decor Shop (`wardrobe_dialog.py`)**:
     - Spend your earned Star Charms to unlock and equip charms: Fairy lights, Mochi bunny, Monstera plant, Polaroid memory wall, Vintage lo-fi radio, Amethyst crystal, and more!

3. **Graphical Focus Cycle Analytics (`charts_canvas.py`)**:
   - **Focus Integrity Donut Chart**: Visual split of pure focus vs off-tab distracted minutes with central integrity percentage.
   - **Daily Focus Cycles Chronometer**: Chronological study blocks for each session, color-coded by integrity (Emerald Green $\ge 90\%$, Amber $75-89\%$, Soft Rose $<75\%$).
   - **7-Day Trend Stacked Bar Chart**: Daily focus minutes vs off-tab minutes and tab-switch counts.
   - **Productivity KPI Cards**: Total study hours, best streak, completed cycles.

4. **Priority Task & Deadline Manager (`task_view.py`)**:
   - Categorized by subject/course with pastel tags.
   - Eisenhower priority badges (High, Medium, Low).
   - Deadline countdowns (*"Due Today"*, *"Overdue"*, *"Due in 2 days"*).
   - "Focus Now" button that instantly binds a task to the Pomodoro timer.
   - Completing tasks before deadlines awards bonus Star Charms!

5. **Monthly Study Calendar & Daily Log Inspector (`calendar_view.py`)**:
   - Monthly grid with month navigation.
   - Glowing activity indicator dots for study sessions and deadlines.
   - Day Inspector drawer: click any day to see total study time, tab switches, and detailed session logs.

6. **Functional Programming Core (`fp_models.py`, `fp_utils.py`, `fp_reducers.py`, `fp_analytics.py`)**:
   - **Immutability**: All domain models are frozen dataclasses (`@dataclass(frozen=True)`).
   - **Pure Reducers**: State transformations take `(AppState, Action) -> AppState` without in-place mutation.
   - **Higher-Order Functions**: Pipelines using `pipe`, `compose`, `curry`, `map_tuple`, `filter_tuple`, and `reduce_iterable`.
   - **Zero Pip Dependencies**: Runs 100% locally with Python's built-in standard library and Tkinter.

---

## 🚀 How to Run CozyStudy

In your terminal, navigate to this directory and run:

```bash
python3 main.py
```

Or run via `sh`:
```bash
sh run.sh
```

### Running Automated Tests

A complete unit test suite verifying the functional core, immutability, pure reducers, and analytics is included:

```bash
python3 test_app.py
```

---

## 🎨 Theme Customization

CozyStudy includes 4 hand-crafted pastel palettes in the **Settings** tab:
- **Sakura Blossom** (Soft blush pinks and cream)
- **Matcha Study** (Calming botanical greens and sage)
- **Lavender Haze** (Soothing misty violet)
- **Midnight Lo-Fi** (Cozy dark mode with warm lamp accents)

---

## 📂 File Architecture

```
├── main.py               # Main GUI shell & global event controller
├── fp_models.py          # Immutable domain models (frozen dataclasses)
├── fp_utils.py           # Pure combinators: pipe, curry, map/filter/reduce
├── fp_reducers.py        # Pure state transition reducers
├── fp_analytics.py       # Higher-order focus cycle aggregation pipelines
├── room_canvas.py        # Cozy room diorama & charm renderer
├── timer_view.py         # Anti-cheat Pomodoro timer & window focus tracker
├── charts_canvas.py      # Vector canvas graphical focus cycle charts
├── task_view.py          # Priority task manager with deadline tracking
├── calendar_view.py      # Monthly calendar & daily study log inspector
├── wardrobe_dialog.py    # Charm wardrobe shop & room customizer
├── theme.py              # Pastel palettes & typography tokens
├── storage.py            # JSON persistence & seed data
├── cozystudy_data.json   # Local storage database
├── test_app.py           # Comprehensive automated test suite
└── README.md             # Documentation
```
