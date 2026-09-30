<h1 align="center">237Boots</h1>

<p align="center">
  <b>Version camerounaise de Ventoy</b><br/>
  <a href="https://github.com/noumegniedmond237-sketch/237Boots">github.com/noumegniedmond237-sketch/237Boots</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/noumegniedmond237-sketch/237Boots?style=for-the-badge">
  <img src="https://img.shields.io/github/stars/noumegniedmond237-sketch/237Boots?style=for-the-badge">
  <img src="https://img.shields.io/github/actions/workflow/status/noumegniedmond237-sketch/237Boots/ci.yml?label=build&logo=github&style=for-the-badge">
</p>

> [!IMPORTANT]
> **237Boots est un fork de <a href="https://github.com/ventoy/Ventoy">Ventoy</a>.**
> Ventoy est l creations de **longpanda** et est distribue sous licence **GPL v3+**.
> 237Boots redistribue ce travail sous la meme licence. Toutes les mentions de
> copyright d'origine (longpanda, Free Software Foundation, iPXE, exFAT, 7-Zip,
> FreeBSD, etc.) sont **conservees intactes** dans le code, conformement a
> l'article 5 de la GPL.
> Si vous cherchez le projet original : <a href="https://github.com/ventoy/Ventoy">ventoy/Ventoy</a>.

---

## 🇫🇷 Français

### Qu'est-ce que 237Boots ?

237Boots est un outil **libre** pour creer des cles USB amorcables a partir de
fichiers **ISO / WIM / IMG / VHD(x) / EFI**.

Avec 237Boots, vous ne reformatez plus la cle a chaque fois : **copiez** vos
images sur la cle et demarrez. Vous pouvez copier plusieurs images a la fois,
237Boots affiche un **menu de demarrage** pour choisir laquelle lancer.

- Amorce : BIOS x86, UEFI IA32, UEFI x86_64, UEFI ARM64, UEFI MIPS64EL
- Styles de partition : **MBR** et **GPT**
- Plus de 1300 images ISO testees, 90 %+ des distributions de distrowatch.com

### Ce que cette version ajoute (edition camerounaise)

| Ajout | Detail |
|---|---|
| **Interface graphique PyQt6** | `237Boots.exe`, fenetre native en **francais**, pilote le moteur via l'interface `VTOYCLI`. Aucun compilateur C requis. |
| **Interface en francais** | Documentation, README et messages de l'interface traduits. |
| **Parametre regional** | `fr_CM` (francais - Cameroun) et `en_CM` (anglais - Cameroun) dans le selecteur de langue. |
| **Cle USB preconfiguree** | `ventoy.json` par defaut (theme, menu) et lot d'ISO recommande pour le Cameroun. |
| **Secure Boot 237Boots** | Cle de signature propre, avec guide d'enrolement MokManager. |

### Installation rapide

1. Telechargez l'archive `237boots-*-windows*.zip` depuis
   <a href="https://github.com/noumegniedmond237-sketch/237Boots/releases">https://github.com/noumegniedmond237-sketch/237Boots/releases</a> et decompressez-la.
