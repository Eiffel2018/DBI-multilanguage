"""Translate the three statistics headers after fixed-size native copies.

Only the three header measurement call sites enter this wrapper. Their native
strings use inline storage; retaining that ownership avoids freeing table data.
"""
def make_statistics_width(lookup):
    source='''
stp x29, x30, [sp, #-0x20]!
stp x19, x20, [sp, #0x10]
mov x19, x0
ldp x0, x1, [x19]
add x9, x19, #0x10
cmp x0, x9
b.ne {measure}
cmp x1, #15
b.hi {measure}
bl LOOKUP
cbz x0, {measure}
cmp x1, #15
b.hi {measure}
mov x20, x1
add x9, x19, #0x10
{copy}:
cbz x1, {publish}
ldrb w10, [x0], #1
strb w10, [x9], #1
sub x1, x1, #1
b {copy}
{publish}:
strb wzr, [x9]
str x20, [x19, #8]
{measure}:
mov x0, x19
bl 0x134e60
ldp x19, x20, [sp, #0x10]
ldp x29, x30, [sp], #0x20
ret
'''.replace('LOOKUP',hex(lookup))
    return [('L',s[1:-2]) if s.startswith('{') and s.endswith('}:') else ('I',s)
            for s in source.strip().splitlines()]
