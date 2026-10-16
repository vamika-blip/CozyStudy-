"""
theme.py - Aesthetic Pastel Themes and Visual Tokens for CozyStudy.

Features four hand-crafted palettes:
- Sakura (Soft blush pinks, creamy ivory, warm rose)
- Matcha (Cozy botanical greens, warm oat milk, soft sage)
- Lavender (Calming misty lilac, twilight purples, soft violet)
- Midnight (Lo-fi dark mode, cozy deep navy, warm amber lamp glow)
"""

THEMES = {
    'sakura': {
        'name': 'Sakura Blossom',
        'bg': '#FFF5F7',
        'bg_card': '#FFFFFF',
        'bg_card_secondary': '#FDF0F3',
        'accent': '#E79AAB',
        'accent_hover': '#D88395',
        'accent_light': '#FFE4EA',
        'text_primary': '#4A3B40',
        'text_secondary': '#8A7A80',
        'border': '#F4D4DD',
        'room_wall': '#FDE8EC',
        'room_floor': '#EBD5BA',
        'room_baseboard': '#D6BFA6',
        'room_window_sky_day': '#BEE3F8',
        'room_window_sky_night': '#2C3E50',
        'success': '#88B04B',
        'warning': '#F4A261',
        'danger': '#E76F51',
        'charm_coin': '#FFB703',
        'tab_active_bg': '#FFE4EA',
        'tab_active_fg': '#B85068'
    },
    'matcha': {
        'name': 'Matcha Study',
        'bg': '#F4F7F2',
        'bg_card': '#FFFFFF',
        'bg_card_secondary': '#EBF1E8',
        'accent': '#7A9A60',
        'accent_hover': '#688450',
        'accent_light': '#E2EBDC',
        'text_primary': '#323E2A',
        'text_secondary': '#6E7C66',
        'border': '#D3DFCC',
        'room_wall': '#EAF0E5',
        'room_floor': '#D9C5AA',
        'room_baseboard': '#C4B095',
        'room_window_sky_day': '#C3E6CB',
        'room_window_sky_night': '#1E2D24',
        'success': '#6F9E42',
        'warning': '#E09F3E',
        'danger': '#D9534F',
        'charm_coin': '#E9C46A',
        'tab_active_bg': '#E2EBDC',
        'tab_active_fg': '#4A6836'
    },
    'lavender': {
        'name': 'Lavender Haze',
        'bg': '#F8F6FC',
        'bg_card': '#FFFFFF',
        'bg_card_secondary': '#F0ECFA',
        'accent': '#9A86C4',
        'accent_hover': '#8670B3',
        'accent_light': '#E8E1F6',
        'text_primary': '#3B364A',
        'text_secondary': '#77708A',
        'border': '#DFD6F2',
        'room_wall': '#EEE8F8',
        'room_floor': '#DFC9B5',
        'room_baseboard': '#CBB5A1',
        'room_window_sky_day': '#C5D8F6',
        'room_window_sky_night': '#222034',
        'success': '#7BB069',
        'warning': '#F4A261',
        'danger': '#E76F51',
        'charm_coin': '#F4A261',
        'tab_active_bg': '#E8E1F6',
        'tab_active_fg': '#685098'
    },
    'midnight': {
        'name': 'Midnight Lo-Fi',
        'bg': '#1E1E2E',
        'bg_card': '#28283E',
        'bg_card_secondary': '#232338',
        'accent': '#CBA6F7',
        'accent_hover': '#B48EED',
        'accent_light': '#383454',
        'text_primary': '#CDD6F4',
        'text_secondary': '#A6ADC8',
        'border': '#3E3B5C',
        'room_wall': '#26243D',
        'room_floor': '#3D332A',
        'room_baseboard': '#2D241C',
        'room_window_sky_day': '#4A5568',
        'room_window_sky_night': '#0F111A',
        'success': '#A6E3A1',
        'warning': '#F9E2AF',
        'danger': '#F38BA8',
        'charm_coin': '#F9E2AF',
        'tab_active_bg': '#383454',
        'tab_active_fg': '#CBA6F7'
    }
}

# Typography tokens
FONT_FAMILY = "Helvetica"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_TIMER = (FONT_FAMILY, 40, "bold")
FONT_EMOJI_BIG = (FONT_FAMILY, 28)
