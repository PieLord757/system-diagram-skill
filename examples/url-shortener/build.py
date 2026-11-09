"""Build the example diagram: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "skills" / "system-diagram" / "scripts"))
sys.dont_write_bytecode = True

from draw import Scene  # noqa: E402

s = Scene()
s.title("How one short link works", "Written once, read many times. One link, row 125, carried from start to finish.")

# The two people, and the handoff between them.
author = s.person(470, 290, "Author")
visitor = s.person(1700, 290, "Visitor")
s.arrow(author, visitor, "shares the link /21", size=30)
s.tag(1090, 285, "4")
s.boundary(60, 2420, 540, above="the internet", below="one server", label_x=1060)

# The write path runs down the left.
post = s.box(390, 720, 270, 120, "POST /shorten", fill="blue")
s.arrow(author, post, "long URL")
s.tag(690, 750, "1")
s.text(770, 755, "https://example.com/a-long-page", size=28, color="muted")

valid = s.gate(375, 930, 300, 190, "http or https?", size=28)
s.arrow(post, valid, sides="bt")
rejected = s.doc(850, 960, 210, 130, "400 error")
s.arrow(valid, rejected, "no", sides="rl")

insert = s.box(395, 1240, 260, 110, "INSERT the URL", fill="blue", size=30)
s.arrow(valid, insert, "yes", sides="bt")

links = s.store(900, 1470, 440, 250, "SQLite\nlinks table", size=38)
s.arrow(insert, links, "a new row", sides="bl", via=[(525, 1560), (800, 1560)], at=(0.5, 0.36))
s.tag(610, 1480, "2")
s.text(900, 1360, "row 125: https://example.com/a-long-page", size=30)
s.text(860, 1750, "The row id is unique, so the code\nneeds no collision check.", size=30)

encode = s.oval(60, 1210, 280, 150, "Base62 encode", fill="blue", size=30)
s.arrow(links, encode, "id 125", sides="lb", via=[(600, 1660), (200, 1660)], at=(0.76, 0.5))
s.tag(300, 1590, "3")
s.text(235, 1420, "125 = 2 x 62 + 1\nso the code is 21", size=28)
s.arrow(encode, author, "/21", sides="tl", via=[(200, 800), (200, author.cy)])

# The read path runs down the right.
get = s.box(1620, 720, 270, 120, "GET /21\ndecode to 125", fill="green", size=30)
s.arrow(visitor, get, "/21")
s.tag(1910, 750, "5")

in_cache = s.gate(1605, 930, 300, 190, "In the cache?", size=28)
s.arrow(get, in_cache, sides="bt")

cache = s.store(2060, 930, 300, 190, "Cache: last\n1000 codes", size=28)
s.arrow(in_cache, cache, "hit", sides="rl")

s.arrow(in_cache, links, "miss: SELECT", sides="br", via=[(1755, 1560), (1400, 1560)], at=(0.5, 0.36))
s.tag(1540, 1480, "6")
s.arrow(links, cache, "long URL", sides="rb", via=[(1700, 1660), (2210, 1660)], at=(0.76, 0.5))
s.text(1810, 1290, "Every answer goes\nin the cache, so the\nnext visit skips the table.", size=28)

redirect = s.box(2070, 650, 280, 120, "302 to the long URL", fill="green", size=30)
s.arrow(cache, redirect, sides="tb")
s.arrow(redirect, visitor, "302", sides="tr", via=[(2210, 520), (2210, visitor.cy)])
s.tag(2370, 680, "7")

# The key.
s.text(1130, 950, "blue: handles a write", size=30, color="blue")
s.text(1130, 1000, "green: handles a read", size=30, color="green")
s.text(1130, 1050, "cylinder: where data rests", size=30, color="teal")

s.save(str(HERE / "url-shortener.excalidraw"))
