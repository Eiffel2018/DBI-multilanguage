"""ARM64 runtime tests. Native file I/O is stubbed; this is not a Switch test."""
from pathlib import Path
import sys,json,struct,random
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'python-deps'),str(ROOT/'dbi-translate-main/src')]
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from build_912_v74 import V, SINK2, RENDER1, RENDER2, APPEND1, APPEND2, DRAW, TAB_CTOR, TAB_RENDER
from dbi_translate.runtime import STATE_MAGIC
from dbi_translate.table import parse_table

BASE=0x7100000000
report=json.loads((ROOT/'mtp-native-v7.4/build-report.json').read_text())
binary=(ROOT/'mtp-native-v7.4/switch/DBI/translation.bin').read_bytes()
nro=(ROOT/'mtp-native-v7.4/switch/DBI/DBI.nro').read_bytes()
pairs=parse_table(binary)
class Machine:
    def __init__(self,payload=binary):
        self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.u.mem_map(BASE,0x1c00000)
        self.u.mem_write(BASE,nro);self.payload=payload
        self.table=BASE+0x1400000;self.input=BASE+0x1600000;self.stop=BASE+0x1800000
        self.stack=BASE+0x1a00000;self.reads=0;self.stopped=False
        if payload:self.u.mem_write(self.table,payload)
        # Run the actual native BSS-zeroing function called by crt0, stopping before relocations.
        self.u.mem_write(BASE+0x1278000,b'\xa5'*0x1000)
        self.u.hook_add(UC_HOOK_CODE,self.zero_mem,begin=BASE+0xbc7d80,end=BASE+0xbc7d80)
        self.u.hook_add(UC_HOOK_CODE,self.end,begin=BASE+0xaf0b4c,end=BASE+0xaf0b4c)
        self.u.hook_add(UC_HOOK_CODE,self.reader,begin=BASE+V.reader.resume,end=BASE+V.reader.resume)
        self.u.hook_add(UC_HOOK_CODE,self.end,begin=self.stop,end=self.stop)
        for s in (V.fmt,V.glog,V.ctor,V.sink,SINK2,RENDER1,RENDER2,APPEND1,APPEND2,DRAW,TAB_CTOR, TAB_RENDER):self.u.hook_add(UC_HOOK_CODE,self.end,begin=BASE+s.resume,end=BASE+s.resume)
        self.run(0xaf0b00,{UC_ARM64_REG_X0:BASE,UC_ARM64_REG_X1:BASE+0xf0})
        assert self.u.mem_read(BASE+V.state,0x20)==b'\0'*0x20
        self.run(int(report['blocks']['loader'],16),{})
    def zero_mem(self,u,address,size,user):
        ptr=u.reg_read(UC_ARM64_REG_X0);value=u.reg_read(UC_ARM64_REG_X1)&255;n=u.reg_read(UC_ARM64_REG_X2)
        u.mem_write(ptr,bytes([value])*n);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_X30))
    def end(self,u,address,size,user):self.stopped=True;u.emu_stop()
    def reader(self,u,address,size,user):
        self.reads+=1
        assert u.reg_read(UC_ARM64_REG_X0)==32
        assert bytes(u.mem_read(u.reg_read(UC_ARM64_REG_X1),32))==b'sdmc:/switch/DBI/translation.bin'
        out=u.reg_read(UC_ARM64_REG_X8)
        ptr=self.table if self.payload else out+16
        u.mem_write(out,struct.pack('<QQQQ',ptr,len(self.payload or b''),0,0))
        sp=u.reg_read(UC_ARM64_REG_SP);fp,lr=struct.unpack('<QQ',u.mem_read(sp,16))
        u.reg_write(UC_ARM64_REG_X29,fp);u.reg_write(UC_ARM64_REG_X30,lr);u.reg_write(UC_ARM64_REG_SP,sp+0x80);u.reg_write(UC_ARM64_REG_PC,lr)
    def run(self,offset,regs):
        u=self.u;self.stopped=False
        u.reg_write(UC_ARM64_REG_SP,self.stack);u.reg_write(UC_ARM64_REG_X30,self.stop)
        for r,val in regs.items():u.reg_write(r,val)
        u.emu_start(BASE+offset,self.stop+4,count=15000000)
        assert self.stopped,f'instruction budget exhausted: {offset:x}, pc={u.reg_read(UC_ARM64_REG_PC):x}'
    def call(self,name,text):
        self.u.mem_write(self.input,text+b'\0')
        self.run(int(report['blocks'][name],16),{UC_ARM64_REG_X0:self.input,UC_ARM64_REG_X1:len(text)})
        ptr=self.u.reg_read(UC_ARM64_REG_X0);n=self.u.reg_read(UC_ARM64_REG_X1)
        return bytes(self.u.mem_read(ptr,n)) if ptr else None

