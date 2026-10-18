"""Translate all native tab labels through the external language table."""
from runtime_v7 import make_tab_render as make_native_tab_render

def make_tab_render(site,matcher):
    code=make_native_tab_render(site,matcher)
    at=code.index(('I','cbz x2, {original}'))+1
    # Activity Log also uses this renderer for a single user's nickname.
    code[at:at]=[('I','cmp x2, #2'),('I','b.lo {original}')]
    return code

def make_tab_label(lookup):
    return [('I','cbz x0, {done}'),('I','cbz x1, {done}'),
            ('I','cmp x1, #0x100'),('I','b.hi {done}'),
            ('I','stp x29, x30, [sp, #-0x20]!'),
            ('I','stp x0, x1, [sp, #0x10]'),('I',f'bl {lookup:#x}'),
            ('I','cbnz x0, {hit}'),('I','ldp x0, x1, [sp, #0x10]'),
            ('L','hit'),('I','ldp x29, x30, [sp], #0x20'),
            ('L','done'),('I','ret')]
