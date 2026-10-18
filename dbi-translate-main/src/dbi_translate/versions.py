"""Per-version patch configuration. Adding a DBI version is a new Version entry here."""

from __future__ import annotations

from dataclasses import dataclass

BASE = 0x7100000000   # NRO load address; the offsets below are file offsets


@dataclass(frozen=True)
class Site:
    """A hook site: the patched offset, the instruction it replaces (verified and
    re-run inside the hook), where the hook branches back to, and the branch style.
    entry='B' for a function's first instruction (LR not yet saved); 'BL' where LR
    is already saved."""

    addr: int
    insn: int
    resume: int
    entry: str


@dataclass(frozen=True)
class Version:
    """Everything the builder needs to target one DBI release."""

    name: str
    cave: tuple[int, int]        # [start, end) zero-fill in .text
    state: int                   # bss: +0 lock, +4 retry, +8 state-ready, +0x10 magic, +0x18 tableptr
    persist: int                 # 32-byte std::string the loader fills and leaks
    scratch: int                 # rebuild buffer
    reader_fn: int               # file reader the loader calls (X0=len, X1=path, X8=out)
    reader: Site
    fmt: Site
    glog: Site
    ctor: Site
    sink: Site


V905 = Version(
    name="905",
    cave=(0xB90B3C, 0xB91000),
    state=0x11FE000,
    persist=0x11FE020,
    scratch=0x11FE080,
    reader_fn=0x143A80,
    reader=Site(0x143A80, 0xA9B87BFD, 0x143A84, "B"),   # STP X29,X30,[SP,#-0x80]!
    fmt=Site(0x6F6460, 0xD10983FF, 0x6F6464, "B"),      # SUB SP,SP,#0x260
    glog=Site(0x1AC470, 0xA9B77BFD, 0x1AC474, "B"),     # STP X29,X30,[SP,#-0x90]!
    ctor=Site(0x7E180, 0xA9BD7BFD, 0x7E184, "B"),       # STP X29,X30,[SP,#-0x30]!
    sink=Site(0x6771B0, 0xAA0103F6, 0x6771B4, "BL"),    # MOV X22,X1
)

VERSIONS = {v.name: v for v in (V905,)}
