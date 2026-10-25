"""Experimental DBI 912 localization; MIT runtime from 0xroast/dbi-translate.
Uses return-following alignment padding, preserving NRO segment addresses.
"""
from pathlib import Path
import sys, struct, re, hashlib, json, array
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'python-deps'),str(ROOT/'dbi-translate-main/src')]
from dbi_translate.asm import assemble, enc_b, enc_bl, enc_adrp, enc_ldr_lit
from dbi_translate import runtime, hooks, table
from dbi_translate.versions import Version, Site
from dataclasses import replace
from runtime_v3 import safe_lookup, safe_loader
from runtime_v74 import make_ansi
from runtime_v76 import make_ctor
from runtime_v4 import make_token, make_progress
from runtime_v6 import make_ui_field
from runtime_v61 import make_tab_text
from runtime_v71 import make_tab_render, make_tab_label
from runtime_v72 import make_statistics_width
from runtime_v5 import make_fmt_args, make_draw_text
OUT=ROOT/"mtp-native-v7.4"
RENDER1=Site(0x67dd90,0xa9bc7bfd,0x67dd94,"B")
RENDER2=Site(0x67e020,0xa9bc7bfd,0x67e024,"B")
APPEND1=Site(0x14e420,0xa9bd7bfd,0x14e424,"B")
APPEND2=Site(0x3c6b70,0xa9bd7bfd,0x3c6b74,"B")
DRAW=Site(0x1aff88,0xa9b77bfd,0x1aff8c,"B")
TAB_CTOR=Site(0x5bc160,0x91004005,0x5bc164,"B")
SINK2=Site(0x67dec0,0xaa0103f6,0x67dec4,"BL")

SHA='e77da77f95a24f94fb39df23513961846a75d07aa2f970f39846ed7bbbd22bd2'
V=Version('912',(0xbecdbc,0xbed000),0x1278a00,0x1278a20,0x1278a80,0x147510,
    Site(0x147510,0xa9b87bfd,0x147514,'B'),Site(0x6fca60,0xd10983ff,0x6fca64,'B'),
    Site(0x1b2650,0xa9b77bfd,0x1b2654,'B'),Site(0x7e780,0xa9bd7bfd,0x7e784,'B'),
    Site(0x67e160,0xaa0103f6,0x67e164,'BL'))
SITES={k:getattr(V,k) for k in ('reader','fmt','glog','ctor','sink')}
SITES.update(draw=DRAW,sink2=SINK2,render1=RENDER1,render2=RENDER2,append1=APPEND1,append2=APPEND2)
TAB_RENDER=Site(0x50bf50,0xa9b07bfd,0x50bf54,'B')
SITES['tabctor']=TAB_CTOR
SITES['tabrender']=TAB_RENDER
SITES['statplayer']=Site(0x3e0588,0x97f55236,0x3e058c,'BL')
SITES['statsessions']=Site(0x3e0800,0x97f55198,0x3e0804,'BL')
SITES['stattime']=Site(0x3e0a54,0x97f55103,0x3e0a58,'BL')

def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value
def pc_target(w,pc):
    if w&0x7c000000==0x14000000:return 'branch',pc+signed(w&0x3ffffff,26)*4
    if w&0xff000010==0x54000000 or w&0x7e000000==0x34000000:return 'cond',pc+signed((w>>5)&0x7ffff,19)*4
    if w&0x7e000000==0x36000000:return 'test',pc+signed((w>>5)&0x3fff,14)*4
    if w&0x9f000000 in (0x10000000,0x90000000):
        d=signed(((w>>29)&3)|(((w>>5)&0x7ffff)<<2),21)
        return ('adrp',(pc&~0xfff)+d*4096) if w&0x80000000 else ('adr',pc+d)
    if w&0x3b000000==0x18000000:return 'literal',pc+signed((w>>5)&0x7ffff,19)*4
    return None
