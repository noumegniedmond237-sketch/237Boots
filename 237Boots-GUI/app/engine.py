# -*- coding: utf-8 -*-
"""Pilotage du moteur d'installation via l'interface VTOYCLI.

Interface exposee par Ventoy2Disk (Ventoy2Disk/Ventoy2Disk/ventoy_cli.c:458) :

    Ventoy2Disk.exe VTOYCLI  { /I | /U }  { /Drive:F: | /PhyDrive:1 }
                            /GPT  /NoSB  /R:4096  /NoUSBCheck

Points de vigilance :
  * Le moteur ecrit cli_percent.txt / cli_done.txt / log.txt dans son
    repertoire courant : le QProcess DOIT pointer dessus, sinon la jauge
    reste bloquee a 0 %.
  * L'operation bloque plusieurs minutes : on passe par QProcess (asynchrone)
    et jamais par subprocess.run depuis le thread graphique.
  * L'executable embarque n'est pas toujours le bon : INSTALL/Ventoy2Disk.exe
    est en x86 (machine 0x014C) alors qu'une variante _X64 existe.
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal

# Constantes de fichier lues par le moteur (Ventoy2Disk/Ventoy2Disk/Ventoy2Disk.h)
CLI_PERCENT = "cli_percent.txt"
CLI_DONE = "cli_done.txt"
LOG_FILE = "log.txt"

# Magic argv[1] qui bascule le binaire en mode CLI silencieux
CLI_MAGIC = "VTOYCLI"

# Payload que le moteur charge au demarrage. Ces trois fichiers ne sont PAS
# dans l'arborescence des sources : ils sont produits par INSTALL/ventoy_pack.sh
# au moment du paquetage. Sans eux, le moteur sort avec le code 1168
# (ERROR_NOT_FOUND) sans message exploitable.
REQUIRED_PAYLOAD = (
    Path("boot") / "boot.img",
    Path("boot") / "core.img.xz",
    Path("ventoy") / "ventoy.disk.img.xz",
)


def missing_payload(base: Path) -> list[str]:
    """Liste les fichiers de payload absents du repertoire `base`."""
    return [str(p).replace("\\", "/") for p in REQUIRED_PAYLOAD if not (base / p).is_file()]


def _resource_dir() -> Path:
    """Repertoire des fichiers embarques (PyInstaller ou execution depuis les sources)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def find_engine() -> Path | None:
    """Retrouve le moteur, en privilegiant un candidat au payload complet.

    Le moteur doit se trouver dans le repertoire qui contient boot/ et ventoy/ :
    il y lit boot\\boot.img et ventoy\\ventoy.disk.img.xz relativement a son
    repertoire courant. Les binaires de l'archive `altexe/` en sont exprimes
    loin et ne fonctionnent pas (FOR_X64_ARM.txt demande explicitement de les
    copier a la racine), donc on les ecarte.
    """
    here = _resource_dir()
    roots = [
        here,                              # exe a cote de Ventoy2Disk.exe
        here / "INSTALL",
        Path(sys.executable).parent,
        here.parent / "INSTALL",           # developpement depuis l'arborescence
    ]
    machine = platform.machine().lower()
    suffix = {
        "amd64": "_X64", "x86_64": "_X64", "x64": "_X64",
        "arm64": "_ARM64", "aarch64": "_ARM64",
        "x86": "", "i386": "", "i686": "",
    }.get(machine)

    # Le binaire x86 par defaut est en 32 bits (PE machine 0x014C) : sur un
    # hote 64 bits on tente d'abord la variante _X64.
    if suffix:
        names = [f"Ventoy2Disk{suffix}.exe"] if suffix else [
            "Ventoy2Disk_X64.exe", "Ventoy2Disk.exe"
        ]
    else:
        names = ["Ventoy2Disk.exe"]

    # Passe 1 : candidats dont le payload est complet.
    for want_complete in (True, False):
        for root in roots:
            for name in names:
                candidate = root / name
                if not candidate.is_file():
                    continue
                if (not missing_payload(candidate.parent)) == want_complete:
                    return candidate
    return None


class EngineError(RuntimeError):
    pass


