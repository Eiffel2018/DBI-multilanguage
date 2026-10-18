"""Local native ARM64 and archive verification; no Switch/device I/O."""
import hashlib, json, zipfile
import build_912_v74 as b
from trace_mtp_creation_v74 import creation

def main():
    import validate_912_v74  # Existing loader/hook/fallback assertions.
    from build_release import LANGS, VERSION
    report=json.loads((b.OUT/'build-report.json').read_text())
    nro=(b.OUT/'switch/DBI/DBI.nro').read_bytes()
    cases=[(b'1: SD Card',p.encode()) for p in (
      '/switch/breeze/profile_hbl_18.zip','/switch/breeze/qlaunch.zip',
      '/switch/breeze/reeze/ftpexe.nro','/switch/breeze/reeze/hbmenu.nro',
      '/switch/breeze/setptr.txt','/switch/breeze/x30.txt',
      '/Castlevania Belmont’s Curse v1.1.0[0100BA4026E94800][v65536][UPD].nsz',
      '/switch/Игрок/Создание объекта.nsp')]
    cases += [(b'5: SD Card install',b'/test.nsp'),('Custom Игрок'.encode(),b'/test.nsp')]
    for lang in LANGS:
        payload,items=b.compile_translation(b.OUT/f'translations_{lang}_v74.csv')
        mapping=dict(items)
        for name,path in cases:
            t,raw=creation(name,path)
            actual=t.through_sink(nro,payload,report)
            assert actual == b'['+name+b']\n'+mapping['Создание объекта: '.encode()]+path
    t,raw=creation(); assert t.through_sink(nro,b'',report)==raw
    from audit_salty_menu import main as audit_menu
    audit_menu()
    archives=sorted((b.ROOT/'dist').glob(f'*-v{VERSION}-Ready.zip'))
    assert len(archives)==7
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            for line in z.read('SHA256SUMS.txt').decode().splitlines():
                sha,name=line.split('  ',1)
                assert hashlib.sha256(z.read(name)).hexdigest()==sha
    print('PASS: 60 native caller cases, no-table fallback, archive manifests and CRCs. Not a hardware test.')

if __name__=='__main__':main()
