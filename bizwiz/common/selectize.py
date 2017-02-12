"""Support for selectize.js Javascript library."""
from bizwiz.common import media

Media = media.Media(
    css={'all': ('selectize/dist/css/selectize.bootstrap3.css',)},
    js=('selectize/dist/js/standalone/selectize.min.js',)
)
