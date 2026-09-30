# -*- coding: utf-8 -*-
"""Enumeration physique des disques sous Windows.

Aucune dependance externe : on interroge SetupAPI et les IOCTL de stockage
directement via ctypes. Le moteur (/PhyDrive:N) attend exactement cet index
physique, et les device paths renvoyes par SetupAPI sont de la forme
``\\\\?\\PHYSICALDRIVE0`` - l'index est donc directement exploitable.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------

# ctypes.wintypes n'expose pas HDEVINFO : c'est un simple HANDLE.
HDEVINFO = wintypes.HANDLE

INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3

DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010

IOCTL_STORAGE_GET_HOTPLUG_INFO = 0x002D0C14
IOCTL_STORAGE_QUERY_PROPERTY = 0x002D1400
IOCTL_STORAGE_GET_DEVICE_NUMBER = 0x002D1080
IOCTL_DISK_GET_LENGTH_INFO = 0x0007405C

StorageDeviceProperty = 0
StorageAdapterProperty = 1
PropertyStandardQuery = 0

FILE_DEVICE_UNKNOWN = 0x00000022
FILE_DEVICE_DISK = 0x00000007
FILE_DEVICE_CD_ROM = 0x00000005

BusType_USB = 0x07
BusType_1394 = 0x08
BusType_SATA = 0x0B
BusType_NVME = 0x11
BusType_SD = 0x0C
BusType_MMC = 0x0D

BUS_LABELS = {
    BusType_USB: "USB",
    BusType_1394: "FireWire",
    BusType_SATA: "SATA",
    BusType_NVME: "NVMe",
    BusType_SD: "SD",
    BusType_MMC: "MMC",
}

# Nom de partition GPT de la partition EFI 32 Mo creee par l'installeur.
# Volontairement conserve tel quel : c'est le format on-disk (couche 0 du
# rebrand), pas une marque. Le boot le compare octet pour octet.
GPT_ESP_NAME = "VTOYEFI"

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_setup = ctypes.WinDLL("setupapi", use_last_error=True)


# --------------------------------------------------------------------------
# Structures Win32
# --------------------------------------------------------------------------


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __str__(self) -> str:
        head = "".join(f"{b:02X}" for b in self.Data4[:2])
        tail = "".join(f"{b:02X}" for b in self.Data4[2:])
        return f"{{{self.Data1:08X}-{self.Data2:04X}-{self.Data3:04X}-{head}-{tail}}}"


GUID_DEVINTERFACE_DISK = GUID(
    0x53F56307,
    0xB6BF,
    0x11D0,
    (ctypes.c_ubyte * 8)(0x94, 0xF2, 0x00, 0xA0, 0xC9, 0x1E, 0xFB, 0x8B),
)


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", wintypes.DWORD),
        ("Reserved", ctypes.POINTER(ctypes.c_ulong)),
    ]


class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("ClassGuid", GUID),
        ("DevInst", wintypes.DWORD),
        ("Reserved", ctypes.POINTER(ctypes.c_ulong)),
    ]


class STORAGE_HOTPLUG_INFO(ctypes.Structure):
    _fields_ = [
        ("Size", wintypes.DWORD),
        ("DeviceType", wintypes.DWORD),
        ("DeviceId", wintypes.DWORD),
        ("DeviceHotplug", wintypes.BOOLEAN),
        ("DeviceSafeToRemove", wintypes.BOOLEAN),
        ("DeviceIsRemovable", wintypes.BOOLEAN),
        ("DeviceSeekable", wintypes.BOOLEAN),
    ]


class STORAGE_PROPERTY_QUERY(ctypes.Structure):
    _fields_ = [
        ("PropertyId", wintypes.DWORD),
        ("QueryType", wintypes.DWORD),
        ("AdditionalParameters", ctypes.c_byte * 1),
    ]


class STORAGE_ADAPTER_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.DWORD),
        ("Size", wintypes.DWORD),
        ("MaximumTransferLength", wintypes.DWORD),
        ("MaximumPhysicalPages", wintypes.DWORD),
        ("AlignmentMask", wintypes.DWORD),
        ("AdapterUsesPio", wintypes.BOOLEAN),
        ("AdapterScansDown", wintypes.BOOLEAN),
        ("CommandQueueing", wintypes.BOOLEAN),
        ("AcceleratedTransfer", wintypes.BOOLEAN),
        ("BusType", wintypes.DWORD),
        ("BusMajorVersion", wintypes.WORD),
        ("BusMinorVersion", wintypes.WORD),
        ("Revision", wintypes.WORD),
        ("TransferCount", wintypes.DWORD),
    ]


class GET_LENGTH_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Length", ctypes.c_uint64),
        ("NumberOfBlocks", wintypes.DWORD),
    ]


class STORAGE_DEVICE_NUMBER(ctypes.Structure):
    """DeviceNumber = index physique attendu par l'option /PhyDrive:N."""

    _fields_ = [
        ("DeviceType", wintypes.DWORD),
        ("DeviceNumber", wintypes.DWORD),
    ]


