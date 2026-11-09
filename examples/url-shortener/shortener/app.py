"""A tiny URL shortener, made up as the system behind the example diagram."""
import sqlite3
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, HTTPServer

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CACHE_LIMIT = 1000


def encode(n):
    code = ""
    while n:
        n, r = divmod(n, len(ALPHABET))
        code = ALPHABET[r] + code
    return code


def decode(code):
    n = 0
    for c in code:
        n = n * len(ALPHABET) + ALPHABET.index(c)
    return n


class Shortener:
    def __init__(self, path="links.db"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, url TEXT NOT NULL)")
        self.cache = OrderedDict()

    def shorten(self, url):
        if not url.startswith(("http://", "https://")):
            raise ValueError("only http and https links can be shortened")
        row = self.db.execute("INSERT INTO links (url) VALUES (?)", (url,))
        self.db.commit()
        # The row id is unique, so the code needs no collision check.
        return encode(row.lastrowid)

    def resolve(self, code):
        if code in self.cache:
            self.cache.move_to_end(code)
            return self.cache[code]
        found = self.db.execute("SELECT url FROM links WHERE id = ?", (decode(code),)).fetchone()
        if found is None:
            return None
        self.cache[code] = found[0]
        if len(self.cache) > CACHE_LIMIT:
            self.cache.popitem(last=False)  # Drop the code used longest ago.
        return found[0]


class Handler(BaseHTTPRequestHandler):
    links = None

    def reply(self, status, body="", location=None):
        self.send_response(status)
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_POST(self):
        if self.path != "/shorten":
            return self.reply(404)
        url = self.rfile.read(int(self.headers["Content-Length"])).decode()
        try:
            self.reply(201, "/" + self.links.shorten(url))
        except ValueError as error:
            self.reply(400, str(error))

    def do_GET(self):
        try:
            url = self.links.resolve(self.path.lstrip("/"))
        except ValueError:  # A character outside the alphabet.
            url = None
        if url is None:
            return self.reply(404)
        self.reply(302, location=url)


if __name__ == "__main__":
    Handler.links = Shortener()
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
