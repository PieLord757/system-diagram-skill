"""Make an excalidraw.com link for a board. Run only when the user asks for a link.

    uv run --quiet --with cryptography python scripts/share.py board.excalidraw

The scene is encrypted here with a fresh key before upload. Only the ciphertext reaches
excalidraw.com, and the key lives in the link's fragment, so anyone with the link can open it.
"""
import base64
import json
import os
import struct
import sys
import urllib.request
import zlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def concat(*bufs):
    out = struct.pack(">I", 1)
    for b in bufs:
        out += struct.pack(">I", len(b)) + b
    return out


def main():
    with open(sys.argv[1], encoding="utf8") as fh:
        data = json.load(fh)
    scene = json.dumps({"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
                        "elements": data["elements"], "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}).encode()
    key, iv = AESGCM.generate_key(bit_length=128), os.urandom(12)
    sealed = AESGCM(key).encrypt(iv, zlib.compress(concat(json.dumps(None).encode(), scene)), None)
    meta = json.dumps({"version": 2, "compression": "pako@1", "encryption": "AES-GCM"}).encode()
    req = urllib.request.Request("https://json.excalidraw.com/api/v2/post/", data=concat(meta, iv, sealed), method="POST",
                                 headers={"Origin": "https://excalidraw.com"})
    with urllib.request.urlopen(req) as resp:
        rid = json.load(resp)["id"]
    print(f"https://excalidraw.com/#json={rid},{base64.urlsafe_b64encode(key).decode().rstrip('=')}")


if __name__ == "__main__":
    main()
