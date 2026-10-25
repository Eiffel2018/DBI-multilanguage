"""Keep DBI 912's INI parser strings out of the presentation translator."""
from dbi_translate import hooks

# Native section/comment parser followed by the key/value parser. Their direct
# std::string constructor calls create machine-readable nodes, not UI labels.
PARSER_START = 0x67ad40
PARSER_END = 0x67c570


def make_ctor(v, translator):
    # LR is the native caller's return address: the entry hook is a B, not BL.
    # ADRP remains image-relative after relocation; preserve both scratch regs
    # and all original constructor arguments on the untranslated path.
    return [
        ('I', 'stp x9, x10, [sp, #-0x10]!'),
        ('ADRP', 9, PARSER_START),
        ('I', f'add x9, x9, #{PARSER_START & 0xfff:#x}'),
        ('I', 'sub x9, x30, x9'),
        ('I', f'mov x10, #{PARSER_END - PARSER_START:#x}'),
        ('I', 'cmp x9, x10'),
        ('I', 'b.lo {metadata}'),
        ('I', 'ldp x9, x10, [sp], #0x10'),
    ] + hooks.ctor_hook(v, translator) + [
        ('L', 'metadata'),
        ('I', 'ldp x9, x10, [sp], #0x10'),
        ('I', 'stp x29, x30, [sp, #-0x30]!'),
        ('I', f'b {v.ctor.resume:#x}'),
    ]
