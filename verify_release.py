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
    from audit_restore_v76 import main as audit_restore
    audit_restore()
    from audit_labels_v77 import main as audit_labels
    audit_labels()
    verify_archives()
    print('PASS: 60 native caller cases, no-table fallback, archive manifests and CRCs. Not a hardware test.')


def verify_archives():
    from build_release import LANGS, VERSION
    expected=json.loads((b.ROOT/'release_manifest.json').read_text())
    archives=sorted((b.ROOT/'dist').glob(f'*-v{VERSION}-Ready.zip'))
    assert len(archives)==7
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert hashlib.sha256(z.read('switch/DBI/DBI.nro')).hexdigest()==expected['nro_sha256']
            default=next((lang for lang,title in LANGS.items()
                          if archive.name==f'DBI-912-{title}-v{VERSION}-Ready.zip'),'en')
            assert hashlib.sha256(z.read('switch/DBI/translation.bin')).hexdigest()==expected['table_sha256'][default]
            for lang in LANGS:
                name=f'translations/translation_{lang}.bin'
                if name in z.namelist():
                    assert hashlib.sha256(z.read(name)).hexdigest()==expected['table_sha256'][lang]
            for line in z.read('SHA256SUMS.txt').decode().splitlines():
                sha,name=line.split('  ',1)
                assert hashlib.sha256(z.read(name)).hexdigest()==sha
    print('PASS: seven archives; pinned NRO/BIN hashes, manifests and CRCs.')

if __name__=='__main__':main()
