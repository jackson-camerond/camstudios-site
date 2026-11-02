#!/usr/bin/env python3
"""Make a personal review link: site/review/data/<code>.json + site/review/p/<code>/ photos.

Usage: new_review.py <first name> "<shoot>" "<date>" <photo> [<photo>]
Prints the link, camstudios.la/review/<code>/ (a personal page with their photo as the link preview).\nAfter editing site/review/index.html, run `new_review.py --pages` to rebuild every personal page. The code is the first name plus 5 random
characters so links can't be guessed. The holiday code is FIRSTNAME20: 20% off, used once by them or one friend,
booked with a deposit by 12/31/26 (the shoot or event can be later).
Needs Pillow for resizing (photos go up at 900px on the long side).
"""
import html, json, os, re, secrets, string, sys
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
    personal_page(code, info)
    print(f"https://camstudios.la/review/{code}/")

def personal_page(code, info):
    """site/review/<code>/index.html: the review page plus link-preview tags with their own photo."""
    page = open(os.path.join(SITE, "index.html")).read()
    who, img = html.escape(info["first"]), f"https://camstudios.la/review/p/{code}/1.jpg"
    title = html.escape(info.get("og_title") or f'{info["first"]}, found these from your shoot')
    tags = (f'<meta name="review-code" content="{code}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="A couple of my favorites and a holiday gift inside. CAM Studios LA">\n'
            f'<meta property="og:image" content="{img}">\n<meta property="og:type" content="website">\n'
            f'<meta property="og:url" content="https://camstudios.la/review/{code}/">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n')
    os.makedirs(os.path.join(SITE, code), exist_ok=True)
    with open(os.path.join(SITE, code, "index.html"), "w") as f:
        f.write(page.replace("<title>", tags + "<title>", 1))

if __name__ == "__main__":
    if sys.argv[1:] == ["--pages"]:  # rebuild every personal page after editing index.html
        for f in sorted(os.listdir(os.path.join(SITE, "data"))):
            personal_page(f[:-5], json.load(open(os.path.join(SITE, "data", f))))
        sys.exit()
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