class STORAGE_DEVICE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.DWORD),
        ("Size", wintypes.DWORD),
        ("DeviceType", ctypes.c_ubyte),
        ("DeviceTypeModifier", ctypes.c_ubyte),
        ("RemovableMedia", wintypes.BOOLEAN),
        ("CommandQueueing", wintypes.BOOLEAN),
        ("VendorIdOffset", wintypes.DWORD),
        ("ProductIdOffset", wintypes.DWORD),
        ("ProductRevisionOffset", wintypes.DWORD),
        ("SerialNumberOffset", wintypes.DWORD),
        ("BusType", wintypes.DWORD),
        ("RawPropertiesLength", wintypes.DWORD),
        ("RawDeviceProperties", ctypes.c_ubyte * 1),
    ]


# --------------------------------------------------------------------------
# Prototypes
# --------------------------------------------------------------------------

_setup.SetupDiGetClassDevsW.argtypes = [
    ctypes.POINTER(GUID),
    wintypes.LPCWSTR,
    wintypes.HWND,
    wintypes.DWORD,
]
_setup.SetupDiGetClassDevsW.restype = HDEVINFO

_setup.SetupDiEnumDeviceInterfaces.argtypes = [
    HDEVINFO,
    ctypes.POINTER(SP_DEVINFO_DATA),
    ctypes.POINTER(GUID),
    wintypes.DWORD,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
]
_setup.SetupDiEnumDeviceInterfaces.restype = wintypes.BOOL

_setup.SetupDiGetDeviceInterfaceDetailW.argtypes = [
    HDEVINFO,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(SP_DEVINFO_DATA),
]
_setup.SetupDiGetDeviceInterfaceDetailW.restype = wintypes.BOOL

_setup.SetupDiDestroyDeviceInfoList.argtypes = [HDEVINFO]
_setup.SetupDiDestroyDeviceInfoList.restype = wintypes.BOOL

_k32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
_k32.CreateFileW.restype = wintypes.HANDLE

_k32.DeviceIoControl.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p,
]
_k32.DeviceIoControl.restype = wintypes.BOOL

_k32.CloseHandle.argtypes = [wintypes.HANDLE]
_k32.CloseHandle.restype = wintypes.BOOL

_k32.GetLogicalDrives.restype = wintypes.DWORD


# --------------------------------------------------------------------------
# Dataclass publique
# --------------------------------------------------------------------------


@dataclass
class Disk:
    index: int
    path: str
    model: str = ""
    size_bytes: int = 0
    bus_type: int = 0
    is_removable: bool = False
    is_external: bool = False
    part_scheme: str = ""          # "GPT" / "MBR" / ""
    has_boots_esp: bool = False     # partition EFI VTOYEFI presente
    is_system: bool = False
    error: str = ""

    @property
    def bus_label(self) -> str:
        return BUS_LABELS.get(self.bus_type, "Inconnu")

    @property
    def size_gib(self) -> float:
        return self.size_bytes / (1024 ** 3)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def human_size(n: int) -> str:
    step = 1024.0
    for unit in ("o", "Ko", "Mo", "Go", "To"):
        if n < step or unit == "To":
            return f"{n:.1f} {unit}" if unit != "o" else f"{int(n)} o"
        n /= step
    return f"{n:.1f} To"


