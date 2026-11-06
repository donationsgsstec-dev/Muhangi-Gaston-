# Muhangi Gaston — Professional Profile

Founder & Software Engineer, Gaston Software Solutions LLP — Kampala, Uganda.

**Innovation Today. Transformation Tomorrow.**

## Profile page

`index.html` is the self-contained profile page (logo embedded, no external
requests). Open it directly in a browser.

## QR code

`qr/` holds the QR that points at this profile page. The payload is the URL
below, encoded at error correction **H** with the company logo centred in the
code.

```
https://donationsgsstec-dev.github.io/Muhangi-Gaston-/
```

| File | Format |
|------|--------|
| `qr/muhangi-gaston-profile-qr.png` | High-resolution raster |
| `qr/muhangi-gaston-profile-qr.svg` | Vector, self-contained |
| `qr/muhangi-gaston-profile-qr.pdf` | A4 print-ready |
| `qr/qr-target.txt` | The exact encoded URL |

## Poster

`poster/` holds the single-page A4 networking poster — name, role, company,
slogan, six service icons flanking the QR, and the contact footer.

| File | Format |
|------|--------|
| `poster/muhangi-gaston-qr-poster.png` | 3200 × 4526 px |
| `poster/muhangi-gaston-qr-poster.svg` | Vector, self-contained |
| `poster/muhangi-gaston-qr-poster.pdf` | A4, one page |

## Rebuilding

```sh
python3 build_site.py        # writes site/index.html
python3 build_qr_url.py URL  # writes qr/
python3 poster/build_poster.py
```

Requires `Pillow`, `segno`, `cairosvg`, `fonttools`, `pypdfium2`.

## Contact

Kampala, Uganda · info@gss-tec.com · +256 755 274 944 · [gss-tec.com](https://www.gss-tec.com)
