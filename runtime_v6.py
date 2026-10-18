"""UI field matching, preserving padding, colors and unmodified field values."""
from dbi_translate.asm import movk_seq
from runtime_v3 import OUTPUT

def make_ui_field(v,lookup,fallback):
    source='''
sub sp, sp, #0x280
stp x29, x30, [sp]
stp x19, x20, [sp, #0x10]
stp x21, x22, [sp, #0x20]
stp x23, x24, [sp, #0x30]
stp x25, x26, [sp, #0x40]
stp x27, x28, [sp, #0x50]
mov x19, x0
mov x20, x1
bl LOOKUP
cbnz x0, {done}
cmp x20, #512
b.hi {miss}
mov x21, #0
{leading}:
cmp x21, x20
b.hs {miss}
ldrb w9, [x19, x21]
cmp w9, #32
b.ne {trim_end}
add x21, x21, #1
b {leading}
{trim_end}:
sub x22, x20, x21
add x23, x19, x21
{trailing}:
cbz x22, {miss}
sub x9, x22, #1
ldrb w10, [x23, x9]
cmp w10, #32
b.ne {trimmed}
sub x22, x22, #1
b {trailing}
{trimmed}:
mov x0, x23
mov x1, x22
bl LOOKUP
mov x24, x22
cbnz x0, {hit}
mov x24, #0
{colon_scan}:
cmp x24, x22
b.hs {miss}
cmp x24, #64
b.hs {miss}
ldrb w9, [x23, x24]
cmp w9, #58
b.eq {label_trim}
add x24, x24, #1
b {colon_scan}
{label_trim}:
cbz x24, {miss}
sub x9, x24, #1
ldrb w10, [x23, x9]
cmp w10, #32
b.ne {label_key}
sub x24, x24, #1
b {label_trim}
{label_key}:
KEY_PREFIX
add x9, sp, #0x6b
mov x10, x23
mov x11, x24
{key_copy}:
ldrb w12, [x10], #1
strb w12, [x9], #1
subs x11, x11, #1
b.ne {key_copy}
add x0, sp, #0x60
add x1, x24, #11
bl LOOKUP
cbz x0, {miss}
{hit}:
mov x25, x0
mov x26, x1
sub x28, x20, x24
add x28, x28, x26
cmp x28, #511
b.hi {miss}
add x27, sp, #0x60
mov x9, x19
mov x10, x21
cbz x10, {target}
{prefix_copy}:
ldrb w11, [x9], #1
strb w11, [x27], #1
subs x10, x10, #1
b.ne {prefix_copy}
{target}:
mov x9, x25
mov x10, x26
cbz x10, {suffix}
{target_copy}:
ldrb w11, [x9], #1
strb w11, [x27], #1
subs x10, x10, #1
b.ne {target_copy}
{suffix}:
add x10, x21, x24
add x9, x19, x10
sub x10, x20, x10
cbz x10, {publish}
{suffix_copy}:
ldrb w11, [x9], #1
strb w11, [x27], #1
subs x10, x10, #1
b.ne {suffix_copy}
{publish}:
strb wzr, [x27]
SCRATCH
sub x10, x19, x9
cmp x10, #512
b.hs {destination_ready}
OUTPUT
{destination_ready}:
mov x0, x9
mov x1, x28
add x10, sp, #0x60
add x11, x28, #1
{publish_copy}:
ldrb w12, [x10], #1
strb w12, [x9], #1
subs x11, x11, #1
b.ne {publish_copy}
b {done}
{miss}:
mov x0, x19
mov x1, x20
bl FALLBACK
{done}:
ldp x19, x20, [sp, #0x10]
ldp x21, x22, [sp, #0x20]
ldp x23, x24, [sp, #0x30]
ldp x25, x26, [sp, #0x40]
ldp x27, x28, [sp, #0x50]
ldp x29, x30, [sp]
add sp, sp, #0x280
ret
'''.replace('LOOKUP',hex(lookup)).replace('FALLBACK',hex(fallback))
    prefix=b'@DBI_LABEL:'
    program=[]
    for line in source.strip().splitlines():
        if line=='KEY_PREFIX':
            program+=movk_seq(10,int.from_bytes(prefix[:8],'little'))
            program += [('I','str x10, [sp, #0x60]')]
            program+=movk_seq(10,int.from_bytes(prefix[8:],'little'))
            program += [('I','str w10, [sp, #0x68]')]
        elif line=='SCRATCH':program += [('ADRP',9,v.scratch),('I',f'add x9, x9, #{v.scratch&4095}')]
        elif line=='OUTPUT':program += [('ADRP',9,OUTPUT),('I',f'add x9, x9, #{OUTPUT&4095}')]
        elif line.startswith('{') and line.endswith('}:'):program.append(('L',line[1:-2]))
        else:program.append(('I',line))
    return program
