import locale

from bwsite import settings

assert settings.LANGUAGE_CODE == 'de-de', 'Unexpected locale setting.'
locale.setlocale(locale.LC_ALL, 'de')
