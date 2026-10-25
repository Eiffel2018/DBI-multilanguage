"""Run DBI's real INI node parser/query; stub only library/allocator services.

No save data, device I/O, or restore operation is executed. This tests the
metadata lookup that previously failed before restoring could begin.
"""
from pathlib import Path
import argparse, hashlib, json, os, struct
import build_912_v74 as b
from editor_dialog import TARGETS, entries


def main(baseline=None):
    import validate_912_v74 as v

    class Parser(v.Machine):
        def end(self, u, address, size, user):
            if address != v.BASE + v.V.ctor.resume:
                super().end(u, address, size, user)

        def __init__(self, payload, image=None):
            super().__init__(payload)
            if image is not None:
                self.u.mem_write(v.BASE, image)
            self.heap = v.BASE + 0x1500000
            self.events = []
            for addr in (0xb597e0, 0xb59940, 0xb57a20, 0xbbd6c0,
                         0xbce380, 0xbcc920, 0x7403a4, 0xbd2fc0, 0xb92b60):
                self.u.hook_add(v.UC_HOOK_CODE, self.stub,
                               begin=v.BASE+addr, end=v.BASE+addr)
            self.u.hook_add(v.UC_HOOK_CODE, self.ctor,
                           begin=v.BASE+v.V.ctor.addr, end=v.BASE+v.V.ctor.addr)

        def alloc(self, n):
            assert 0 <= n < 0x10000, n
            out = self.heap
            self.heap += (n+31) & ~15
            self.u.mem_write(out, bytes(n+1))
            return out

        def string(self, address):
            p, n = struct.unpack('<QQ', self.u.mem_read(address, 16))
            return bytes(self.u.mem_read(p, n)) if n else b''

        def stub(self, u, pc, size, data):
            addr = pc-v.BASE
            x = [u.reg_read(v.UC_ARM64_REG_X0+i) for i in range(3)]
            result = None
            if addr in (0xb597e0, 0xb59940):
                result = self.alloc(x[0])
            elif addr == 0x7403a4:
                result = self.alloc(struct.unpack('<Q', u.mem_read(x[1], 8))[0]+1)
            elif addr == 0xbbd6c0:
                assert x[2] < 0x10000
                u.mem_write(x[0], bytes(u.mem_read(x[1], x[2])))
            elif addr == 0xbce380:
                result = len(bytes(u.mem_read(x[0], 4096)).split(b'\0')[0])
            elif addr == 0xbcc920:
                result = int(x[0] in b' \t\r\n\v\f')
            elif addr == 0xbd2fc0:
                left, right = (bytes(u.mem_read(p, x[2])) for p in x[:2])
                result = int(left > right)-int(left < right)
            elif addr == 0xb92b60:
                result = self.string(x[0]).find(bytes([x[1] & 255]), x[2])
            if result is not None:
                u.reg_write(v.UC_ARM64_REG_X0, result & ((1 << 64)-1))
            u.reg_write(v.UC_ARM64_REG_PC, u.reg_read(v.UC_ARM64_REG_X30))

        def ctor(self, u, pc, size, data):
            p, n = (u.reg_read(r) for r in (v.UC_ARM64_REG_X1, v.UC_ARM64_REG_X2))
            self.events.append({'source': bytes(u.mem_read(p, min(n, 512))).decode('utf8'),
                                'return_rva': hex(u.reg_read(v.UC_ARM64_REG_X30)-v.BASE)})

        def parse(self, raw, key_value=False):
            self.events = []
            self.u.mem_write(self.input, struct.pack('<QQQQ', self.input+0x1000, len(raw), len(raw), 0))
            self.u.mem_write(self.input+0x1000, raw+b'\0')
            output = self.input+0x4000
            self.run(0x67b4e0 if key_value else 0x67ad40,
                     {v.UC_ARM64_REG_X0: self.input, v.UC_ARM64_REG_X1: 1,
                      v.UC_ARM64_REG_X8: output})
            self.node = struct.unpack('<Q', self.u.mem_read(output, 8))[0]
            assert self.node
            assert self.u.reg_read(v.UC_ARM64_REG_SP) == self.stack
            return (self.string(self.node+8), self.string(self.node+0x28) if key_value else b'')

        def query(self, name):
            # The real query expects the root's node-pointer vector. Use the
            # node just constructed by the real parser; no string replacement.
            root, vector, key = self.input+0x8000, self.input+0x8100, self.input+0x8200
            self.u.mem_write(root, struct.pack('<QQQ', vector, vector+8, vector+8))
            self.u.mem_write(vector, struct.pack('<Q', self.node))
            self.u.mem_write(key, struct.pack('<QQQ', key+0x20, len(name), len(name)))
            self.u.mem_write(key+0x20, name+b'\0')
            self.u.mem_write(v.BASE+0x11ef740, struct.pack('<Q', 1))  # initialized static sentinel
            self.run(0x67a060, {v.UC_ARM64_REG_X0: root, v.UC_ARM64_REG_X1: 1,
                               v.UC_ARM64_REG_X2: key})
            slot = self.u.reg_read(v.UC_ARM64_REG_X0)
            return struct.unpack('<Q', self.u.mem_read(slot, 8))[0] == self.node

    original = (b.ROOT/'DBI.912.original.nro').read_bytes()
    results = {}
    for lang in ('original', 'none', *TARGETS):
        payload = b'' if lang in ('original', 'none') else b.compile_translation(b.OUT/f'translations_{lang}_v74.csv')[0]
        machine = Parser(payload, original if lang == 'original' else None)
        sections = ('Account', 'BackupDate', 'System', 'Device', 'Cache', 'Temporary', 'SDCard')
        for key in sections:
            assert machine.parse(f'[{key}]'.encode())[0] == key.encode(), (lang, key)
            assert machine.query(key.encode()), (lang, key, 'native query')
        for raw in (b'Account=System', b'Device=Account', b'BackupDate=2026-10-25'):
            assert machine.parse(raw, True) == tuple(raw.split(b'=', 1)), (lang, raw)
        dialogs = 0
        if lang in TARGETS:
            mapping = dict(b.compile_translation(b.OUT/f'translations_{lang}_v74.csv')[1])
            assert machine.call('uiansi', b'Account') == mapping.get(b'Account', b'Account')
            for source, target in entries(lang):
                assert machine.call('uiansi', source.encode()) == target.encode(), (lang, source)
                dialogs += 1
            # Gate boundaries: machine strings bypass translation, while callers
            # outside the parser continue translating. Stop at the constructor
            # resume, before the supplied LR could be used as a return target.
            gate = v.Machine(payload)
            from runtime_v76 import PARSER_START, PARSER_END
            for caller, protected in ((PARSER_START-4, False), (PARSER_START, True),
                                      (0x67b0c8, True), (PARSER_END-4, True),
                                      (PARSER_END, False)):
                raw = b'Account'
                gate.u.mem_write(gate.input, raw+b'\0')
                gate.run(v.V.ctor.addr, {v.UC_ARM64_REG_X0: gate.input+0x5000,
                         v.UC_ARM64_REG_X1: gate.input, v.UC_ARM64_REG_X2: len(raw),
                         v.UC_ARM64_REG_X30: v.BASE+caller,
                         v.UC_ARM64_REG_X9: 0x123456, v.UC_ARM64_REG_X10: 0xabcdef})
                p, n = (gate.u.reg_read(r) for r in (v.UC_ARM64_REG_X1, v.UC_ARM64_REG_X2))
                assert bytes(gate.u.mem_read(p, n)) == (raw if protected else mapping.get(raw, raw))
                assert gate.u.reg_read(v.UC_ARM64_REG_SP) == gate.stack-0x30
                if protected:
                    assert gate.u.reg_read(v.UC_ARM64_REG_X9) == 0x123456
                    assert gate.u.reg_read(v.UC_ARM64_REG_X10) == 0xabcdef
        results[lang] = {'native_sections_and_queries': len(sections), 'native_key_value_nodes': 3,
                         'dialog_wrapper_cases': dialogs, 'ctor_gate_boundary_cases': 5 if lang in TARGETS else 0,
                         'ui_account_label_preserved': lang in TARGETS}
    reproduction = None
    if baseline:
        payload = b.compile_translation(b.OUT/'translations_zhtw_v74.csv')[0]
        old = Path(baseline).read_bytes()
        machine = Parser(payload, old)
        name, _ = machine.parse(b'[Account]')
        found = machine.query(b'Account')
        assert name == '帳戶'.encode() and not found
        reproduction = {'nro_sha256': hashlib.sha256(old).hexdigest(), 'parsed_name': name.decode(),
                        'native_Account_lookup_succeeded': found}
    out = Path(os.environ.get('TEMP', r'R:\Temp'))/'dbi-restore-v76'
    out.mkdir(parents=True, exist_ok=True)
    report = {'result': 'PASS', 'nro_sha256': hashlib.sha256(v.nro).hexdigest(),
              'scope': 'Native INI node parser and lookup with allocator/libc stubs; UI wrapper for screenshot-derived dialog spelling/newline variants. No save restore or Switch I/O executed.',
              'baseline_reproduction': reproduction, 'cases': results}
    (out/'restore-dialog-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print('PASS: native metadata parsing/query and editor-dialog translation; report:', out/'restore-dialog-report.json')


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--baseline', type=Path)
    main(args.parse_args().baseline)
