# Ledger: URL shortener example

The system is made up for this example. Every citation resolves to `shortener/app.py`, and the
checker confirms each one exists.

| Claim | Evidence |
| --- | --- |
| Writes arrive as POST /shorten | `shortener/app.py:62` |
| Only http and https links are accepted | `shortener/app.py:32` |
| A rejected link gets a 400 | `shortener/app.py:69` |
| The URL is inserted as a new row | `shortener/app.py:34` |
| The table holds an integer id and the URL | `shortener/app.py:28` |
| The code is the row id in base62 | `shortener/app.py:37` |
| Row 125 encodes to 21, because 125 = 2 x 62 + 1 | `shortener/app.py:10` |
| The row id is unique, so the code needs no collision check | `shortener/app.py:36` |
| The author gets the short path back | `shortener/app.py:67` |
| Reads arrive as GET /code | `shortener/app.py:71` |
| The code decodes back to the row id | `shortener/app.py:43` |
| A hit is served from the cache | `shortener/app.py:40` |
| A miss runs a SELECT on the table | `shortener/app.py:43` |
| Every answer from the table is cached | `shortener/app.py:46` |
| The cache holds the last 1000 codes | `shortener/app.py:7` |
| The visitor gets a 302 to the long URL | `shortener/app.py:78` |
| How the author shares the link | assumed: outside this system |