m=Machine();assert m.reads==1
m.run(int(report['blocks']['loader'],16),{});assert m.reads==1
main=['Главное меню','Просмотр SD карты','Инструменты','Просмотр сохранений','Выход','Да','Нет','Настройки DBI']
selected=[s.encode() for s in main if s.encode() in pairs]+random.Random(912).sample(list(pairs),24)
for ru in selected:assert m.call('lookup',ru)==pairs[ru]
assert m.call('lookup',b'NO_SUCH_KEY') is None
assert m.call('pfxsfx',b'NO_SUCH_KEY')==b'NO_SUCH_KEY'
for ru in selected[:8]:assert m.call('pfxsfx',ru)==pairs[ru]
prefix='Записано: '.encode()
if prefix in pairs:
    assert m.call('pfxsfx',prefix+b'123 MB')==pairs[prefix]+b'123 MB'
    assert m.call('pfxsfx',b'\r'+prefix+b'123 MB')==b'\r'+pairs[prefix]+b'123 MB'
# All four UI consumers enter through their patched original instructions.
ru=next(r for r in pairs if r.decode()=='Да');tr=pairs[ru]
for name in ('ctor','glog','sink'):
    m.u.mem_write(m.input,ru+b'\0')
    regs={UC_ARM64_REG_X0:0x1234,UC_ARM64_REG_X1:m.input if name=='ctor' else len(ru),
          UC_ARM64_REG_X2:len(ru) if name=='ctor' else m.input,UC_ARM64_REG_X3:0x5678}
    m.run(getattr(V,name).addr,regs)
    ptr=m.u.reg_read(UC_ARM64_REG_X1 if name=='ctor' else UC_ARM64_REG_X2)
    n=m.u.reg_read(UC_ARM64_REG_X2 if name=='ctor' else UC_ARM64_REG_X1)
    assert bytes(m.u.mem_read(ptr,n))==tr
    assert m.u.reg_read(UC_ARM64_REG_X0)==0x1234
    if name=='glog':assert m.u.reg_read(UC_ARM64_REG_X3)==0x5678
template='Тема : {}'.encode();arg='Нет'.encode()
m.u.mem_write(m.input,template+b'\0');m.u.mem_write(m.input+0x1000,arg+b'\0');m.u.mem_write(m.input+0x2000,struct.pack('<Q',m.input+0x1000))
m.run(V.fmt.addr,{UC_ARM64_REG_X0:m.input,UC_ARM64_REG_X1:len(template),UC_ARM64_REG_X2:12,UC_ARM64_REG_X3:m.input+0x2000,UC_ARM64_REG_X8:0x123456})
argptr=struct.unpack('<Q',m.u.mem_read(m.input+0x2000,8))[0]
assert bytes(m.u.mem_read(argptr,len(pairs[arg])))==pairs[arg]
assert m.u.reg_read(UC_ARM64_REG_X2)==12 and m.u.reg_read(UC_ARM64_REG_X3)==m.input+0x2000 and m.u.reg_read(UC_ARM64_REG_X8)==0x123456
# Bad/missing tables fail safely and never publish a pointer.
for payload in (None,binary[:16],binary[:-1],b'BADMAGIC'+binary[8:]):
    bad=Machine(payload)
    assert struct.unpack('<Q',bad.u.mem_read(BASE+V.state+0x10,8))[0]!=STATE_MAGIC
    assert bad.call('lookup',ru) is None
print(json.dumps({'status':'PASS','sample_exact_matches':len(selected),'table_entries_roundtripped':len(pairs),
 'native_bss_clear':'emulated with memset stub','loader':'native reader stub, recursion/idempotence checked',
 'hooks':['ctor','fmt/argument','glog','sink'],'prefix_suffix':'numeric middle and CR prefix checked',
 'bad_tables':4,'switch_runtime_tested':False},indent=2))
