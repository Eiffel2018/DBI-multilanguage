"""Build the pinned NRO and minimal ready-to-use language archives."""
from pathlib import Path
import contextlib, hashlib, io, json, shutil, tempfile, zipfile
import build_912_v74 as b

LANGS = {'en':'English','zhtw':'Traditional-Chinese','zhcn':'Simplified-Chinese',
         'jp':'Japanese','fr':'French','es':'Spanish'}
VERSION = '7.5'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    expected = json.loads((b.ROOT/'release_manifest.json').read_text())
    with contextlib.redirect_stdout(io.StringIO()): nro, _, report, _, _ = b.build()
    assert hashlib.sha256(nro).hexdigest() == expected['nro_sha256']
    dist = b.ROOT/'dist'; dist.mkdir(exist_ok=True)
    for lang in (*LANGS, 'six-languages'):
        default = 'en' if lang == 'six-languages' else lang
        staging = tempfile.TemporaryDirectory(prefix='dbi-912-')
        target = Path(staging.name)/f'ready-{lang}'
        shutil.copytree(b.ROOT/'templates'/default, target)
        app = target/'switch/DBI'; app.mkdir(parents=True, exist_ok=True)
        (app/'DBI.nro').write_bytes(nro)
        payload, _ = b.compile_translation(b.OUT/f'translations_{default}_v74.csv')
        assert hashlib.sha256(payload).hexdigest() == expected['table_sha256'][default]
        (app/'translation.bin').write_bytes(payload)
        if lang == 'six-languages':
            for code in LANGS:
                binary, _ = b.compile_translation(b.OUT/f'translations_{code}_v74.csv')
                p=target/'translations'/f'translation_{code}.bin'; p.parent.mkdir(exist_ok=True)
                p.write_bytes(binary)
                shutil.copy2(b.ROOT/'templates'/code/'README.txt', target/f'README-{code}.txt')
        files=sorted(p for p in target.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
        (target/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(target).as_posix()}\n' for p in files), encoding='utf8', newline='\n')
        title='Six-Languages' if lang=='six-languages' else LANGS[lang]
        archive=dist/f'DBI-912-{title}-v{VERSION}-Ready.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(target.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(target).as_posix())
        with zipfile.ZipFile(archive) as z: assert z.testzip() is None
        staging.cleanup()
    (dist/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(dist.glob(f'*-v{VERSION}-Ready.zip'))),encoding='utf8',newline='\n')
    print(f'Built and CRC-checked seven archives; pinned NRO/BIN hashes match v{VERSION}.')

if __name__=='__main__':main()