def _ioctl(handle, code, in_ref, in_len, out_size) -> tuple[bool, ctypes.Array, int]:
    """Appelle un DeviceIoControl avec un buffer de sortie dimensionne au besoin.

    Les descripteurs STORAGE_* sont de taille variable (en-tete + bloc de
    proprietes), d'ou l'obligation d'allouer generously : passer sizeof(struct)
    seule renvoie des offsets vides.
    """
    out = ctypes.create_string_buffer(out_size)
    returned = wintypes.DWORD(0)
    ok = _k32.DeviceIoControl(
        handle,
        code,
        in_ref,
        in_len,
        ctypes.cast(out, ctypes.c_void_p),
        out_size,
        ctypes.byref(returned),
        None,
    )
    return bool(ok), out, returned.value


def _as(buf: ctypes.Array, struct_type):
    return ctypes.cast(buf, ctypes.POINTER(struct_type)).contents


def _read_sector(path: str, lba: int, count: int = 1) -> bytes:
    """Lecture brute de secteurs via un handle en lecture seule."""
    h = _k32.CreateFileW(
        path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if h == INVALID_HANDLE_VALUE:
        return b""
    try:
        # SET_FILE_POINTER / ReadFile sont plus simples qu'un IOCTL de lecture
        # et suffisent largement pour lire l'en-tete GPT.
        _k32.SetFilePointerEx.argtypes = [
            wintypes.HANDLE, ctypes.c_longlong, ctypes.c_void_p, wintypes.DWORD
        ]
        _k32.SetFilePointerEx.restype = wintypes.BOOL
        _k32.SetFilePointerEx(h, ctypes.c_longlong(lba * 512), None, 0)

        buf = ctypes.create_string_buffer(512 * count)
        got = wintypes.DWORD(0)
        _k32.ReadFile.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p,
        ]
        _k32.ReadFile.restype = wintypes.BOOL
        if not _k32.ReadFile(h, buf, 512 * count, ctypes.byref(got), None):
            return b""
        return buf.raw[: got.value]
    finally:
        _k32.CloseHandle(h)


def _probe_gpt(path: str) -> tuple[str, bool]:
    """Retourne (scheme, presence de la partition VTOYEFI)."""
    header = _read_sector(path, 1)
    if len(header) < 92 or header[:8] != b"EFI PART":
        return "", False
    # Les entrees commencent au LBA declare dans l'en-tete (souvent 2).
    entries_lba = int.from_bytes(header[72:80], "little")
    entries = _read_sector(path, entries_lba, 4)
    if len(entries) < 512:
        return "GPT", False
    # Entree n2 -> offset 128, nom a +56, UTF-16LE, 36 caracteres.
    name = entries[128 + 56: 128 + 56 + 16].decode("utf-16-le", errors="ignore")
    return "GPT", name.rstrip("\x00").strip() == GPT_ESP_NAME


def _drive_letters() -> set[str]:
    mask = _k32.GetLogicalDrives()
    return {
        f"{chr(ord('A') + i)}:"
        for i in range(26)
        if mask & (1 << i)
    }


def _letter_for_index(index: int) -> str:
    """Cherche la lettre de lecteur associee a un disque physique (WMIC-free)."""
    try:
        import subprocess  # noqa: PLC0415

        out = subprocess.run(
            [
                "powershell", "-NoProfile", "-NonInteractive", "-Command",
                "(Get-CimInstance Win32_LogicalDisk | "
                "Where-Object {$_.DriveType -eq 3} | "
                "ForEach-Object { $d=$_; "
                "$p = (Get-CimAssociatedInstance -InputObject $d "
                "-ResultClassName Win32_DiskPartition); "
                "if ($p) { $r = (Get-CimAssociatedInstance -InputObject $p "
                "-ResultClassName Win32_DiskDrive); "
                "if ($r) { \"$($r.Index):$($d.DeviceID)\" } } })",
            ],
            capture_output=True, text=True, timeout=8,
        )
        for line in out.stdout.splitlines():
            if ":" in line:
                idx, dev = line.strip().split(":", 1)
                if idx.strip().isdigit() and int(idx.strip()) == index:
                    return dev.strip().upper()
    except Exception:  # pragma: no cover - degrade gracieusement
        pass
    return ""