2. Lancez **`237Boots.exe`** (clic droit -> *Executer en tant qu'administrateur*).
3. Selectez votre cle USB, cliquez sur **Installer**.
4. Copiez vos fichiers ISO sur la cle. C'est tout.

### Secure Boot

Si votre PC demarre avec **Secure Boot active**, deux options :

- **Desactiver Secure Boot** (reglages du fabricant) — le plus simple.
- **Enroler la cle 237Boots** dans MokManager au premier demarrage, avec le
  fichier `ENROLL_THIS_KEY_IN_MOKMANAGER.cer` livre dans l'archive.
  Voir <a href="https://github.com/noumegniedmond237-sketch/237Boots/blob/237boots/DOC/SECUREBOOT_237BOOTS.md">le guide</a>.

### Documentation

La documentation technique complete (theme, plugins, persistence, injection,
auto-installation, layout disque) est celle de Ventoy, encore valable :
<https://www.ventoy.net/en/doc_start.html>

---

## 🇬🇧 English

### What is 237Boots?

237Boots is an **open source** tool to create bootable USB drives from
**ISO / WIM / IMG / VHD(x) / EFI** files.

With 237Boots you don't need to format the drive over and over: just **copy**
your images onto it and boot. You can copy many images at a time and 237Boots
gives you a **boot menu** to choose which one to launch.

- Boot: x86 Legacy BIOS, IA32 UEFI, x86_64 UEFI, ARM64 UEFI, MIPS64EL UEFI
- Partition style: both **MBR** and **GPT**
- 1300+ tested ISO images, 90%+ of distrowatch.com distributions supported

### What this edition adds (Cameroon edition)

| Addition | Detail |
|---|---|
| **PyQt6 GUI** | `237Boots.exe`, native **French** window driving the engine through the `VTOYCLI` interface. No C compiler required. |
| **French interface & docs** | README and UI messages translated. |
| **Regional locale** | `fr_CM` (French - Cameroon) and `en_CM` (English - Cameroon) in the language selector. |
| **Preconfigured stick** | Default `ventoy.json` (theme, menu) and a curated ISO bundle for Cameroon. |
| **237Boots Secure Boot** | Own signing key, with a MokManager enrolment guide. |

### Quick start

1. Download `237boots-*-windows*.zip` from
   <a href="https://github.com/noumegniedmond237-sketch/237Boots/releases">https://github.com/noumegniedmond237-sketch/237Boots/releases</a> and extract it.
2. Run **`237Boots.exe`** (right-click -> *Run as administrator*).
3. Pick your USB drive and click **Install**.
4. Copy your ISO files onto the drive. That's it.

### Tested OS

**Windows**
Windows 7, Windows 8, Windows 8.1, Windows 10, Windows 11, Windows Server 2012, Windows Server 2012 R2, Windows Server 2016, Windows Server 2019, Windows Server 2022, Windows Server 2025, WinPE

**Linux**
Debian, Ubuntu, CentOS(6/7/8/9/10), RHEL(6/7/8/9/10), Deepin, Fedora, Rocky Linux, AlmaLinux, EuroLinux(6/7/8/9), openEuler, OpenAnolis, SLES, openSUSE, MX Linux, Manjaro, Linux Mint, Endless OS, Elementary OS, Solus, Linx, Zorin, antiX, PClinuxOS, Arch, ArcoLinux, ArchLabs, BlackArch, Obarun, Artix Linux, Puppy Linux, Tails, Slax, Kali, Mageia, Slackware, Q4OS, Archman, Gentoo, Pentoo, NixOS, Kylin, openKylin, Ubuntu Kylin, KylinSec, Lubuntu, Xubuntu, Kubuntu, Ubuntu MATE, Ubuntu Budgie, Ubuntu Studio, Bluestar, OpenMandriva, ExTiX, Netrunner, ALT Linux, Nitrux, Peppermint, KDE neon, Linux Lite, Parrot OS, Qubes, Pop OS, ROSA, Void Linux, Star Linux, EndeavourOS, MakuluLinux, Voyager, Feren, ArchBang, LXLE, Knoppix, Calculate Linux, Clear Linux, Pure OS, Oracle Linux, Trident, Septor, Porteus, Devuan, GoboLinux, 4MLinux, Simplicity Linux, Zeroshell, Android-x86, netboot.xyz, Slitaz, SuperGrub2Disk, Proxmox VE, Kaspersky Rescue, SystemRescueCD, MemTest86, MemTest86+, MiniTool Partition Wizard, Parted Magic, veket, Sabayon, Scientific, alpine, ClearOS, CloneZilla, Berry Linux, Trisquel, Ataraxia Linux, Minimal Linux Live, BackBox Linux, Emmabuntüs, ESET SysRescue Live,Nova Linux, AV Linux, RoboLinux, NuTyX, IPFire, SELKS, ZStack, Enso Linux, Security Onion, Network Security Toolkit, Absolute Linux, TinyCore, Springdale Linux, Frost Linux, Shark Linux, LinuxFX, Snail Linux, Astra Linux, Namib Linux, Resilient Linux, Virage Linux, Blackweb Security OS, R-DriveImage, O-O.DiskImage, Macrium, ToOpPy LINUX, GNU Guix, YunoHost, foxclone, siduction, Adelie Linux, Elive, Pardus, CDlinux, AcademiX, Austrumi, Zenwalk, Anarchy, DuZeru, BigLinux, OpenMediaVault, Ubuntu DP, Exe GNU/Linux, 3CX Phone System, KANOTIX, Grml, Karoshi, PrimTux, ArchStrike, CAELinux, Cucumber, Fatdog, ForLEx, Hanthana, Kwort, MiniNo, Redcore, Runtu, Asianux, Clu Linux Live, Uruk, OB2D, BlueOnyx, Finnix, HamoniKR, Parabola, LinHES, LinuxConsole, BEE free, Untangle, Pearl, Thinstation, TurnKey, tuxtrans, Neptune, HefftorLinux, GeckoLinux, Mabox Linux, Zentyal, Maui, Reborn OS, SereneLinux , SkyWave Linux, Kaisen Linux, Regata OS, TROM-Jaro, DRBL Linux, Chalet OS, Chapeau, Desa OS, BlankOn, OpenMamba, Frugalware, Kibojoe Linux, Revenge OS, Tsurugi Linux, Drauger OS, Hash Linux, gNewSense, Ikki Boot, SteamOS, Hyperbola, VyOS, EasyNAS, SuperGamer, Live Raizo, Swift Linux, RebeccaBlackOS, Daphile, CRUX, Univention, Ufficio Zero, Rescuezilla, Phoenix OS, Garuda Linux, Mll, NethServer, OSGeoLive, Easy OS, Volumio, FreedomBox, paldo, UBOS, Recalbox, batocera, Lakka, LibreELEC, Pardus Topluluk, Pinguy, KolibriOS, Elastix, Arya, Omoikane, Omarine, Endian Firewall, Hamara, Rocks Cluster, MorpheusArch, Redo, Slackel, SME Server, APODIO, Smoothwall, Dragora, Linspire, Secure-K OS, Peach OSI, Photon, Plamo, SuperX, Bicom, Ploplinux, HP SPP, LliureX, Freespire, DietPi, BOSS, Webconverger, Lunar, TENS, Source Mage, RancherOS, T2, Vine, Pisi, blackPanther, mAid, Acronis, Active.Boot, AOMEI, Boot.Repair, CAINE, DaRT, EasyUEFI, R-Drive, PrimeOS, Avira Rescue System, bitdefender, Checkra1n Linux, Lenovo Diagnostics, Clover, Bliss-OS, Lenovo BIOS Update, Arcabit Rescue Disk, MiyoLinux, TeLOS, Kerio Control, RED OS, OpenWrt, MocaccinoOS, EasyStartup, Pyabr, Refracta, Eset SysRescue, Linpack Xtreme, Archcraft, NHVBOOT, pearOS, SeaTools, Easy Recovery Essentional, iKuai, StorageCraft SCRE, ZFSBootMenu, TROMjaro, BunsenLabs, Todo en Uno, ChallengerOS, Nobara, Holo, CachyOS, Peux OS, Vanilla OS, ShredOS, paladin, Palen1x, dban, ReviOS, HelenOS, XeroLinux, Tiny 11, chimera linux, CuteFish, DragonOs, Rhino Linux, vanilladpup, crystal, IGELOS, MiniOS, gnoppix, PikaOS, UwUntu, Noble, PocketHandyBox, DiskGenius, Commodore, Talos, Shebang Linux, hrmpf, Bazzite, ManualLinux, nyarchlinux, ultramarine, TempleOS, bluefin, Damn Small Linux, Kicksecure, SerentiyOS, AerynOS, ......

**Unix**
DragonFly, FreeBSD, pfSense, OPNsense, GhostBSD, FreeNAS, TrueNAS, XigmaNAS, FuryBSD, HardenedBSD, MidnightBSD, ClonOS, EmergencyBootKit, helloSystem

**ChromeOS**
FydeOS, CloudReady, ChromeOS Flex, ThoriumOS

**Other**
VMware ESXi, Citrix XenServer, Xen XCP-ng

---

## Build from source

The Linux/UEFI boot payload is built with the upstream toolchain in a Linux
container:

```bash
docker compose up
```

The Windows GUI (`237Boots.exe`) is a PyQt6 application:

```bash
pip install PyQt6 pyinstaller
python 237Boots-GUI/main.py
```

See [DOC/BuildVentoyFromSource.txt](DOC/BuildVentoyFromSource.txt) for the
detailed toolchain documentation.

## Licence

**GPL v3+** — inherited from Ventoy. See [COPYING](COPYING).

```
Copyright (c) 2020-2026, longpanda <admin@ventoy.net>   (original Ventoy)
Copyright (c) 2026, Edmond Noumegni                      (237Boots changes)
```

The upstream author's copyright notices are preserved in every source file as
required by GPL-3.0 section 5. 237Boots changes are additive.

## Credits

- **Ventoy** by [longpanda](https://github.com/ventoy) — the original project.
  Without it, 237Boots would not exist.
- [DistroWatch](https://distrowatch.com/) and the Ventoy ISO test list.
- Author of 237Boots: **Edmond Noumegni** — <a href="https://portfolio-nine-jade-22.vercel.app/">https://portfolio-nine-jade-22.vercel.app/</a>

## Links

| | |
|---|---|
| Source & issues | <a href="https://github.com/noumegniedmond237-sketch/237Boots">github.com/noumegniedmond237-sketch/237Boots</a> |
| Releases | <a href="https://github.com/noumegniedmond237-sketch/237Boots/releases">Releases</a> |
| Upstream project | <a href="https://github.com/ventoy/Ventoy">ventoy/Ventoy</a> |
| Upstream website | <a href="https://www.ventoy.net">ventoy.net</a> |
