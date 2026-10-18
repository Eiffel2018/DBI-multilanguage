"""Recognize interior line controls before translating native multiline logs."""
from runtime_v3 import make_ansi as legacy_make_ansi

def make_ansi(v,matcher,lookup):
 code=legacy_make_ansi(v,matcher)
 at=code.index(('L','scan'))
 stop=code.index(('L','segmented'))
 # Previously only ESC triggered segmentation after the first character. MTP
 # combines its ASCII storage heading, LF, and localized message in one write.
 # Preserve whole-message dictionary entries before using the existing bounded,
 # control-preserving path for interior CR/LF/TAB. ESC keeps its original path.
 part=code[at:stop]
 needle=[('I','cmp w10, #0x1b'),('I','b.ne {scan}')]
 i=next(i for i in range(len(part)-1) if part[i:i+2]==needle)
 part[i:i+2]=[
  ('I','cmp w10, #0x1b'),('I','b.eq {segmented}'),
  ('I','cmp w10, #0x20'),('I','b.hs {scan}'),
  ('I',f'bl {lookup:#x}'),('I','cbnz x0, {out}'),
  ('I','mov x0, x19'),('I','sub x1, x20, x19'),('I','b {segmented}')]
 return code[:at]+part+code[stop:]
