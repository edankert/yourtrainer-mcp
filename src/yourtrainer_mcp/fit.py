"""Minimal, self-contained FIT binary codec (TASK-0020 support).

The FIT (Flexible and Interoperable Data Transfer) format is publicly
documented by Garmin. This module implements just enough of it to *write*
valid files and *read* the standard (non-compressed, non-developer-field)
records we and common exporters emit — without pulling in the Garmin SDK
(per ADR-0001's minimal-dependency posture).

For rich reading of arbitrary real-world files, the optional ``fitparse``
extra is preferred; this codec is the always-available fallback and the basis
for hermetic round-trip tests.

Layout written:
- 14-byte header (with header CRC), little-endian.
- One definition message + data message(s) per message type.
- Trailing file CRC.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

# Global message numbers (FIT profile).
MSG_FILE_ID = 0
MSG_RECORD = 20
MSG_WORKOUT = 26
MSG_WORKOUT_STEP = 27

# Base types: name -> (type byte, struct format, size, invalid value).
ENUM = ("enum", 0x00, "B", 1, 0xFF)
UINT8 = ("uint8", 0x02, "B", 1, 0xFF)
UINT16 = ("uint16", 0x84, "<H", 2, 0xFFFF)
UINT32 = ("uint32", 0x86, "<I", 4, 0xFFFFFFFF)
SINT32 = ("sint32", 0x85, "<i", 4, 0x7FFFFFFF)
STRING = ("string", 0x07, None, None, 0x00)

_TYPE_BY_BYTE = {t[1]: t for t in (ENUM, UINT8, UINT16, UINT32, SINT32, STRING)}

# FIT epoch: seconds between Unix epoch and 1989-12-31T00:00:00Z.
FIT_EPOCH_OFFSET = 631065600


def crc16(data: bytes) -> int:
    """The FIT 16-bit CRC."""
    table = [
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]
    crc = 0
    for byte in data:
        tmp = table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ table[byte & 0xF]
        tmp = table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ table[(byte >> 4) & 0xF]
    return crc & 0xFFFF


@dataclass
class Field:
    num: int
    base_type: tuple
    value: Any


class FitWriter:
    """Accumulates messages and emits a complete FIT byte string."""

    def __init__(self) -> None:
        self._body = bytearray()
        self._defined: dict[int, int] = {}  # global_msg_num -> local_type
        self._next_local = 0

    def _field_bytes(self, f: Field) -> tuple[int, int, bytes]:
        """Return (size, type_byte, encoded_value) for a field."""
        name = f.base_type[0]
        type_byte = f.base_type[1]
        if name == "string":
            raw = str(f.value).encode("utf-8") + b"\x00"
            return len(raw), type_byte, raw
        fmt = f.base_type[2]
        size = f.base_type[3]
        return size, type_byte, struct.pack(fmt, int(f.value))

    def add_message(self, global_num: int, fields: list[Field]) -> None:
        # Definitions are size-specific (strings vary), so (re)define each time
        # a message of this global number is written. Simple and correct.
        local = self._next_local % 16
        self._next_local += 1

        encoded = [self._field_bytes(f) for f in fields]

        # Definition record.
        defn = bytearray()
        defn.append(0x40 | local)  # definition header
        defn.append(0x00)  # reserved
        defn.append(0x00)  # architecture: little-endian
        defn += struct.pack("<H", global_num)
        defn.append(len(fields))
        for f, (size, type_byte, _) in zip(fields, encoded, strict=True):
            defn += bytes([f.num, size, type_byte])
        self._body += defn

        # Data record.
        data = bytearray([local])
        for _size, _tb, raw in encoded:
            data += raw
        self._body += data

    def to_bytes(self) -> bytes:
        body = bytes(self._body)
        header = bytearray()
        header.append(14)  # header size
        header.append(0x20)  # protocol version 2.0
        header += struct.pack("<H", 2147)  # profile version
        header += struct.pack("<I", len(body))
        header += b".FIT"
        header += struct.pack("<H", crc16(bytes(header)))
        full = bytes(header) + body
        return full + struct.pack("<H", crc16(full))


def decode(data: bytes) -> list[tuple[int, dict[int, Any]]]:
    """Decode standard FIT bytes into ``[(global_msg_num, {field_num: value})]``.

    Handles little-endian normal-header records with the base types this module
    writes. Compressed-timestamp headers and developer fields are not supported
    (use the ``fitparse`` extra for those).
    """
    if len(data) < 14 or data[8:12] != b".FIT":
        raise ValueError("not a FIT file (missing .FIT signature)")
    header_size = data[0]
    data_size = struct.unpack("<I", data[4:8])[0]
    pos = header_size
    end = header_size + data_size

    definitions: dict[int, dict] = {}
    messages: list[tuple[int, dict[int, Any]]] = []

    while pos < end:
        record_header = data[pos]
        pos += 1
        if record_header & 0x80:
            raise ValueError("compressed-timestamp headers are not supported")
        local = record_header & 0x0F
        if record_header & 0x40:  # definition message
            # reserved, arch, global(2), nfields, fields*3
            arch = data[pos + 1]
            endian = "<" if arch == 0 else ">"
            global_num = struct.unpack(f"{endian}H", data[pos + 2:pos + 4])[0]
            nfields = data[pos + 4]
            pos += 5
            fields = []
            for _ in range(nfields):
                fnum, size, type_byte = data[pos], data[pos + 1], data[pos + 2]
                fields.append((fnum, size, type_byte))
                pos += 3
            definitions[local] = {"global": global_num, "fields": fields, "endian": endian}
        else:  # data message
            defn = definitions[local]
            values: dict[int, Any] = {}
            for fnum, size, type_byte in defn["fields"]:
                raw = data[pos:pos + size]
                pos += size
                values[fnum] = _decode_value(type_byte, size, raw, defn["endian"])
            messages.append((defn["global"], values))
    return messages


def encode_activity_fit(samples: list[dict]) -> bytes:
    """Encode a minimal FIT *activity* file from per-second samples.

    Each sample may contain: ``power`` (W), ``heart_rate`` (bpm),
    ``cadence`` (rpm), ``distance_m``, ``altitude_m``, ``speed_mps``.
    ``timestamp`` is assigned at 1 Hz from a fixed FIT-epoch base. Primarily
    used to generate test fixtures; field scaling follows the FIT profile.
    """
    w = FitWriter()
    w.add_message(MSG_FILE_ID, [
        Field(0, ENUM, 4),       # type = activity
        Field(1, UINT16, 255),
        Field(4, UINT32, 0),
    ])
    for i, s in enumerate(samples):
        w.add_message(MSG_RECORD, [
            Field(253, UINT32, i),                                   # timestamp (s, FIT epoch)
            Field(7, UINT16, int(s.get("power", 0))),                # power (W)
            Field(3, UINT8, int(s.get("heart_rate", 0))),            # heart_rate (bpm)
            Field(4, UINT8, int(s.get("cadence", 0))),               # cadence (rpm)
            Field(5, UINT32, int(round(s.get("distance_m", 0) * 100))),       # distance (cm)
            Field(2, UINT16, int(round((s.get("altitude_m", 0) + 500) * 5))), # altitude
            Field(6, UINT16, int(round(s.get("speed_mps", 0) * 1000))),       # speed (mm/s)
        ])
    return w.to_bytes()


def decode_activity(data: bytes) -> list[dict]:
    """Decode FIT activity ``record`` messages into unscaled sample dicts."""
    out: list[dict] = []
    for global_num, vals in decode(data):
        if global_num != MSG_RECORD:
            continue
        sample: dict = {}
        if 253 in vals:
            sample["timestamp_s"] = int(vals[253])  # seconds since FIT epoch
        if 7 in vals:
            sample["power"] = float(vals[7])
        if 3 in vals:
            sample["heart_rate"] = float(vals[3])
        if 4 in vals:
            sample["cadence"] = float(vals[4])
        if 5 in vals:
            sample["distance_m"] = vals[5] / 100.0
        if 2 in vals:
            sample["altitude_m"] = vals[2] / 5.0 - 500.0
        if 6 in vals:
            sample["speed_mps"] = vals[6] / 1000.0
        out.append(sample)
    return out


def _decode_value(type_byte: int, size: int, raw: bytes, endian: str) -> Any:
    base = _TYPE_BY_BYTE.get(type_byte)
    if base is None:
        return raw  # unknown type: return raw bytes
    name = base[0]
    if name == "string":
        return raw.split(b"\x00", 1)[0].decode("utf-8", "replace")
    fmt_char = base[2]
    assert fmt_char is not None  # only string has no struct format, handled above
    fmt = endian + fmt_char.lstrip("<>")
    return struct.unpack(fmt, raw)[0]
