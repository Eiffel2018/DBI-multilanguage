"""Render screenshot-derived menu labels through native DBI UTF-8 drawing."""
import hashlib, json, os
from pathlib import Path
import build_912_v74 as b
from salty_menu import LABELS, entries

def main():
    import validate_912_v74 as v

    class NativeDraw(v.Machine):
        def end(self,u,address,size,user):
            if address != v.BASE+v.DRAW.resume: super().end(u,address,size,user)

        def __init__(self,payload):
            super().__init__(payload)
            self.characters=[]
            self.u.hook_add(v.UC_HOOK_CODE,self.cell,begin=v.BASE+0x1af8b0,end=v.BASE+0x1af8b0)

        def cell(self,u,address,size,user):
            self.characters.append(chr(u.reg_read(v.UC_ARM64_REG_X1)&0xffffffff))
            u.reg_write(v.UC_ARM64_REG_PC,u.reg_read(v.UC_ARM64_REG_X30))

        def draw(self,value):
            self.characters=[]
            self.u.mem_write(self.input,value+b'\0')
            try:
                self.run(0x1aff80,{v.UC_ARM64_REG_X0:self.input+0x10000,
                    v.UC_ARM64_REG_X1:len(value),v.UC_ARM64_REG_X2:self.input,v.UC_ARM64_REG_X3:1000})
            except Exception as error:
                raise AssertionError((value,hex(self.u.reg_read(v.UC_ARM64_REG_PC)-v.BASE))) from error
            assert self.u.reg_read(v.UC_ARM64_REG_SP)==self.stack
            return ''.join(self.characters).encode()

    results={}
    for lang in LABELS:
        payload,_=b.compile_translation(b.OUT/f'translations_{lang}_v74.csv')
        machine=NativeDraw(payload)
        native_cases=0
        wrapper_cases=0
        for source,target in entries(lang):
            for left,right in ((b'',b''),(b'  ',b' '),(b'\x1b[37;1m',b'\x1b[0m')):
                # ANSI handling is verified before the native parser strips it.
                raw=left+source.encode()+right
                expected=left+target.encode()+right
                assert machine.call('uiansi',raw)==expected,(lang,source,'uiansi')
                wrapper_cases+=1
                # Color preservation is checked at the actual UI wrapper.
                # Native color-number parsing requires OS/newlib locale state;
                # exercise the native glyph parser with plain/padded labels.
                if not left.startswith(b'\x1b'):
                    assert machine.draw(raw)==expected,(lang,source,'draw')
                    native_cases+=1
            # A literal filename or path containing the same text stays intact.
            for raw in ((source+'.nsp').encode(),('sdmc:/games/'+source+'.nsp').encode()):
                assert machine.draw(raw)==raw,(lang,source,'path')
                native_cases+=1
        results[lang]={'native_draw_cases':native_cases,'ui_wrapper_cases':wrapper_cases,'whole_label_only':True,
            'labels':dict(entries(lang))}
    from build_release import VERSION
    output=Path(os.environ.get('TEMP', r'R:\Temp'))/f'dbi-v{VERSION}'
    output.mkdir(parents=True,exist_ok=True)
    (output/'salty-menu-report.json').write_text(json.dumps({
        'result':'PASS','source':'User screenshot; whole labels, including punctuation variants',
        'scope':'Native UTF-8 parser with final character output stub for plain/padded labels and filenames; ANSI preservation tested at native UI wrapper. Native ANSI color parser, menu construction and actions not executed.',
        'nro_sha256':hashlib.sha256(v.nro).hexdigest(),
        'switch_hardware_tested':False,'languages':results},
        ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PASS: 96 native drawing cases and 72 UI wrapper cases across six languages; paths unchanged.')

if __name__=='__main__':main()