class Engine(QObject):
    """Wrapper asynchrone autour de Ventoy2Disk.exe VTOYCLI."""

    progress = pyqtSignal(int)          # 0..100
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)    # succes, message

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._proc: QProcess | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._poll)
        self._exit_code = 1
        self._stderr = ""
        self.progress_value = 0

    # -- API ---------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._proc is not None and self._proc.state() != QProcess.ProcessState.NotRunning

    def install(self, index: int, gpt: bool, secure_boot: bool, force: bool = False) -> None:
        self._start("/I", index, gpt, secure_boot, force)

    def update(self, index: int, force: bool = False) -> None:
        self._start("/U", index, gpt=True, secure_boot=False, force=force)

    # -- Interne -----------------------------------------------------------

    def _start(self, op: str, index: int, gpt: bool, secure_boot: bool, force: bool) -> None:
        if self.running:
            raise EngineError("Une operation est deja en cours.")

        exe = find_engine()
        if exe is None:
            raise EngineError(
                "Moteur introuvable (Ventoy2Disk.exe). Placez-le a cote de "
                "237Boots.exe, ou dans le dossier INSTALL/ du paquetage."
            )

        # Verifie la presence du payload AVANT de lancer : sans lui le moteur
        # echoue silencieusement avec le code 1168.
        absent = missing_payload(exe.parent)
        if absent:
            raise EngineError(
                "Paquetage incomplet : fichier(s) manquant(s) a cote du moteur : "
                + ", ".join(absent)
                + ". Utilisez l'archive de release complete, pas l'arborescence des sources."
            )

        args = [CLI_MAGIC, op, f"/PhyDrive:{index}"]
        args.append("/GPT" if gpt else "/MBR")
        if not secure_boot:
            args.append("/NoSB")
        if force:
            args.append("/NoUSBCheck")

        self.log.emit(f"$ {exe.name} {' '.join(args)}")
        self.progress.emit(0)

        # Le moteur ecrit ses fichiers de suivi dans le repertoire courant.
        workdir = str(exe.parent)
        for name in (CLI_PERCENT, CLI_DONE, LOG_FILE):
            try:
                (Path(workdir) / name).unlink(missing_ok=True)
            except OSError:
                pass

        self._stderr = ""
        self._exit_code = 1
        self._proc = QProcess(self)
        self._proc.setWorkingDirectory(workdir)
        self._proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._drain)
        self._proc.errorOccurred.connect(self._on_error)
        self._proc.finished.connect(self._on_finished)
        self._proc.start(str(exe), args)
        self._timer.start()

    def _drain(self) -> None:
        if self._proc is None:
            return
        data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        for line in data.splitlines():
            if line.strip():
                self.log.emit(line.rstrip())

    def _on_error(self, _err) -> None:
        if self._proc is not None and self._proc.error() == QProcess.ProcessError.FailedToStart:
            self.finished.emit(False, "Impossible de lancer le moteur d'installation.")

    def _on_finished(self, code: int, _status) -> None:
        self._timer.stop()
        self._exit_code = code
        self._flush_log_tail()
        ok, message = self._interpret(code)
        self.progress.emit(100 if ok else self.progress_value)
        self.finished.emit(ok, message)
        self._proc = None

    def _poll(self) -> None:
        if self._proc is None:
            return
        base = Path(self._proc.workingDirectory())
        try:
            raw = (base / CLI_PERCENT).read_text(encoding="utf-8", errors="ignore").strip()
            if raw:
                self.progress_value = max(0, min(100, int(float(raw.split()[0]))))
                self.progress.emit(self.progress_value)
        except (OSError, ValueError, IndexError):
            pass

    def _flush_log_tail(self) -> None:
        if self._proc is None:
            return
        try:
            text = (Path(self._proc.workingDirectory()) / LOG_FILE).read_text(
                encoding="utf-8", errors="ignore"
            )
        except OSError:
            return
        for line in text.splitlines()[-25:]:
            if line.strip():
                self.log.emit(line.rstrip())

    def _interpret(self, code: int) -> tuple[bool, str]:
        done = ""
        if self._proc is not None:
            try:
                done = (
                    Path(self._proc.workingDirectory()) / CLI_DONE
                ).read_text(encoding="utf-8", errors="ignore").strip()
            except OSError:
                done = ""
        if code == 0 and done == "0":
            return True, "Operation terminee avec succes."
        if code == 0 and not done:
            return True, "Operation terminee."
        if code == 1168:
            # ERROR_NOT_FOUND : payload absent (voir REQUIRED_PAYLOAD)
            return False, (
                "Le moteur n'a pas trouve son payload (boot.img / core.img.xz / "
                "ventoy.disk.img.xz). Reessayez avec l'archive de release complete."
            )
        if done == "1":
            return False, "Echec de l'operation. Consultez le journal ci-dessous."
        return False, f"Le moteur s'est arrete avec le code {code}."
