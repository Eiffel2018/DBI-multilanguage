"""Translate numeric progress fields without applying substring edits to filenames."""
from dbi_translate.asm import movk_seq

TOKENS=('МБ/сек','тек.','сек','ср.','МБ')
RATE_KEY='@DBI_RATE:'

def make_token(lookup):
    program=[('I','stp x29, x30, [sp, #-0x30]!')]
    for index,word in enumerate(TOKENS):
        data=word.encode();n=len(data);nextlabel=f'token_{index+1}'
        program += [('I',f'cmp x1, #{n}'),('I',f'b.lo {{{nextlabel}}}')]
        offset=0
        for width in (8,4,2,1):
            while n-offset>=width:
                rd='x9' if width==8 else 'w9'
                load={8:'ldr',4:'ldr',2:'ldrh',1:'ldrb'}[width]
                program.append(('I',f'{load} {rd}, [x0, #{offset}]'))
                value=int.from_bytes(data[offset:offset+width],'little')
                if width==8:program+=movk_seq(10,value)
                elif width==4:
                    program += [('I',f'movz w10, #{value&65535}'),('I',f'movk w10, #{value>>16}, lsl #16')]
                else:program.append(('I',f'mov w10, #{value}'))
                program += [('I',f'cmp {rd}, '+('x10' if width==8 else 'w10')),
                            ('I',f'b.ne {{{nextlabel}}}')]
                offset+=width
        program += [('I',f'mov x4, #{n}'),('I','b {token_hit}'),('L',nextlabel)]
    # Private table keys keep tiny unit/abbreviation fragments out of the
    # general prefix/suffix matcher used for other UI text and filenames.
    program += [('I','mov x0, #0'),('I','mov x4, #0'),('I','b {token_out}'),('L','token_hit'),
                ('I','mov x9, x0')]
    program += movk_seq(10,int.from_bytes(RATE_KEY.encode()[:8],'little'))
    program += [('I','str x10, [sp, #0x10]'),
                ('I',f'mov w10, #{int.from_bytes(RATE_KEY.encode()[8:],'little')}'),
                ('I','strh w10, [sp, #0x18]'),('I','add x10, sp, #0x1a'),
                ('I','mov x11, x4'),('L','key_copy'),('I','ldrb w12, [x9], #1'),
                ('I','strb w12, [x10], #1'),('I','subs x11, x11, #1'),('I','b.ne {key_copy}'),
                ('I','add x0, sp, #0x10'),('I','add x1, x4, #10'),('I',f'bl {lookup:#x}'),
                ('L','token_out'),('I','ldp x29, x30, [sp], #0x30'),('I','ret')]
    return program

def make_progress(v,token,original):
    # Recognize complete numeric spans containing only the five known Russian
    # labels and progress punctuation. Any other letter makes the whole span
    # fall back to the original exact/prefix/suffix matcher.
    source='''
sub sp, sp, #0x260
stp x29, x30, [sp]
stp x19, x20, [sp, #0x10]
stp x21, x22, [sp, #0x20]
stp x23, x24, [sp, #0x30]
stp x25, x26, [sp, #0x40]
stp x27, x28, [sp, #0x50]
mov x19, x0
mov x20, x1
cmp x20, #0x200
b.hi {fallback}
mov x21, #0
add x22, sp, #0x60
mov x23, #0
mov x27, #0
mov x28, #0
loop:
cmp x21, x20
b.hs {finished}
ldrb w9, [x19, x21]
cmp w9, #0x80
b.hs {label}
sub w10, w9, #0x30
cmp w10, #9
b.hi {punctuation}
mov x28, #1
b {ascii}
punctuation:
PUNCTUATION
b {fallback}
ascii:
cmp x23, #0x1ff
b.hs {fallback}
strb w9, [x22], #1
add x23, x23, #1
add x21, x21, #1
b {loop}
label:
add x0, x19, x21
sub x1, x20, x21
bl TOKEN
cbz x0, {fallback}
mov x27, #1
add x21, x21, x4
add x9, x23, x1
cmp x9, #0x1ff
b.hi {fallback}
mov x23, x9
copy:
ldrb w9, [x0], #1
strb w9, [x22], #1
subs x1, x1, #1
b.ne {copy}
b {loop}
finished:
cbz x27, {fallback}
SCRATCH_ADRP
SCRATCH_ADD
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
fallback:
mov x0, x19
mov x1, x20
bl ORIGINAL
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
    for line in source.strip().splitlines():
        if line=='PUNCTUATION':
            for char in ' /:,.()%+-[]RW':
                program += [('I',f'cmp w9, #{ord(char)}'),('I','b.eq {ascii}')]
        elif line=='SCRATCH_ADRP':program.append(('ADRP',12,v.scratch))
        elif line=='SCRATCH_ADD':program.append(('I',f'add x12, x12, #{v.scratch&4095:#x}'))
        elif line.endswith(':'):program.append(('L',line[:-1]))
        else:program.append(('I',line.replace('TOKEN',hex(token)).replace('ORIGINAL',hex(original))))
    return program
