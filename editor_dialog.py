"""Correctly spelled unsaved-dialog variants visible in the user's screenshot.

The older dataset spells несохранёные with a missing н. Keep that old key for
compatibility and cover both е/ё and LF/CRLF in the corrected spellings.
"""
TARGETS = {
    'en': ('There are unsaved changes.', 'Do you want to save them?',
           'Save', 'Exit without saving', 'Other button - Cancel'),
    'zhtw': ('有尚未儲存的變更。', '是否儲存？',
             '儲存', '不儲存並離開', '其他按鈕 - 取消'),
    'zhcn': ('有尚未保存的更改。', '是否保存？',
             '保存', '不保存并退出', '其他按键 - 取消'),
    'jp': ('未保存の変更があります。', '保存しますか？',
           '保存', '保存せずに終了', 'その他のボタン - キャンセル'),
    'fr': ('Des modifications ne sont pas enregistrées.', 'Voulez-vous les enregistrer ?',
           'Enregistrer', 'Quitter sans enregistrer', 'Autre touche - Annuler'),
    'es': ('Hay cambios sin guardar.', '¿Quieres guardarlos?',
           'Guardar', 'Salir sin guardar', 'Otro botón - Cancelar'),
}


def entries(lang):
    first, question, save, discard, cancel = TARGETS[lang]
    target = f'{first}\n{question}\n\n(+) - {save}\n\n(-) - {discard}\n\n{cancel}'
    for spelling in ('несохранённые', 'несохраненные'):
        source = (f'Есть {spelling} изменения.\nВы хотите их сохранить?'
                  '\n\n(+) - Да, сохранить\n\n(-) - Выйти без сохранения'
                  '\n\nДругая кнопка - Отмена')
        for newline in ('\n', '\r\n'):
            yield source.replace('\n', newline), target.replace('\n', newline)
    # Dialog widgets may send each line separately to the text renderer.
    for spelling in ('несохранённые', 'несохраненные'):
        yield f'Есть {spelling} изменения.', first
    yield 'Вы хотите их сохранить?', question
    yield '(+) - Да, сохранить', f'(+) - {save}'
    yield '(-) - Выйти без сохранения', f'(-) - {discard}'
    yield 'Другая кнопка - Отмена', cancel
