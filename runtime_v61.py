"""Translate only the six native tab labels before std::string construction."""
from dbi_translate.asm import movk_seq

def make_tab_text(lookup):
    p=[]
    for n,label in enumerate(('Установленные','Удалённые','Бекапы','Контент','Тикеты','Сохранения')):
        source=label.encode()
        p += [('I',f'cmp x1, #{len(source)}'),('I',f'b.ne {{next{n}}}'),('I','ldr x9, [x0]')]
        p += movk_seq(10,int.from_bytes(source[:8],'little'))
        p += [('I','cmp x9, x10'),('I','b.eq {lookup}'),('L',f'next{n}')]
    p += [('I','ret'),('L','lookup'),('I','stp x29, x30, [sp, #-0x20]!'),
          ('I','stp x0, x1, [sp, #0x10]'),('I',f'bl {lookup:#x}'),('I','cbnz x0, {hit}'),
          ('I','ldp x0, x1, [sp, #0x10]'),('L','hit'),('I','ldp x29, x30, [sp], #0x20'),('I','ret')]
    return p
