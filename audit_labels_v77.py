"""Exercise both reported labels through DBI's real UTF-8 drawing function."""
import hashlib, json, os
from pathlib import Path
import build_912_v74 as b
from audit_salty_menu import native_draw_type
from editor_dialog import TARGETS as DIALOGS
from install_labels import SOURCE, TARGETS


def main():
    NativeDraw = native_draw_type()
    results = {}
    for lang, target in TARGETS.items():
        payload, _ = b.compile_translation(b.OUT/f'translations_{lang}_v74.csv')
        machine = NativeDraw(payload)
        title = 'Есть несохранёные изменения.'  # Actual misspelling in the screenshot.
        cases = [(title, DIALOGS[lang][0]), (SOURCE, target)]
        # Same UI label with alignment and a colon; values remain untouched.
        for padding in ('', ' ', '    '):
            for suffix in (':', ': ', ': NAND', ': SD'):
                cases.append((SOURCE+padding+suffix, target+padding+suffix))
        for source, expected in cases:
            raw = source.encode()
            assert machine.draw(raw) == expected.encode(), (lang, source, 'native draw')
            raw = b'\x1b[37;1m'+raw+b'\x1b[0m'
            assert machine.call('uiansi', raw) == b'\x1b[37;1m'+expected.encode()+b'\x1b[0m'
        for raw in ((SOURCE+'.nsp').encode(), ('sdmc:/games/'+SOURCE+'.nsp').encode(),
                    (title+'.txt').encode()):
            assert machine.draw(raw) == raw, (lang, 'filename')
        results[lang] = {'native_draw_cases': len(cases)+3, 'ansi_wrapper_cases': len(cases),
                         'editor_title': DIALOGS[lang][0], 'installation_label': target}
    output = Path(os.environ.get('TEMP', r'R:\Temp'))/'dbi-v7.7'
    output.mkdir(parents=True, exist_ok=True)
    (output/'reported-labels.json').write_text(json.dumps({
        'result': 'PASS', 'nro_sha256': hashlib.sha256((b.OUT/'switch/DBI/DBI.nro').read_bytes()).hexdigest(),
        'scope': 'Native UTF-8 drawing with final glyph-output stub; ANSI bytes at UI wrapper. No install, editor action, device I/O or Switch hardware test.',
        'languages': results}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print('PASS: 102 native draw and 84 ANSI-wrapper cases for both reported labels; filenames unchanged.')


if __name__ == '__main__':
    main()
