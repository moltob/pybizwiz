import locale

from django.utils import translation

# make django language also effective for current locale
_language = translation.get_language()
_locale = translation.to_locale(_language)
locale.setlocale(locale.LC_ALL, _locale[:2])  # meager attempt to get around
