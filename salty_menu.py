"""Whole-label translations for the reported SaltyNX game context menu."""
LABELS = {
    'en': ('Add to SaltyNX exclusions', 'SaltyNX patches'),
    'zhtw': ('加入SaltyNX排除清單', 'SaltyNX修補'),
    'zhcn': ('加入SaltyNX排除列表', 'SaltyNX补丁'),
    'jp': ('SaltyNXの除外リストに追加', 'SaltyNXパッチ'),
    'fr': ('Ajouter aux exclusions SaltyNX', 'Correctifs SaltyNX'),
    'es': ('Añadir a exclusiones de SaltyNX', 'Parches SaltyNX'),
}

def entries(lang):
    exclude, patches = LABELS[lang]
    return [('Добавить в исключения SaltyNX', exclude),
            ('Патчи SaltyNX', patches),
            ('Патчи SaltyNX...', patches + '...'),
            ('Патчи SaltyNX…', patches + '…')]
