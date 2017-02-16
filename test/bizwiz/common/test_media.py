from bizwiz.common.media import Media


def test__media__combination():
    m1 = Media(js=('a', 'b', 'c'), css={
        'all': ('d', 'e'),
        'in1': ('f',)
    })
    m2 = Media(js=('a', 'd'), css={
        'all': ('e', 'g'),
        'in2': ('h',)
    })

    m = m1 + m2

    assert len(m.js) == 4
    assert 'a' in m.js
    assert 'b' in m.js
    assert 'c' in m.js
    assert 'd' in m.js
    assert len(m.css['all']) == 3
    assert 'd' in m.css['all']
    assert 'e' in m.css['all']
    assert 'g' in m.css['all']
    assert len(m.css['in1']) == 1
    assert 'f' in m.css['in1']
    assert len(m.css['in2']) == 1
    assert 'h' in m.css['in2']


def test__media__css_order():
    m1 = Media(css={'all': ('a',)})
    m2 = Media(css={'all': ('b',)})

    m = m1 + m2

    assert m.css['all'][0] == 'a'
    assert m.css['all'][1] == 'b'

    m = m2 + m1

    assert m.css['all'][0] == 'b'
    assert m.css['all'][1] == 'a'
