class Media:
    """Utility class allowing to combine media at form level.

    If media is given at form level, since no specific widgets have been used, if often requires
    combining JS and CSS. This class implements the __add__ operator to simplify this.

    Use:
        Media = media.Media(js=..., css=...) + media.Media(js=..., css=...)
    """

    def __init__(self, *, js=None, css=None):
        self.js = tuple(js) if js else ()
        self.css = dict(css) if css else {}

    def __add__(self, other):
        js = list(self.js)
        js += [e for e in other.js if e not in js]

        css = {}
        for category, v in self.css.items():
            css_in_category = list(v)
            css_in_category += [e for e in other.css.get(category, ()) if e not in css_in_category]
            css[category] = css_in_category
        for category, v in other.css.items():
            if category not in self.css:
                css[category] = list(v)

        return Media(js=js, css=css)
