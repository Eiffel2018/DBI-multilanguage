"""Targeted original DBI 912 ARM64 MTP message discovery (no device I/O)."""
from pathlib import Path
import sys,struct,json,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'python-deps'))
from unicorn import *
from unicorn.arm64_const import *
from capstone import *
B=(ROOT/'DBI.912.original.nro').read_bytes()
BASE=0x7100000000; TLS=BASE+0x2000000; STACK=BASE+0x3100000
MD=Cs(CS_ARCH_ARM64,CS_MODE_ARM)

class Trace:
 def __init__(self):
  self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.u.mem_map(BASE,0x4000000);self.u.mem_write(BASE,B)
  self.heap=BASE+0x3400000;self.calls=[];self.stop=None
  self.trace_hook=self.u.hook_add(UC_HOOK_CODE,self.code)
 def alloc(self,n):
  p=self.heap;self.heap+=(n+31)&~15;return p
 def string(self,p,n=None):
  try:
   if n is not None and not 0<=n<8192:return None
   raw=bytes(self.u.mem_read(p,n if n is not None else 256))
   if n is None:raw=raw.split(b'\0')[0]
   return raw.decode('utf8')
  except:return None
 def value(self,p):
  try:a,n=struct.unpack('<QQ',self.u.mem_read(p,16));return self.string(a,n)
  except:return None
 def put(self,p,s):
  raw=s.encode() if isinstance(s,str) else s;q=self.alloc(len(raw)+1);self.u.mem_write(q,raw+b'\0');self.u.mem_write(p,struct.pack('<QQQ',q,len(raw),len(raw)))
 def code(self,u,pc,size,user):
  a=pc-BASE
  if not 0<=a<len(B):self.stop=hex(a);u.emu_stop();return
  w=struct.unpack_from('<I',B,a)[0]
  if w&0xfc000000!=0x94000000:return
  d=w&0x3ffffff;d=d-(1<<26) if d&(1<<25) else d;dest=a+d*4
  x=[u.reg_read(UC_ARM64_REG_X0+i) for i in range(9)]
  if dest==0xae9738:u.reg_write(UC_ARM64_REG_X0,TLS)
  elif dest in (0xb575c0,0xb57a20):pass
  elif dest==0x7403a4:
   n=struct.unpack('<Q',u.mem_read(x[1],8))[0];assert n<8192;u.reg_write(UC_ARM64_REG_X0,self.alloc(n+1))
  elif dest==0x868c14:
   old,n=struct.unpack('<QQ',u.mem_read(x[0],16));assert n<8192 and x[1]<8192
   p=self.alloc(x[1]+1);u.mem_write(p,bytes(u.mem_read(old,n))+b'\0');u.mem_write(x[0],struct.pack('<QQQ',p,n,x[1]))
  elif dest==0x76f758:
   assert x[2]<8192;old=self.value(x[0]);assert old is not None
   self.put(x[0],old.encode()+bytes(u.mem_read(x[1],x[2])))
  elif dest==0x7e780:
   self.put(x[0],bytes(u.mem_read(x[1],x[2])))
  elif dest==0x7a57b4:
   raw=self.value(x[0]).encode();self.put(x[0],raw[:x[1]]+bytes(u.mem_read(x[3],x[4]))+raw[x[1]+x[2]:])
  else:
   rec={'site':hex(a),'dest':hex(dest),'regs':[hex(v) for v in x],
        'strings':{str(i):self.string(p) for i,p in enumerate(x) if self.string(p)},
        'objects':{str(i):self.value(p) for i,p in enumerate(x) if self.value(p)}}
   self.calls.append(rec)
   self.stop=rec;u.emu_stop();return
  u.reg_write(UC_ARM64_REG_PC,pc+4)
 def run(self,start,regs=None):
  for i in range(29):self.u.reg_write(UC_ARM64_REG_X0+i,BASE+0x3000000+i*0x1000)
  self.u.reg_write(UC_ARM64_REG_SP,STACK)
  for r,v in (regs or {}).items():self.u.reg_write(r,v)
  try:self.u.emu_start(BASE+start,BASE+len(B),count=100000)
  except UcError as e:self.stop={'error':str(e),'pc':hex(self.u.reg_read(UC_ARM64_REG_PC)-BASE)}
  return self.stop
 def through_sink(self,nro,payload,build_report):
  """Continue captured native output into real patched sink2 and return its bytes.

  Stops immediately after sink2's translation hook, before native mutex/I/O.
  The unmodified full native buffer remains at its captured pointer.
  """
  u=self.u;incoming={r:u.reg_read(r) for r in (UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2)}
  u.hook_del(self.trace_hook);u.mem_write(BASE,nro)
  table=BASE+0x1400000;sentinel=BASE+0x3fff000
  u.mem_write(table,payload);u.mem_write(BASE+0x1278a00,bytes(0x80))
  def reader(u,pc,size,user):
   out=u.reg_read(UC_ARM64_REG_X8)
   u.mem_write(out,struct.pack('<QQQQ',table,len(payload),0,0))
   sp=u.reg_read(UC_ARM64_REG_SP);fp,lr=struct.unpack('<QQ',u.mem_read(sp,16))
   u.reg_write(UC_ARM64_REG_X29,fp);u.reg_write(UC_ARM64_REG_X30,lr)
   u.reg_write(UC_ARM64_REG_SP,sp+0x80);u.reg_write(UC_ARM64_REG_PC,lr)
  def stop(u,pc,size,user):u.emu_stop()
  hooks=[u.hook_add(UC_HOOK_CODE,reader,begin=BASE+0x147514,end=BASE+0x147514),
         u.hook_add(UC_HOOK_CODE,stop,begin=sentinel,end=sentinel),
         u.hook_add(UC_HOOK_CODE,stop,begin=BASE+0x67dec4,end=BASE+0x67dec4)]
  u.reg_write(UC_ARM64_REG_SP,STACK);u.reg_write(UC_ARM64_REG_X30,sentinel)
  loader=build_report['blocks']['loader'];loader=int(loader,16) if isinstance(loader,str) else loader
  u.emu_start(BASE+loader,sentinel+4,count=5000000)
  assert u.reg_read(UC_ARM64_REG_PC)==sentinel,'loader did not finish'
  for r,v in incoming.items():u.reg_write(r,v)
  u.reg_write(UC_ARM64_REG_SP,STACK);u.reg_write(UC_ARM64_REG_X30,sentinel)
  u.emu_start(BASE+0x67deb0,sentinel+4,count=5000000)
  assert u.reg_read(UC_ARM64_REG_PC)==BASE+0x67dec4,'sink2 did not reach resume'
  p=u.reg_read(UC_ARM64_REG_X2);n=u.reg_read(UC_ARM64_REG_X1)
  result=bytes(u.mem_read(p,n))
  for h in hooks:u.hook_del(h)
  return result

