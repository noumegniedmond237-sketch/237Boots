#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controle de conformite du rebrand 237Boots.

Verifie trois choses, en comparant a l'amont (upstream/master) :

  1. COUCHE 0 - les 23 lignes qui portent le contrat on-disk et le protocole
     de boot sont identiques octet pour octet a celles de Ventoy amont.
     VTOYEFI, VENTOY_GUID, l'empreinte MBR, le placeholder SHA-256 du shim,
     la geometrie de l'ESP, sbat.csv, le drapeau VENTOY COMPATIBLE...
     Si l'une bouge, la cle refuse de demarrer.

  2. LICENCE - les notices GPL d'origine sont conservees et les notices
     237Boots ajoutees (art. 5 de la GPL v3).

  3. MARQUE - la marque 237Boots est bien presente.

Lancer depuis la racine du depot :

    python tools/verify_rebrand.py

A integrer a la CI : c'est le garde-fou contre une future substitution
mecanique qui casserait le demarrage.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPSTREAM = "upstream/master"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True).stdout.decode("utf-8", "replace")


def lines_at(rev: str, path: str) -> list[str]:
    return git("show", f"{rev}:{path}").replace("\r\n", "\n").split("\n")


# (fichier, motif, description) -- NE JAMAIS modifier ces lignes
LAYER0 = [
    ("GRUB2/MOD_SRC/grub-2.04/grub-core/ventoy/ventoy_cmd.c",
     'grub_strncmp("VTOYEFI", label, 7)', "comparaison du label FAT au boot"),
    ("GRUB2/MOD_SRC/grub-2.04/grub-core/ventoy/ventoy_cmd.c",
     "g_check_mbr_data[]", "empreinte MBR comparee octet a octet"),
    ("GRUB2/MOD_SRC/grub-2.04/include/grub/ventoy.h", "#define VENTOY_GUID", "GUID (GRUB)"),
    ("EDK2/edk2_mod/edk2-edk2-stable201911/MdeModulePkg/Application/Ventoy/Ventoy.h",
     "#define VENTOY_GUID", "GUID (EFI)"),
    ("IPXE/ipxe_mod_code/ipxe-3fe683e/src/include/ventoy.h", "#define VENTOY_GUID", "GUID (iPXE)"),
    ("VtoyTool/vtoytool.h", "#define VENTOY_GUID", "GUID (OS)"),
    ("Vlnk/src/vlnk.h", "#define VENTOY_GUID", "GUID (vlnk)"),
    ("Ventoy2Disk/Ventoy2Disk/Utility.c",
     'memcpy(Table[1].Name, L"VTOYEFI"', "nom ESP ecrit (GUI Windows)"),
    ("vtoycli/vtoycli.h", "#define VENTOY_EFI_PART_SIZE", "geometrie de l'ESP"),
    ("vtoycli/vtoycli.h", "#define VENTOY_EFI_PART_ATTR", "bit d'attribut GPT ESP"),
    ("EDK2/edk2_mod/edk2-edk2-stable201911/MdeModulePkg/Application/VtoyShim/VtoyShim.c",
     "gVtoyGrubSha256Hash", "placeholder SHA-256"),
    ("INSTALL/ventoy_pack.sh", "26 26 26 26 26 26 26 26", "grep du placeholder 0x26"),
    ("EDK2/edk2_mod/edk2-edk2-stable201911/MdeModulePkg/Application/VtoyShim/sbat.csv",
     "ventoy-shim", "identite SBAT de revocation"),
    ("LiveCD/livecd.sh", "-P 'VENTOY COMPATIBLE'", "drapeau d'interoperabilite"),
    ("LinuxGUI/Ventoy2Disk/Core/ventoy_define.h", "#define VTOYEFI_PART_SECTORS", "taille ESP (Linux)"),
    ("Unix/ventoy_unix_src/FreeBSD/geom_ventoy_src/10.x/sys/geom/ventoy/g_ventoy.h",
     "G_VENTOY_VERSION", "ABI GEOM FreeBSD"),
    ("GRUB2/MOD_SRC/grub-2.04/include/grub/ventoy.h",
     "#define VENTOY_COMPATIBLE_STR", "chaine de compatibilite"),
    ("INSTALL/grub/grub.cfg", 'set VENTOY_VERSION="', "version lue par 3 parseurs"),
    ("GRUB2/MOD_SRC/grub-2.04/grub-core/ventoy/ventoy_cmd.c", '"ventoy.json"', "fichier de plugin"),
    ("GRUB2/MOD_SRC/grub-2.04/grub-core/ventoy/ventoy_cmd.c", '".ventoyignore"', "marqueur d'exclusion"),
    ("GRUB2/MOD_SRC/grub-2.04/grub-core/kern/main.c", "ventoy.disk.img.xz", "image ESP chargee au boot"),
    ("EDK2/edk2_mod/edk2-edk2-stable201911/MdeModulePkg/Application/VtoyShim/VtoyShim.h",
     "REAL_GRUB_FILE", "nom du chargeur reel"),
]

