#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-test de l'interface 237Boots.

Construct la fenetre hors ecran et verifie ce qui peut l'etre sans disque
reel : import, enumeration, bascule de langue, etat des boutons.

    python selftest.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt6.QtWidgets import QApplication  # noqa: E402

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "OK  " if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        failures.append(label)


def main() -> int:
    app = QApplication(sys.argv)

    from app import i18n, theme
    from app.engine import CLI_MAGIC, find_engine, missing_payload
    from app.mainwindow import MainWindow

    print("237Boots - auto-test")
    print("-" * 60)

    print("theme")
    check("feuille de style non vide", len(theme.QSS) > 500, f"{len(theme.QSS)} car.")

    print("i18n")
    check("locale par defaut fr_CM", i18n.get_locale() == "fr_CM")
    check("cle manquante renvoie la cle", i18n.t("__absent__") == "__absent__")
    i18n.set_locale("en_CM")
    check("bascule en_CM", i18n.t("install") == "Install")
    i18n.set_locale("fr_CM")
    check("retour fr_CM", i18n.t("install") == "Installer")

    print("moteur")
    check("magic CLI = VTOYCLI", CLI_MAGIC == "VTOYCLI")
    exe = find_engine()
    check("moteur localise", exe is not None, str(exe) if exe else "absent")
    if exe is not None:
        # Informatif : hors paquetage de release (arborescence des sources ou
        # runner CI), le payload est absent par construction. L'IHM le signale
        # a l'utilisateur, ce n'est donc pas une erreur de l'interface.
        absent = missing_payload(exe.parent)
        print(
            f"  [INFO] payload {'complet' if not absent else 'absent (normal hors release) : ' + ', '.join(absent)}"
        )

    print("fenetre")
    window = MainWindow()
    app.processEvents()
    check("MainWindow instanciee", True)

    disks = window._disks
    check("enumeration de disques", isinstance(disks, list), f"{len(disks)} disque(s)")
    for d in disks:
        print(f"         #{d.index} {d.model[:36]:<36} {d.bus_label:<10} {d.part_scheme}")

    check("journal en lecture seule", window._log.isReadOnly())
    check("barre de progression presente", window._bar.maximum() == 100)

    if disks:
        check("une selection par defaut", window._selected() is not None)
        sel = window._selected()
        check("install actif", window._install.isEnabled())
        expected_update = sel.has_boots_esp
        check(
            "etat du bouton mise a jour coherent",
            window._update.isEnabled() == expected_update,
            f"installable={sel.has_boots_esp}",
        )
    else:
        check("aucun disque : install desactive", not window._install.isEnabled())

    print("-" * 60)
    if failures:
        print(f"ECHEC : {len(failures)} verification(s)")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("OK : toutes les verifications passent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