def creation(name=b'1: SD Card',path=b'/switch/breeze/profile_hbl_18.zip'):
 """Execute native prefix, literal initialization/decryption, concatenation and sink call.

 The device/display name and path are supplied fixtures. String allocation,
 reserve, append, insertion and ctor are semantic stubs; TLS and atexit are
 host-independent stubs. All native branch/concatenation order is executed.
 """
 t=Trace();obj=BASE+0x3000000;dev=BASE+0x3002000;container=BASE+0x3003000
 p=t.alloc(len(name)+1);t.u.mem_write(p,name+b'\0')
 t.u.mem_write(dev,struct.pack('<QQQ',0,p,len(name)))
 t.u.mem_write(container,struct.pack('<Q',dev))
 t.u.mem_write(STACK+0x88,struct.pack('<Q',obj))
 t.u.mem_write(obj+0x50,struct.pack('<Q',BASE+0x3004000))
 t.put(STACK+0x130,path)
 stop=t.run(0x2bd974,{UC_ARM64_REG_X25:container})
 assert stop['site']=='0x2bdf6c' and stop['dest']=='0x67deb0',stop
 p=t.u.reg_read(UC_ARM64_REG_X2);n=t.u.reg_read(UC_ARM64_REG_X1)
 raw=bytes(t.u.mem_read(p,n))
 assert raw==b'['+name+b']\n'+'Создание объекта: '.encode()+path
 return t,raw
