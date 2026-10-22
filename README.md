# Shin Megami Tensei: DemiKids - Book of Fire English translation

Unofficial English fan translation of **Shin Megami Tensei: Devil Children 2 Honoo no Sho** (Game Boy Advance, Atlus,
2003): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, graphics, release. |
| `asm/`, `font/` | Engine patch (variable-width font hook) and the English fonts. |
| `fixes/` | Review fixes applied to the script. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+ (with Pillow), armips in `tools/armips/`, and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/smt-devil-children-2-honoo-no-sho
cd smt-devil-children-2-honoo-no-sho
# copy your dump to: rom/honoo.gba
#   (8388608 bytes, SHA-1 8c29d6921e7db8b0e71094d32e32066ac13c500d; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/honoo_en.gba
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Atlus's and is included only so
the translation can be checked against it. Shin Megami Tensei: Devil Children is (c) ATLUS; this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