def _open(path: str):
    """Ouvre un disque, en lecture/ecriture puis en lecture seule si refuse."""
    access = GENERIC_READ | GENERIC_WRITE
    h = _k32.CreateFileW(
        path, access, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None
    )
    if h == INVALID_HANDLE_VALUE:
        h = _k32.CreateFileW(
            path, 0, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None
        )
    return None if h == INVALID_HANDLE_VALUE else h


def _plausible(raw: bytes) -> str:
    """Ne retient que les chaines manifestement exploitables."""
    text = raw.split(b"\x00", 1)[0].decode("utf-8", errors="ignore").strip()
    if not text or len(text) > 80:
        return ""
    printable = sum(1 for c in text if c.isprintable())
    if printable < max(3, len(text) * 0.8):
        return ""
    return text


def _descriptor_string(buf: ctypes.Array, offset: int, length: int) -> str:
    """Extrait la chaine de marque/modele du descripteur STORAGE_DEVICE.

    Les pilotes ne sont pas coherents sur la base des offsets : la plupart
    les donnent relativement a RawDeviceProperties (offset 36), d'autres
    relativement au debut de la structure. RawPropertiesLength vaut souvent 0.
    On teste donc les deux interpretations et on garde la seule plausible.
    """
    if not offset or offset >= length:
        return ""
    data = bytes(buf)
    header = STORAGE_DEVICE_DESCRIPTOR.RawDeviceProperties.offset
    for base in (0, header):
        if base + offset >= length:
            continue
        text = _plausible(data[base + offset: length])
        if text:
            return text
    return ""


def _query_disk(path: str) -> dict:
    """Interroge un disque (chemin \\?\\PHYSICALDRIVE ou chemin d'interface).

    Retourne numero physique, taille, bus, modele et caractere amovible.
    """
    info: dict = {}
    h = _open(path)
    if h is None:
        return info
    try:
        ok, buf, _ = _ioctl(h, IOCTL_STORAGE_GET_DEVICE_NUMBER, None, 0, 64)
        if ok:
            info["number"] = int(_as(buf, STORAGE_DEVICE_NUMBER).DeviceNumber)

        hot = STORAGE_HOTPLUG_INFO()
        hot.Size = ctypes.sizeof(hot)
        ok, buf, _ = _ioctl(
            h, IOCTL_STORAGE_GET_HOTPLUG_INFO,
            ctypes.cast(ctypes.byref(hot), ctypes.c_void_p), ctypes.sizeof(hot), 64,
        )
        if ok:
            result = _as(buf, STORAGE_HOTPLUG_INFO)
            info["removable"] = bool(result.DeviceIsRemovable)
            info["device_type"] = result.DeviceType

        ok, buf, _ = _ioctl(h, IOCTL_DISK_GET_LENGTH_INFO, None, 0, 64)
        if ok:
            info["size"] = int(_as(buf, GET_LENGTH_INFORMATION).Length)

        query = STORAGE_PROPERTY_QUERY()
        query.QueryType = PropertyStandardQuery
        query.PropertyId = StorageDeviceProperty
        ok, buf, returned = _ioctl(
            h, IOCTL_STORAGE_QUERY_PROPERTY,
            ctypes.cast(ctypes.byref(query), ctypes.c_void_p),
            ctypes.sizeof(query), 4096,
        )
        if ok and returned >= ctypes.sizeof(STORAGE_DEVICE_DESCRIPTOR):
            dev = _as(buf, STORAGE_DEVICE_DESCRIPTOR)
            info["bus"] = int(dev.BusType)
            # Some drivers report RawPropertiesLength == 0; Size is the only
            # reliable upper bound for the string block.
            length = dev.RawPropertiesLength or returned
            vendor = _descriptor_string(buf, dev.VendorIdOffset, length)
            product = _descriptor_string(buf, dev.ProductIdOffset, length)
            model = " ".join(p for p in (vendor, product) if p)
            if not model:
                model = _descriptor_string(buf, dev.SerialNumberOffset, length)
            info["model"] = model
    finally:
        _k32.CloseHandle(h)
    return info


