#!/usr/bin/env python3
"""Make a personal review link: site/review/data/<code>.json + site/review/p/<code>/ photos.

Usage: new_review.py <first name> "<shoot>" "<date>" <photo> [<photo>]
Prints the link, camstudios.la/review/?c=<code>. The code is the first name plus 5 random
characters so links can't be guessed. The holiday code is FIRSTNAME20: 20% off, used once by them or one friend, book by 12/31/26.
Needs Pillow for resizing (photos go up at 900px on the long side).
"""
import json, os, re, secrets, string, sys
from PIL import Image, ImageOps

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "review")

def main(first, shoot, date, *photos):
    slug = re.sub(r"[^a-z0-9]", "", first.lower())
    code = f"{slug}-{''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(5))}"
    out = os.path.join(SITE, "p", code)
    os.makedirs(out, exist_ok=True)
    names = []
    for n, src in enumerate(photos, 1):
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.thumbnail((900, 900))
        names.append(f"{n}.jpg")
        im.save(os.path.join(out, names[-1]), quality=82, optimize=True, progressive=True)
    info = {"first": first, "shoot": shoot, "date": date, "photos": names, "discount": f"{slug.upper()}20"}
    with open(os.path.join(SITE, "data", f"{code}.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(f"https://camstudios.la/review/?c={code}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
