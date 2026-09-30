#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit 237Boots.exe et assemble le paquetage distribuable.

    python build.py            # onefile + copie du moteur -> dist/237Boots-win64/
    python build.py --onedir   # version dossier (demarrage instantane)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INSTALL = ROOT.parent / "INSTALL"
VERSION = "1.1.17-CM1"
REPO = "https://github.com/noumegniedmond237-sketch/237Boots"


def engine_name() -> str:
    if sys.platform != "win32":
        raise SystemExit("237Boots ne se construit que sous Windows.")
    import platform

    machine = platform.machine().lower()
    return {
        "amd64": "Ventoy2Disk_X64.exe", "x86_64": "Ventoy2Disk_X64.exe", "x64": "Ventoy2Disk_X64.exe",
        "arm64": "Ventoy2Disk_ARM64.exe", "aarch64": "Ventoy2Disk_ARM64.exe",
    }.get(machine, "Ventoy2Disk.exe")


def run(*args: str) -> None:
    print("$", " ".join(args))
    subprocess.run(args, check=True)


def main() -> int:
    onedir = "--onedir" in sys.argv

    extra: list[str] = []
    if onedir:
        # --onedir desactive l'extraction dans %TEMP% a chaque lancement
        extra += ["--onedir"]

    run(
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--name", "237Boots",
        "--windowed",                    # pas de console
        "--uac-admin",                   # elevation pour l'ecriture disque
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT),
        *extra,
        str(ROOT / "main.py"),
    )

    built = ROOT / "dist" / ("237Boots" if onedir else "237Boots.exe")
    target_dir = ROOT / "dist" / f"237Boots-{VERSION}-win64"
    if target_dir.exists():
        shutil.rmtree(target_dir)
    if onedir:
        shutil.copytree(built, target_dir)
        exe = target_dir / "237Boots.exe"
    else:
        target_dir.mkdir(parents=True)
        exe = target_dir / "237Boots.exe"
        shutil.copy2(built, exe)

    # Le moteur est depose a cote de l'exe : find_engine() le decouvre.
    src = INSTALL / engine_name()
    if src.is_file():
        shutil.copy2(src, target_dir / src.name)
        for extra_exe in ("Ventoy2Disk.exe",):
            alt = INSTALL / extra_exe
            if alt.is_file():
                shutil.copy2(alt, target_dir / alt.name)
    else:
        print(f"!! moteur introuvable : {src}")

    (target_dir / "LISEZ-MOI.txt").write_text(
        "237Boots {v}\n"
        "=================\n\n"
        "1. Clic droit sur 237Boots.exe -> Executer en tant qu'administrateur\n"
        "2. Selectionnez votre cle USB, puis Installer\n"
        "3. Copiez vos fichiers ISO sur la cle. C'est termine.\n\n"
        "Secure Boot :\n"
        "  - Soit vous le desactivez dans les reglages du fabricant\n"
        "  - Soit vous enrolez la cle 237Boots dans MokManager au premier demarrage\n\n"
        "Code source : {repo}\n"
        "Fork de Ventoy (c) longpanda - GPL v3+\n".format(v=VERSION, repo=REPO),
        encoding="utf-8",
    )

    size = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
    print(f"\nPaquetage : {target_dir}")
    print(f"Taille    : {size / (1024 * 1024):.1f} Mo")
    for f in sorted(target_dir.iterdir()):
        print(f"   {f.name:<28} {f.stat().st_size / 1024:8.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