# --------------------------------------------------------------------------
# API publique
# --------------------------------------------------------------------------


def list_disks() -> list[Disk]:
    """Enumere tous les disques physiques installes."""
    out: list[Disk] = []
    devinfo = _setup.SetupDiGetClassDevsW(
        ctypes.byref(GUID_DEVINTERFACE_DISK), None, None, DIGCF_PRESENT | DIGCF_DEVICEINTERFACE
    )
    if devinfo == INVALID_HANDLE_VALUE:
        return out

    try:
        index = 0
        while True:
            ifd = SP_DEVICE_INTERFACE_DATA()
            ifd.cbSize = ctypes.sizeof(ifd)
            if not _setup.SetupDiEnumDeviceInterfaces(
                devinfo, None, ctypes.byref(GUID_DEVINTERFACE_DISK), index,
                ctypes.byref(ifd),
            ):
                break
            index += 1

            needed = wintypes.DWORD(0)
            _setup.SetupDiGetDeviceInterfaceDetailW(
                devinfo, ctypes.byref(ifd), None, 0, ctypes.byref(needed), None
            )
            if not needed.value:
                continue
            buf = ctypes.create_string_buffer(needed.value)

            class _Detail(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("DevicePath", wintypes.WCHAR * 1)]

            detail = ctypes.cast(buf, ctypes.POINTER(_Detail))
            detail.contents.cbSize = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
            if not _setup.SetupDiGetDeviceInterfaceDetailW(
                devinfo, ctypes.byref(ifd), buf, needed.value, None, None
            ):
                continue

            # DevicePath est un WCHAR[] situe juste apres le DWORD cbSize.
            # On decode le buffer brut : c'est plus fiable que wstring_at sur
            # un champ de structure, dont l'alignement varie selon la plateforme.
            payload = buf.raw[4:]
            end = payload.find(b"\x00\x00")
            if end % 2:
                end += 1
            iface = payload[:end].decode("utf-16-le", errors="ignore")
            if not iface:
                continue

            # SetupDI renvoie un chemin d'INTERFACE (\\?\usbstor#disk&...),
            # pas \\?\PHYSICALDRIVEn. IOCTL_STORAGE_GET_DEVICE_NUMBER fait la
            # correspondance vers l'index physique attendu par /PhyDrive:N.
            meta = _query_disk(iface)
            num = meta.get("number")
            if num is None:
                continue
            path = rf"\\?\PHYSICALDRIVE{num}"

            disk = Disk(index=num, path=path)
            disk.model = meta.get("model", "")
            disk.size_bytes = meta.get("size", 0)
            disk.bus_type = meta.get("bus", 0)
            disk.is_removable = meta.get("removable", False)
            disk.is_external = disk.bus_type in (BusType_USB, BusType_1394, BusType_SD, BusType_MMC)

            try:
                disk.part_scheme, disk.has_boots_esp = _probe_gpt(path)
            except Exception as exc:  # pragma: no cover
                disk.error = str(exc)

            if not disk.part_scheme:
                # MBR : signature 0xAA55 en fin de secteur 0
                try:
                    sector0 = _read_sector(path, 0)
                    if len(sector0) == 512 and sector0[510:512] == b"\x55\xAA":
                        disk.part_scheme = "MBR"
                except Exception:  # pragma: no cover
                    pass

            out.append(disk)
    finally:
        _setup.SetupDiDestroyDeviceInfoList(devinfo)

    out.sort(key=lambda d: d.index)
    return out


if __name__ == "__main__":  # pragma: no cover
    for d in list_disks():
        flags = []
        if d.is_external:
            flags.append("externe")
        if d.has_boots_esp:
            flags.append("237Boots installe")
        print(
            f"Disque {d.index}: {d.model or '?':<28} {human_size(d.size_bytes):>10} "
            f"{d.bus_label:<9} {d.part_scheme:<4} {' '.join(flags)}"
        )
