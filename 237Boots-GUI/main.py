#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""237Boots - point d'entree de l'interface graphique.

    pip install PyQt6
    python main.py
"""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

# Permet de lancer `python main.py` depuis la racine du projet.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.mainwindow import MainWindow  # noqa: E402


def _apply_dark_titlebar(hwnd: int) -> None:
    """Titre de fenetre sombre sur Windows 10/11."""
    if sys.platform != "win32":
        return
    try:
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)  # DWMWA_USE_IMMERSIVE_DARK_MODE
        )
    except Exception:
        pass


def main() -> int:
    if sys.platform != "win32":
        print("237Boots ne fonctionne que sous Windows.", file=sys.stderr)
        return 1

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("237Boots")
    app.setApplicationDisplayName("237Boots")
    app.setOrganizationName("237Boots")

    window = MainWindow()
    window.show()
    if sys.platform == "win32":
        _apply_dark_titlebar(int(window.winId()))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
