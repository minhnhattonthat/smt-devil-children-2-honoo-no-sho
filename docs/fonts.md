# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| font/en12.txt | rendered once from Tahoma 11px (Windows `tahoma.ttf`, tools/mkfont.py) | Microsoft, proprietary | unchecked: bitmap glyphs only, no font file shipped | 12px dialogue/menu VWF | hand-edited |
| font/en8.txt | the game's own 8x8 font + hand-drawn glyphs (tools/mkfont.py) | game's / MIT | yes, as rendered glyphs | 8px VWF | condensed by hand |
| (graphics, no file) | Tahoma Bold, Arial Black, Impact (Windows fonts; tools/menulabels.py, tools/titlelogo.py) | Microsoft, proprietary | unchecked: rendered pixels only | title logo, menu labels | - |
