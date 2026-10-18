"""Translate the tab-name array before native centering and frame assembly."""
def make_tab_render(site,matcher):
    source='''
sub sp, sp, #0x140
stp x29, x30, [sp]
stp x19, x20, [sp, #0x10]
stp x21, x22, [sp, #0x20]
stp x23, x24, [sp, #0x30]
mov x19, x0
mov x20, x1
mov x21, x2
mov x22, x3
cbz x1, {original}
cbz x2, {original}
cmp x2, #6
b.hi {original}
mov x23, #0
add x24, sp, #0x60
{next}:
ldp x9, x10, [x20]
ldp x11, x12, [x20, #0x10]
stp x9, x10, [x24]
stp x11, x12, [x24, #0x10]
mov x0, x9
mov x1, x10
cbz x0, {advance}
bl MATCHER
stp x0, x1, [x24]
{advance}:
add x20, x20, #0x20
add x24, x24, #0x20
add x23, x23, #1
cmp x23, x21
b.lo {next}
add x1, sp, #0x60
b {call}
{original}:
mov x1, x20
{call}:
mov x0, x19
mov x2, x21
mov x3, x22
bl {native}
ldp x19, x20, [sp, #0x10]
ldp x21, x22, [sp, #0x20]
ldp x23, x24, [sp, #0x30]
ldp x29, x30, [sp]
add sp, sp, #0x140
ret
{native}:
stp x29, x30, [sp, #-0x100]!
b RESUME
'''.replace('MATCHER',hex(matcher)).replace('RESUME',hex(site.resume))
    return [('L',s[1:-2]) if s.startswith('{') and s.endswith('}:') else ('I',s)
            for s in source.strip().splitlines()]