def relocate(w,old,new,mapping):
    t=pc_target(w,old)
    if not t:return w
    kind,target=t
    if kind!='adrp':target=mapping.get(target,target)
    if kind=='branch':
        assert abs(target-new)<1<<27
        return enc_bl(new,target) if w&0x80000000 else enc_b(new,target)
    if kind in ('cond','literal','test'):
        bits=14 if kind=='test' else 19;delta=target-new
        assert delta%4==0 and -(1<<(bits+1))<=delta<(1<<(bits+1))
        mask=((1<<bits)-1)<<5
        return (w&~mask)|(((delta//4)&((1<<bits)-1))<<5)
    if kind=='adrp':return enc_adrp(new,target,w&31)
    delta=target-new
    assert -(1<<20)<=delta<(1<<20)
    return (w&0x9f00001f)|((delta&3)<<29)|(((delta>>2)&0x7ffff)<<5)

def compile_translation(csv_path):
    pairs=table.load_csv(csv_path)
    # Reserve a NUL byte even when the longest string is exactly four-byte aligned.
    ruoff=4;troff=4+((max(len(r) for r,t in pairs)+4)&~3)
    stride=troff+((max(len(t) for r,t in pairs)+4)&~3)
    binary=bytearray(b'DBITRNS\0'+struct.pack('<6I',2,len(pairs),stride,ruoff,troff,0))
    for ru,tr in pairs:
        entry=bytearray(stride);struct.pack_into('<HH',entry,0,len(ru),len(tr));entry[4:4+len(ru)]=ru;entry[troff:troff+len(tr)]=tr;binary.extend(entry)
    assert table.parse_table(bytes(binary))==dict(pairs)
    return bytes(binary),pairs

def build():
    original=(ROOT/'DBI.912.original.nro').read_bytes()
    assert hashlib.sha256(original).hexdigest()==SHA
    data=bytearray(original)
    for s in tuple(SITES.values()):assert struct.unpack_from('<I',data,s.addr)[0]==s.insn
    path=V.cave[0];pool=(path+len(runtime.PATH_STR)+7)&~7;start=pool+8
    blocks={};code=bytearray();addr=start
    def emit(name,program):
        nonlocal addr
        blocks[name]=addr;b=assemble(program,addr);code.extend(b);addr+=len(b)
    emit('lookup',safe_lookup(runtime.shared_lookup(V,pool)))
    emit('loader',safe_loader(runtime.loader(V,path,pool)))
    emit('fmtargs',make_fmt_args(blocks['lookup']))
    fmt=runtime.make_fmt(V,blocks['lookup'])
    # Replace the original sole-C-string argument handler with a bounded packed handler.
    first=next(i for i,p in enumerate(fmt) if p==('I','cmp x2, #0xc'))
    last=next(i for i,p in enumerate(fmt) if p==('L','fargd'))
    fmt=fmt[:first]+[('I',f"bl {blocks['fmtargs']:#x}")]+fmt[last+1:]
    emit('fmt',fmt)
    pfx=runtime.make_pfxsfx(V,blocks['lookup'])
    pfx=[('I','cmp x20, #0x100') if x==('I','cmp x20, #0x80') else x for x in pfx]
    emit('pfxsfx',pfx)
    emit('token',make_token(blocks['lookup']))
    emit('progress',make_progress(V,blocks['token'],blocks['pfxsfx']))
    emit('ansi',make_ansi(V,blocks['progress'],blocks['lookup']))
    for name,func in [('glog',hooks.glog_hook),('ctor',make_ctor),('sink',hooks.sink_hook)]:emit(name,func(V,blocks['ansi']))
    emit('sink2',hooks.sink_hook(replace(V,sink=SINK2),blocks['ansi']))
    for name,site in [('render1',RENDER1),('render2',RENDER2),('append1',APPEND1),('append2',APPEND2)]:
        program=hooks.glog_hook(replace(V,glog=site),blocks['ansi'])
        program=[('I',f'stp x29, x30, [sp, #-{0x30 if name.startswith("append") else 0x40:#x}]!') if p==('I','stp x29, x30, [sp, #-0x90]!') else p for p in program]
        emit(name,program)
    emit('drawtext',make_draw_text(blocks['lookup'],blocks['ansi']))
    emit('uifield',make_ui_field(V,blocks['lookup'],blocks['drawtext']))
    emit('uiansi',make_ansi(V,blocks['uifield'],blocks['lookup']))
    emit('draw',hooks.glog_hook(replace(V,glog=DRAW),blocks['uiansi']))
    emit('tabtext',make_tab_text(blocks['lookup']))
    tabctor=hooks.ctor_hook(replace(V,ctor=TAB_CTOR),blocks['tabtext'])
    tabctor=[('I','add x5, x0, #0x10') if p==('I','stp x29, x30, [sp, #-0x30]!') else p for p in tabctor]
    emit('tabctor',tabctor)
    emit('tablabel',make_tab_label(blocks['lookup']))
    emit('tabrender',make_tab_render(TAB_RENDER,blocks['tablabel']))
    emit('statwidth',make_statistics_width(blocks['lookup']))
    for name in ('statplayer','statsessions','stattime'):blocks[name]=blocks['statwidth']
    emit('reader',hooks.reader_hook(V,blocks['loader']))
    # Only zero padding immediately after RET, ending at a 16-byte function boundary.
    candidates=[]
    for m in re.finditer(b'\0{8,}',original[0xb6d000:0xbed000]):
        s=(m.start()+0xb6d000+3)&~3;e=(m.end()+0xb6d000)&~3
        if e<=path and e%16==0 and struct.unpack_from('<I',original,s-4)[0]&0xfffffc1f==0xd65f0000:candidates.append((s,e))
    # Reject direct control-flow, literal reads and immediate ADRP+ADD addresses into gaps.
    words=array.array('I');words.frombytes(original[:0xbed000]);targets=set()
    for idx,w in enumerate(words):
        pc=idx*4;t=pc_target(w,pc)
        if t and t[0]!='adrp':targets.add(t[1])
        if t and t[0]=='adrp':
            reg=w&31
            for nw in words[idx+1:idx+7]:
                if nw&0xffc00000==0x91000000 and (nw>>5)&31==reg:targets.add(t[1]+((nw>>10)&0xfff))
    candidates=[(s,e) for s,e in candidates if not any(s<=t<e for t in targets)]
    regions=[(start,0xbed000)]+sorted(candidates,key=lambda p:p[1]-p[0],reverse=True)
    mapping={};used=[];cursor=0
    for s,e in regions:
        n=min((e-s-4)//4,(len(code)-cursor)//4)
        if n<=0:continue
        for j in range(n):mapping[start+cursor+j*4]=s+j*4
        used.append((s,s+n*4));cursor+=n*4
        if cursor==len(code):break
    assert cursor==len(code),'insufficient verified padding'
    changed=[]
    data[path:path+32]=runtime.PATH_STR;struct.pack_into('<Q',data,pool,runtime.STATE_MAGIC)
    for old,new in mapping.items():
        w=struct.unpack_from('<I',code,old-start)[0];rw=relocate(w,old,new,mapping)
        struct.pack_into('<I',data,new,rw)
        if (t:=pc_target(w,old)):
            expected=t[1] if t[0]=='adrp' else mapping.get(t[1],t[1])
            assert pc_target(rw,new)==(t[0],expected)
    for i,(s,e) in enumerate(used[:-1]):struct.pack_into('<I',data,e,enc_b(e,used[i+1][0]))
    for name in tuple(SITES):
        site=SITES[name];dest=mapping[blocks[name]]
        struct.pack_into('<I',data,site.addr,(enc_bl if site.entry=='BL' else enc_b)(site.addr,dest))
    # Extend startup's cleared BSS to include the previously unused last-page tail.
    mod=struct.unpack_from('<I',data,4)[0]
    old_bss_end=mod+struct.unpack_from('<I',data,mod+12)[0]
    assert old_bss_end==0x1278988 and old_bss_end<V.state<V.persist<V.scratch+0x400<=0x1279000
    struct.pack_into('<I',data,mod+12,0x1279000-mod)
    allowed=[(path,start)]+[(s,e+4) for s,e in used]+[(s.addr,s.addr+4) for s in tuple(SITES.values())]+[(mod+12,mod+16)]
    for i,(a,b) in enumerate(zip(original,data)):
        if a!=b:
            assert any(s<=i<e for s,e in allowed),f'unexpected edit at {i:x}'
            changed.append(i)
    binary,pairs=compile_translation(OUT/'translations_en_v74.csv')
    out=OUT/'switch/DBI';out.mkdir(parents=True,exist_ok=True)
    (out/'DBI.nro').write_bytes(data);(out/'translation.bin').write_bytes(binary)
    report={'version':912,'status':'experimental - no Switch runtime test','original_sha256':SHA,
      'patched_sha256':hashlib.sha256(data).hexdigest(),'table_sha256':hashlib.sha256(binary).hexdigest(),
      'translation_pairs':len(pairs),'runtime_bytes':len(code),'padding_fragments':len(used),'changed_bytes':len(changed),
      'blocks':{k:hex(mapping[v]) for k,v in blocks.items()},'regions':[(hex(s),hex(e)) for s,e in used],
      'hook_sites':{k:hex(SITES[k].addr) for k in tuple(SITES)},
      'bss_clear_extended_from':hex(old_bss_end),'bss_clear_extended_to':'0x1279000'}
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return bytes(data),bytes(binary),report,mapping,blocks
if __name__=='__main__':build()
