# DBI multilanguage

Unofficial **DBI 912** localization maintained by **Eiffel2018**.

[Download ready-to-use packages](https://github.com/Eiffel2018/DBI-multilanguage/releases/latest)

English, Traditional Chinese, Simplified Chinese, Japanese, French and Spanish.
Each language package contains a patched `DBI.nro`, `translation.bin`, default
configuration, localized instructions and upstream notices. The combined package
defaults to English and includes all six translation tables.

## Install / update

1. Completely exit DBI.
2. Extract the chosen ZIP and copy its `switch` folder to the SD card root.
3. Replace **both** `/switch/DBI/DBI.nro` and `/switch/DBI/translation.bin`.
   You can keep your existing `dbi.config`.
4. Restart DBI.

To switch languages in the combined package, copy
`translations/translation_<language>.bin` over `/switch/DBI/translation.bin`
and restart DBI. Language codes: `en`, `zhtw`, `zhcn`, `jp`, `fr`, `es`.
The same patched NRO works with all six tables.

The official updater can overwrite the patched NRO. Reapply the matching NRO
and BIN after updating. These patches target **912 only**.

## What v7.5 changes

Adds the missing **Add to SaltyNX exclusions** and **SaltyNX patches...** menu
translations in all six languages. The NRO is unchanged from v7.4; update
`translation.bin` and restart DBI. From older versions, replace both files.

## What v7.4 changed

Fixes an untranslated MTP `Creating object:` message when DBI outputs the storage
heading and the message in a single multiline write. The runtime now preserves
whole-message translations first, then translates individual logical lines when
needed. Storage names, file paths and control characters are preserved.
**Updating translation.bin alone will not apply this fix.**

Includes previous SAVE and Activity Log tab fixes, statistics column headings,
installation and cleanup messages, update prompts, progress units and Chinese
spacing corrections. See [release notes](CHANGELOG.md).

## Validation status

Local ARM64 emulation and package checks passed for all six languages, including
60 native MTP caller cases. Recorded reports are in `validation/v7.4/`.
These tests use stubs for device/file I/O and are **not Switch hardware tests**.
English v7.2 was previously confirmed on a Switch; v7.4/v7.5 await hardware feedback. Native drawing tests for v7.5 are in `validation/v7.5/`.
This project does not claim every possible Russian string is covered and is not
a security audit of DBI. Translation changes do not fix interrupted transfers.

For a remaining Russian string, open an issue with a screenshot, package version,
language, and the steps that opened the screen. Do not include console keys.

## Build from source

Use Python 3.12. Install dependencies with `python -m pip install -r requirements.txt`.
Download the original [DBI 912 Russian NRO](https://github.com/rashevskyv/dbi/releases/tag/912ru),
save it here as `DBI.912.original.nro`, then run:

```sh
python build_release.py
python verify_release.py
```

The builder rejects any input whose SHA-256 differs from
`e77da77f95a24f94fb39df23513961846a75d07aa2f970f39846ed7bbbd22bd2`.
Ready-to-use archives are written to `dist/`.
The original NRO is not stored in Git. The pinned runtime source is vendored
under `dbi-translate-main/src`; no devkitA64 installation is required.

## Credits and licensing

- DBI by **duckbill**, hosted/maintained by [rashevskyv](https://github.com/rashevskyv/dbi).
- Runtime foundation: [0xroast/dbi-translate](https://github.com/0xroast/dbi-translate),
  recorded revision `e3e5a1f3db26005d9712669adf38f26a13d0e7f3` (MIT).
- Translation dataset: [rashevskyv/DBIPatcher](https://github.com/rashevskyv/DBIPatcher),
  with local corrections for DBI 912. Related work: BohdanBuinich/dbi-i18n and Morce3232.
- DBI 912 integration, corrections and packaging: **Eiffel2018**.

The tooling's MIT license does not relicense the upstream DBI executable.
Original notices are retained in each package. The hidden Shadok game's story
translations inherit DBIPatcher's deliberately rewritten parody; they are not
a literal translation of the original DBI story. See [NOTICE](NOTICE).
