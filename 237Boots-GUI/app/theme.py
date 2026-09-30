# -*- coding: utf-8 -*-
"""Feuille de style sombre de l'interface 237Boots."""

ACCENT = "#00b894"
ACCENT_DIM = "#009e7d"
DANGER = "#d63031"
BG = "#14161a"
BG_ALT = "#1c1f26"
BORDER = "#2b303b"
FG = "#e6e8ec"
FG_DIM = "#8b93a1"

QSS = f"""
QWidget {{
    background: {BG};
    color: {FG};
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 10pt;
}}

QGroupBox {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    /* Pas de "padding" ici : en QSS il remplace le contentsRect du layout et
       rogne les libelles des radio/checkbox. Les marges reelles sont posees
       via setContentsMargins sur les QVBoxLayout enfants. */
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {FG_DIM};
}}

QLabel#Title {{
    font-size: 20pt;
    font-weight: 700;
    color: {FG};
}}
QLabel#Subtitle {{
    font-size: 10pt;
    color: {FG_DIM};
}}
QLabel#Dim {{ color: {FG_DIM}; }}
QLabel#Warn {{ color: {DANGER}; }}

QPushButton {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 14px;
    color: {FG};
}}
QPushButton:hover  {{ border-color: {ACCENT}; }}
QPushButton:pressed{{ background: {BG}; }}
QPushButton:disabled {{ color: #5a6070; border-color: #23262e; }}

QPushButton#Primary {{
    background: {ACCENT};
    border: none;
    color: #06281f;
    font-weight: 700;
    padding: 10px 18px;
}}
QPushButton#Primary:hover   {{ background: {ACCENT_DIM}; }}
QPushButton#Primary:disabled{{ background: #2b3a36; color: #5d6b66; }}

QPushButton#Danger {{ border-color: {DANGER}; color: #ff8a8a; }}

/* Bouton compact pour les en-tetes de bloc (le padding standard de 8px
   ferait deborder la ligne d'en-tete). */
QPushButton#Small {{
    padding: 1px 10px;
    font-size: 9pt;
    border-radius: 4px;
}}

/*
 * Les blocs sont construits avec un QFrame#Card + un QLabel#CardTitle plutot
 * qu'avec QGroupBox : le titre de QGroupBox passe par subcontrol-origin et son
 * "margin-top" rogne la zone de peinture des libelles radio/checkbox.
 */

QRadioButton {{ padding: 4px 2px; spacing: 8px; }}
QRadioButton::indicator {{
    width: 15px; height: 15px;
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {BG};
}}
QRadioButton::indicator:checked {{
    background: {ACCENT};
    border: 2px solid {BG};
}}

QCheckBox {{ padding: 4px 2px; spacing: 8px; }}
QCheckBox::indicator {{
    width: 15px; height: 15px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

QComboBox {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 150px;
}}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox QAbstractItemView {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    selection-color: #06281f;
    outline: none;
}}

QProgressBar {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    height: 16px;
    text-align: center;
    color: {FG};
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 5px;
}}

QPlainTextEdit {{
    background: #0f1114;
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: #b8c0cc;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
}}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: transparent; width: 10px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 5px; min-height: 30px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}

QFrame#Card {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QLabel#CardTitle {{
    color: {FG_DIM};
    font-weight: 600;
    padding-bottom: 6px;
}}

QMenuBar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
QMenuBar::item:selected {{ background: {BG_ALT}; }}
QMenu {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    padding: 4px;
}}
QMenu::item {{ padding: 6px 22px 6px 14px; border-radius: 4px; }}
QMenu::item:selected {{ background: {ACCENT}; color: #06281f; }}

QStatusBar {{ background: {BG}; color: {FG_DIM}; border-top: 1px solid {BORDER}; }}

QSplitter::handle {{ background: {BORDER}; }}
"""
