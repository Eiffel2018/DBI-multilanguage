"""Bounded ANSI-preserving wrapper for the existing DBI translation matcher."""
OUTPUT = 0x1278D00

def make_ansi(v, matcher):
    # Assemble on the stack before publishing: input may alias OUTPUT after a
    # previous consumer hook. Never overwrite input while still reading it.
    instructions = '''
sub sp, sp, #0x260
stp x29, x30, [sp]
stp x19, x20, [sp, #0x10]
stp x21, x22, [sp, #0x20]
stp x23, x24, [sp, #0x30]
stp x25, x26, [sp, #0x40]
stp x27, x28, [sp, #0x50]
mov x19, x0
add x20, x0, x1
cbz x1, {fallback}
ldrb w9, [x0]
cmp w9, #0x20
b.lo {segmented}
mov x9, x0
scan:
cmp x9, x20
b.hs {direct}
ldrb w10, [x9], #1
cmp w10, #0x1b
b.ne {scan}
segmented:
cmp x1, #0x200
b.hi {fallback}
mov x21, x0
add x22, sp, #0x60
mov x23, #0
mov x28, #0
loop:
cmp x21, x20
b.hs {finished}
ldrb w9, [x21]
cmp w9, #0x20
b.lo {control}
mov x24, x21
plain:
add x21, x21, #1
cmp x21, x20
b.hs {translate}
ldrb w9, [x21]
cmp w9, #0x20
b.hs {plain}
translate:
sub x25, x21, x24
mov x0, x24
mov x1, x25
bl MATCHER
cmp x0, x24
cset w9, ne
orr x28, x28, x9
cmp x1, x25
cset w9, ne
orr x28, x28, x9
b {append}
control:
mov x26, x21
add x21, x21, #1
cmp w9, #0x1b
b.ne {raw}
cmp x21, x20
b.hs {raw}
ldrb w9, [x21]
cmp w9, #0x5b
b.ne {raw}
add x27, x21, #1
ansi:
cmp x27, x20
b.hs {raw}
ldrb w9, [x27], #1
cmp w9, #0x6d
b.eq {valid}
cmp w9, #0x3b
b.eq {ansi}
sub w9, w9, #0x30
cmp w9, #9
b.ls {ansi}
b {raw}
valid:
mov x21, x27
raw:
mov x0, x26
sub x1, x21, x26
append:
add x9, x23, x1
cmp x9, #0x1ff
b.hi {fallback}
mov x23, x9
cbz x1, {loop}
copy:
ldrb w9, [x0], #1
strb w9, [x22], #1
subs x1, x1, #1
b.ne {copy}
b {loop}
finished:
cbz x28, {fallback}
OUTPUT_ADRP
OUTPUT_ADD
mov x0, x12
mov x1, x23
add x13, sp, #0x60
publish:
cbz x23, {published}
ldrb w9, [x13], #1
strb w9, [x12], #1
sub x23, x23, #1
b {publish}
published:
strb wzr, [x12]
b {out}
direct:
bl MATCHER
b {out}
fallback:
mov x0, x19
sub x1, x20, x19
out:
ldp x27, x28, [sp, #0x50]
ldp x25, x26, [sp, #0x40]
ldp x23, x24, [sp, #0x30]
ldp x21, x22, [sp, #0x20]
ldp x19, x20, [sp, #0x10]
ldp x29, x30, [sp]
add sp, sp, #0x260
ret
'''
    program=[]
    for line in instructions.strip().splitlines():
        if line.endswith(':'):program.append(('L',line[:-1]))
        elif line=='OUTPUT_ADRP':program.append(('ADRP',12,OUTPUT))
        elif line=='OUTPUT_ADD':program.append(('I',f'add x12, x12, #{OUTPUT&0xfff:#x}'))
        else:program.append(('I',line.replace('MATCHER',hex(matcher))))
    return program

def safe_lookup(program):
    # Empty keys must not enter the decrement-to-zero comparison loop.
    program=list(program)
    i=program.index(('I','cmp w1, w9'))
    program[i:i]=[('I','cbz w9, {sl_next}')]
    return program

def safe_loader(program):
    program=list(program)
    i=program.index(('I','umull x12, w12, w13'))
    program[i:i]=[
        ('I','cbz w12, {ld_fail}'),('I','cmp w13, #6'),('I','b.lo {ld_fail}'),
        ('I','ldr w14, [x10, #0x14]'),('I','cmp w14, #4'),('I','b.lo {ld_fail}'),
        ('I','ldr w15, [x10, #0x18]'),('I','cmp w15, w14'),('I','b.ls {ld_fail}'),
        ('I','cmp w15, w13'),('I','b.hs {ld_fail}')]
    i=program.index(('I','str x10, [x19, #0x18]'))
    program[i:i]=[
        ('I','ldr w12, [x10, #0xc]'),('I','add x16, x10, #0x20'),
        ('L','entry_check'),('I','ldrh w17, [x16]'),('I','cbz w17, {ld_fail}'),
        ('I','sub w6, w15, w14'),('I','cmp w17, w6'),('I','b.hs {ld_fail}'),
        ('I','add x6, x16, x14'),('I','ldrb w6, [x6, x17]'),('I','cbnz w6, {ld_fail}'),
        ('I','ldrh w17, [x16, #2]'),('I','cbz w17, {ld_fail}'),
        ('I','sub w6, w13, w15'),('I','cmp w17, w6'),('I','b.hs {ld_fail}'),
        ('I','add x6, x16, x15'),('I','ldrb w6, [x6, x17]'),('I','cbnz w6, {ld_fail}'),
        ('I','add x16, x16, x13'),('I','subs w12, w12, #1'),('I','b.ne {entry_check}')]
    return program
