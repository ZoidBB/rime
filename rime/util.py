import box, codecs, re, translitcodec

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = codecs.encode(word, 'translit/short')
        if word:
            result.append(word)
    return delim.join(result)

class Box(box.Box):
    """
     - Merges on update instead of overriding.
     - Supports loading from TOML
    """

    def update(self, item=None, **kwargs):
        source = Box(item)
        if kwargs:
            source.update(kwargs)

        for key, value in source.items():
            if isinstance(value, dict):
                node = self.setdefault(key, Box())
                node.update(value)
            else:
                self[key] = value