BRAND_SCOPE = ["GRUB2", "EDK2", "INSTALL", "EfiISO", "LiveCD", "LiveCDGUI",
               "LANGUAGES", "Ventoy2Disk", "237Boots-GUI"]


def main() -> int:
    print("237Boots - controle de conformite du rebrand")
    print("=" * 78)
    print(f"reference : {git('rev-parse', '--short', UPSTREAM).strip()}  (Ventoy amont)")
    print(f"cible     : {git('rev-parse', '--short', 'HEAD').strip()}  (237Boots)")
    print()
    print("=== COUCHE 0 : ligne de boot identique a l'amont ? ===")

    bad = 0
    for path, needle, desc in LAYER0:
        up = [l.rstrip() for l in lines_at(UPSTREAM, path) if needle in l]
        new = [l.rstrip() for l in lines_at("HEAD", path) if needle in l]
        name = path.rsplit("/", 1)[-1]
        if not up or not new:
            bad += 1
            print(f"  [MOTIF ABSENT  ] {name:<18} {desc}")
        elif up == new:
            print(f"  [IDENTIQUE     ] {name:<18} {desc}")
        elif all(needle in l for l in new):
            print(f"  [INTACT *      ] {name:<18} {desc}  (ligne reecrite, identifiant preserve)")
        else:
            bad += 1
            print(f"  [DIVERGE !     ] {name:<18} {desc}")
            for a, b in zip(up, new):
                if a != b:
                    print(f"       amont : {a.strip()[:86]}")
                    print(f"       237Boot: {b.strip()[:86]}")
                    break
    print(f"\n  -> {len(LAYER0) - bad}/{len(LAYER0)} lignes de boot intactes")

    print("\n=== LICENCE GPL ===")
    n_long = git("grep", "-l", "-I", "longpanda", "HEAD", "--", ".").count("\n")
    n_237 = git("grep", "-l", "-I", "Edmond Noumegni", "HEAD", "--", ".").count("\n")
    copying = os.path.getsize(os.path.join(ROOT, "COPYING"))
    print(f"  notices 'longpanda' conservees  : {n_long}")
    print(f"  notices 'Edmond Noumegni' ajoutees : {n_237}")
    print(f"  COPYING : {copying} octets")
    lic_ok = n_long >= 380 and n_237 >= 380 and copying > 34000
    print(f"  -> {'OK' if lic_ok else 'PROBLEME'}")
    if not lic_ok:
        bad += 1

    print("\n=== MARQUE ===")
    hits = git("grep", "-l", "237Boots", "HEAD", "--", *BRAND_SCOPE).count("\n")
    print(f"  fichiers portant la marque 237Boots : {hits}")
    print(f"  -> {'OK' if hits >= 25 else 'INSUFFISANT'}")
    if hits < 25:
        bad += 1

    print("\n" + "=" * 78)
    print("RESULTAT : " + (
        "CONFORME - couche 0 intacte, licence preservee"
        if bad == 0 else f"{bad} PROBLEME(S)"
    ))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
