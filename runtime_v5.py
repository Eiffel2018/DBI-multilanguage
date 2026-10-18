"""Bounded translation of packed fmt C-string and string-view arguments.

Native fmt packs a four-bit type per argument and uses 16-byte value slots.
Unpacked descriptors (bit 63) and custom/numeric arguments are untouched.
"""
def make_draw_text(lookup,ansi):
    # Low-level rendering also receives real filenames. Match whole labels;
    # only the L3 footer needs suffix matching. Never rewrite filename suffixes.
    source='''
stp x29, x30, [sp, #-0x30]!
stp x19, x20, [sp, #0x10]
mov x19, x0
mov x20, x1
bl LOOKUP
cbnz x0, {done}
cmp x20, #512
b.hi {miss}
mov x9, #0
{scan}:
add x10, x9, #3
cmp x10, x20
b.hi {miss}
ldrb w10, [x19, x9]
cmp w10, #76
b.ne {advance}
add x11, x19, x9
ldrb w10, [x11, #1]
cmp w10, #51
b.ne {advance}
ldrb w10, [x11, #2]
cmp w10, #32
b.eq {footer}
{advance}:
add x9, x9, #1
b {scan}
{footer}:
mov x0, x19
mov x1, x20
bl ANSI
b {done}
{miss}:
mov x0, x19
mov x1, x20
{done}:
ldp x19, x20, [sp, #0x10]
ldp x29, x30, [sp], #0x30
ret
'''.replace('LOOKUP',hex(lookup)).replace('ANSI',hex(ansi))
    return [('L',s[1:-2]) if s.startswith('{') and s.endswith('}:') else ('I',s)
            for s in source.strip().splitlines()]

def make_fmt_args(lookup):
    source='''
sub sp, sp, #0x80
stp x29, x30, [sp]
stp x0, x1, [sp, #0x10]
stp x2, x3, [sp, #0x20]
str x8, [sp, #0x30]
stp x19, x20, [sp, #0x40]
stp x21, x22, [sp, #0x50]
stp x23, x24, [sp, #0x60]
cmp x2, #0
b.lt {done}
cbz x3, {done}
mov x19, x2
mov x20, x3
mov x24, #15
{next}:
cbz x19, {done}
and x21, x19, #15
cmp x21, #12
b.eq {cstring}
cmp x21, #13
b.ne {advance}
ldp x0, x1, [x20]
cbz x0, {advance}
cmp x1, #512
b.hi {advance}
b {lookup}
{cstring}:
ldr x0, [x20]
cbz x0, {advance}
mov x1, #0
{length}:
cmp x1, #512
b.hs {advance}
ldrb w9, [x0, x1]
cbz w9, {lookup}
add x1, x1, #1
b {length}
{lookup}:
cbz x1, {advance}
bl LOOKUP
cbz x0, {advance}
str x0, [x20]
cmp x21, #13
b.ne {advance}
str x1, [x20, #8]
{advance}:
lsr x19, x19, #4
add x20, x20, #16
subs x24, x24, #1
b.ne {next}
{done}:
ldp x19, x20, [sp, #0x40]
ldp x21, x22, [sp, #0x50]
ldp x23, x24, [sp, #0x60]
ldr x8, [sp, #0x30]
ldp x2, x3, [sp, #0x20]
ldp x0, x1, [sp, #0x10]
ldp x29, x30, [sp]
add sp, sp, #0x80
ret
'''.replace('LOOKUP',hex(lookup))
    return [('L',s[1:-2]) if s.startswith('{') and s.endswith('}:') else ('I',s)
            for s in source.strip().splitlines()]
