# -*- coding: utf-8 -*-
"""Fenetre principale de 237Boots."""

from __future__ import annotations

import ctypes
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy, QSplitter, QStatusBar,
    QVBoxLayout, QWidget,
)

from . import i18n
from .drives import Disk, human_size, list_disks
from .engine import Engine, EngineError, find_engine, missing_payload

VERSION = "1.1.17-CM1"
REPO = "https://github.com/noumegniedmond237-sketch/237Boots"
DOCS = "https://www.ventoy.net/en/doc_start.html"
PORTFOLIO = "https://portfolio-nine-jade-22.vercel.app/"


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


class DiskCard(QFrame):
    """Carte cliquable representant un disque physique."""

    def __init__(self, disk: Disk, parent=None):
        super().__init__(parent)
        self.disk = disk
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(96)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(3)

        head = QHBoxLayout()
        head.setSpacing(8)
        self._radio = QRadioButton(i18n.t("disk", index=disk.index))
        self._radio.setEnabled(not disk.is_system)
        head.addWidget(self._radio)
        self._size = QLabel(human_size(disk.size_bytes))
        self._size.setObjectName("Dim")
        head.addStretch()
        head.addWidget(self._size)
        lay.addLayout(head)

        self._model = QLabel(disk.model or i18n.t("generic_model"))
        self._model.setStyleSheet("color:#8b93a1;")
        lay.addWidget(self._model)

        tags = []
        if disk.part_scheme:
            tags.append(disk.part_scheme)
        tags.append(disk.bus_label)
        if disk.has_boots_esp:
            tags.append(i18n.t("boots_installed"))
        if disk.is_external:
            tags.append(i18n.t("external"))
        if disk.is_system:
            tags.append(i18n.t("system_disk"))
        meta = QLabel("  ·  ".join(tags))
        meta.setObjectName("Dim")
        lay.addWidget(meta)

        if disk.is_system:
            self._model.setStyleSheet(f"color:#8b93a1; font-style:italic;")

    def set_checked(self, on: bool) -> None:
        self._radio.setChecked(on)

    def is_checked(self) -> bool:
        return self._radio.isChecked()

    def mousePressEvent(self, event):
        if not self.disk.is_system:
            self._radio.setChecked(True)
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = Engine(self)
        self.engine.progress.connect(self._on_progress)
        self.engine.log.connect(self._on_log)
        self.engine.finished.connect(self._on_finished)

        self._disks: list[Disk] = []
        self._cards: list[DiskCard] = []
        self._lang_value = i18n.DEFAULT

        self.setMinimumSize(940, 760)
        self.setWindowTitle("237Boots")
        self._build_ui()
        self._apply_style()
        self.refresh()

    def _retranslate(self) -> None:
        """Reconstruit l'interface pour la locale courante.

        Les libelles statiques (titres, boutons, menus, barre d'etat) sont
        figes a la construction : sans reconstruction, changer de langue ne
        mettrait a jour que les cartes de disques.
        """
        wanted = self._lang.currentData() if hasattr(self, "_lang") else i18n.DEFAULT

        old = self.centralWidget()
        if old is not None:
            old.setParent(None)
            old.deleteLater()
        self.menuBar().clear()
        self.setStatusBar(QStatusBar())

        self._lang_value = wanted
        self._build_ui()

        idx = self._lang.findData(wanted)
        if idx >= 0:
            self._lang.blockSignals(True)
            self._lang.setCurrentIndex(idx)
            self._lang.blockSignals(False)
        self.refresh()

    @staticmethod
    def _card(title: str) -> tuple[QFrame, QVBoxLayout, QHBoxLayout]:
        """Bloc titre + contenu. Evite QGroupBox, dont le titre rogne les
        libelles des radio/checkbox (subcontrol-origin + margin-top).

        Retourne aussi la ligne d'en-tete pour y loger un bouton, ce qui evite
        d'ajouter une rangee de hauteur dans la colonne droite.
        """
        frame = QFrame()
        frame.setObjectName("Card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 11)
        lay.setSpacing(6)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(8)
        label = QLabel(title)
        label.setObjectName("CardTitle")
        head.addWidget(label)
        head.addStretch()
        lay.addLayout(head)
        return frame, lay, head

    # -- Construction ------------------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 16, 18, 12)
        outer.setSpacing(12)

        # En-tete
        head = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(0)
        title = QLabel("237Boots")
        title.setObjectName("Title")
        self._subtitle = QLabel(i18n.t("app_subtitle"))
        self._subtitle.setObjectName("Subtitle")
        titles.addWidget(title)
        titles.addWidget(self._subtitle)
        head.addLayout(titles)
        head.addStretch()

        self._lang = QComboBox()
        self._lang.addItem("Francais (CM)", "fr_CM")
        self._lang.addItem("English (CM)", "en_CM")
        idx = self._lang.findData(self._lang_value)
        if idx >= 0:
            self._lang.setCurrentIndex(idx)
        self._lang.currentIndexChanged.connect(self._on_language)
        head.addWidget(QLabel(i18n.t("lang")))
        head.addWidget(self._lang)
        outer.addLayout(head)

        if not is_admin():
            warn = QLabel(i18n.t("admin_warning"))
            warn.setObjectName("Warn")
            outer.addWidget(warn)

        # Etat du moteur : l'executable seul ne suffit pas, le payload de
        # boot (boot.img, core.img.xz, ventoy.disk.img.xz) est obligatoire.
        self._engine_note: QLabel | None = None
        exe = find_engine()
        if exe is None:
            note = QLabel(i18n.t("engine_missing"))
            note.setObjectName("Warn")
        else:
            absent = missing_payload(exe.parent)
            if absent:
                note = QLabel(
                    i18n.t("payload_missing", files=", ".join(absent))
                )
                note.setObjectName("Warn")
                note.setWordWrap(True)
            else:
                note = None
        if note is not None:
            self._engine_note = note
            outer.addWidget(note)

        # Corps
        split = QSplitter(Qt.Orientation.Horizontal)

        # -- colonne disques
        left, lv, _ = self._card(i18n.t("devices"))
        self._refresh = QPushButton(i18n.t("refresh"))
        self._refresh.clicked.connect(self.refresh)
        lv.addWidget(self._refresh)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        # Les cartes s'adaptent a la largeur : pas de barre horizontale.
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        holder = QWidget()
        self._cards_layout = QVBoxLayout(holder)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._cards_layout.setSpacing(8)
        self._scroll.setWidget(holder)
        lv.addWidget(self._scroll)

        self._empty = QLabel(i18n.t("no_device"))
        self._empty.setObjectName("Dim")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cards_layout.addWidget(self._empty)
        lv.addStretch()
        split.addWidget(left)

        # -- colonne droite
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(12)

        opts, ov, _ = self._card(i18n.t("options"))

        # La colonne droite est sur-contrainte : sans politique verticale
        # "fixed", Qt compresse les radio/checkbox a ~12 px et rogne leurs
        # libelles (taille observee 12 contre un sizeHint de 25).
        def rigid(*widgets):
            for wd in widgets:
                wd.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        ov.setSpacing(8)
        self._gpt = QRadioButton(i18n.t("gpt"))
        self._mbr = QRadioButton(i18n.t("mbr"))
        self._style_group = QButtonGroup(self)
        self._style_group.addButton(self._gpt)
        self._style_group.addButton(self._mbr)
        self._gpt.setChecked(True)
        rigid(self._gpt, self._mbr)
        ov.addWidget(QLabel(i18n.t("partition_style")))
        ov.addWidget(self._gpt)
        ov.addWidget(self._mbr)

        self._sb = QCheckBox(i18n.t("secure_boot"))
        self._sb.setChecked(True)
        ov.addWidget(self._sb)
        hint = QLabel(i18n.t("secure_boot_hint"))
        hint.setObjectName("Dim")
        hint.setWordWrap(True)
        ov.addWidget(hint)

        self._nousb = QCheckBox(i18n.t("ignore_usb_check"))
        ov.addWidget(self._nousb)
        rigid(self._sb, self._nousb)
        rv.addWidget(opts)

        acts, av, _ = self._card(i18n.t("actions"))
        self._install = QPushButton(i18n.t("install"))
        self._install.setObjectName("Primary")
        self._install.clicked.connect(lambda: self._run("install"))
        self._update = QPushButton(i18n.t("update"))
        self._update.clicked.connect(lambda: self._run("update"))
        self._erase = QPushButton(i18n.t("erase"))
        self._erase.setObjectName("Danger")
        self._erase.clicked.connect(self._erase_disk)
        for b in (self._install, self._update, self._erase):
            av.addWidget(b)
        rv.addWidget(acts)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        rv.addWidget(self._bar)

        logbox, lv2, lhead = self._card(i18n.t("log"))
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(70)
        lv2.addWidget(self._log, 1)
        clr = QPushButton(i18n.t("clear_log"))
        clr.setObjectName("Small")
        clr.setFixedHeight(26)
        clr.clicked.connect(self._log.clear)
        lhead.addWidget(clr)
        rv.addWidget(logbox, 1)

        split.addWidget(right)
        split.setStretchFactor(0, 5)
        split.setStretchFactor(1, 6)
        outer.addWidget(split, 1)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(i18n.t("ready"))

        menubar = self.menuBar()
        m_about = menubar.addMenu(i18n.t("about"))
        m_about.addAction(i18n.t("docs"), lambda: webbrowser.open(DOCS))
        m_about.addAction(i18n.t("github"), lambda: webbrowser.open(REPO))
        m_about.addSeparator()
        m_about.addAction(i18n.t("about"), self._show_about)
        m_about.addAction(i18n.t("close"), self.close)

    def _apply_style(self) -> None:
        from .theme import QSS
        QApplication.instance().setStyleSheet(QSS)

    # -- Disques -----------------------------------------------------------

    def refresh(self) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()
        self._disks = list_disks()
        self._empty.setVisible(not self._disks)
        for d in self._disks:
            card = DiskCard(d)
            card._radio.toggled.connect(self._sync_buttons)
            self._cards_layout.addWidget(card)
            self._cards.append(card)
        if self._disks:
            first = next((c for c in self._cards if not c.disk.is_system), self._cards[0])
            first.set_checked(True)
        self._sync_buttons()

    def _selected(self) -> Disk | None:
        for c in self._cards:
            if c.is_checked():
                return c.disk
        return None

    def _sync_buttons(self) -> None:
        d = self._selected()
        busy = self.engine.running
        self._install.setEnabled(bool(d) and not busy)
        self._update.setEnabled(bool(d and d.has_boots_esp) and not busy)
        self._erase.setEnabled(bool(d) and not busy)
        self._refresh.setEnabled(not busy)
        self._gpt.setEnabled(not busy)
        self._mbr.setEnabled(not busy)
        self._sb.setEnabled(not busy)
        self._nousb.setEnabled(not busy)

    # -- Actions -----------------------------------------------------------

    def _run(self, op: str) -> None:
        disk = self._selected()
        if disk is None:
            QMessageBox.information(self, i18n.t("app_title"), i18n.t("no_selection"))
            return
        if not is_admin():
            QMessageBox.critical(
                self, i18n.t("app_title"), i18n.t("admin_warning")
            )
            return

        name = f"{disk.index} ({disk.model or i18n.t('generic_model')})"
        if op == "install":
            text = i18n.t("confirm_install", name=name).strip()
        else:
            text = i18n.t("confirm_erase", name=name)
        box = QMessageBox(self)
        box.setWindowTitle(i18n.t("confirm_title"))
        box.setText(text)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return

        if find_engine() is None:
            QMessageBox.critical(self, i18n.t("app_title"), i18n.t("engine_missing"))
            return

        self._bar.setValue(0)
        self.statusBar().showMessage(i18n.t("working"))
        self._sync_buttons()
        try:
            if op == "install":
                self.engine.install(
                    disk.index,
                    gpt=self._gpt.isChecked(),
                    secure_boot=self._sb.isChecked(),
                    force=self._nousb.isChecked(),
                )
            else:
                self.engine.update(disk.index, force=self._nousb.isChecked())
        except EngineError as exc:
            QMessageBox.critical(self, i18n.t("app_title"), str(exc))
            self._sync_buttons()

    def _erase_disk(self) -> None:
        # Ventoy2Disk n'expose pas d'operation de nettoyage via VTOYCLI :
        # l'effacement passe par la desinstallation (/U sur un support deja
        # installe laisse les donnees). On ne simule donc rien ici.
        QMessageBox.information(
            self, i18n.t("app_title"),
            "L'effacement complet n'est pas expose par l'interface VTOYCLI.\n"
            "Reformatez la cle depuis l'Explorateur Windows."
            if i18n.get_locale() == "fr_CM" else
            "Full erase is not exposed by the VTOYCLI interface.\n"
            "Format the drive from Windows Explorer instead.",
        )

    def _on_progress(self, value: int) -> None:
        self._bar.setValue(value)

    def _on_log(self, line: str) -> None:
        self._log.appendPlainText(line)

    def _on_finished(self, ok: bool, message: str) -> None:
        self._log.appendPlainText("")
        self._log.appendPlainText(("[OK] " if ok else "[!!] ") + message)
        self.statusBar().showMessage(
            f"{i18n.t('done')} - {message}" if ok else f"{i18n.t('failed')} - {message}"
        )
        self.refresh()
        if ok:
            QMessageBox.information(self, i18n.t("app_title"), message)

    # -- Langue / apropos --------------------------------------------------

    def _on_language(self) -> None:
        i18n.set_locale(self._lang.currentData())
        self._retranslate()

    def _show_about(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(i18n.t("about"))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(i18n.t("about_text", version=VERSION))
        box.exec()
