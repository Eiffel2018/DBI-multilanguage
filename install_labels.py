"""Screenshot-reported installation option; translate its label, not values."""
SOURCE = 'Патчить версию в meta'
TARGETS = {
    'en': 'Patch meta version',
    'zhtw': '修補中繼資料版本',
    'zhcn': '修补元数据版本',
    'jp': 'メタデータの版を修正',
    'fr': 'Corriger version méta',
    'es': 'Parchear versión meta',
}


def entries(lang):
    target = TARGETS[lang]
    return [(SOURCE, target), ('@DBI_LABEL:'+SOURCE, target)]
