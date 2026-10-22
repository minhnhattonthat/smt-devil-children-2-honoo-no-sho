# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| font/en12.txt | rendered from `font/DejaVuSans.ttf` 11px by tools/mkfont.py | Bitstream Vera / DejaVu (`font/LICENSE-DejaVu.txt`) | yes, as rendered glyphs | 12px dialogue/menu VWF | 25 glyphs redrawn narrower (`EN12_HAND`) to keep the widths the script was fitted to |
| font/en8.txt | the game's own 8x8 font + hand-drawn glyphs (tools/mkfont.py) | game's / MIT | yes, as rendered glyphs | 8px VWF | condensed by hand |
| font/LiberationSans-Bold.ttf | https://github.com/liberationfonts/liberation-fonts 2.1.5 | OFL 1.1 (`font/LICENSE-Liberation.txt`) | yes, as rendered glyphs | field menu labels (tools/menulabels.py), "Book of Fire" (tools/titlelogo.py) | - |
| font/ArchivoBlack-Regular.ttf | https://github.com/google/fonts/tree/main/ofl/archivoblack | OFL 1.1 (`font/LICENSE-ArchivoBlack.txt`) | yes, as rendered glyphs | "SHIN MEGAMI TENSEI" (tools/titlelogo.py) | - |
| font/Anton-Regular.ttf | https://github.com/googlefonts/AntonFont | OFL 1.1 (`font/LICENSE-Anton.txt`) | yes, as rendered glyphs | "DEMIKIDS" (tools/titlelogo.py) | - |
