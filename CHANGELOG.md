# DBI 912 localization v7.5

- Translated the previously missing SaltyNX game context menu labels:
  **Add to SaltyNX exclusions** and **SaltyNX patches...**.
- Added all six languages and punctuation variants; matching is limited to
  complete labels so filenames and paths remain unchanged.
- The patched NRO is identical to v7.4. **translation.bin has changed.**
  Replace the BIN and completely restart DBI; from older versions, replace both files.
- Local native drawing regression coverage added. No Switch hardware test was performed.

# DBI 912 localization v7.4

- Fixed remaining Russian `Creating object:` messages during MTP file transfers.
  The native caller combines the storage heading and message in a single write;
  earlier single-line checks did not exercise that boundary.
- Added interior LF/CR/TAB handling while retaining exact multiline translations,
  ANSI colors, storage labels, file paths and safe fallback behavior.
- Retained all six languages and existing SAVE/Activity Log tabs, statistics
  headers, installation/cleanup logs, progress units and Chinese spacing fixes.
- Added native-caller regression coverage and verified seven ready-to-use ZIPs.

**Install the new DBI.nro.** Translation tables are unchanged from v7.3.
Replace both the NRO and BIN, then completely exit and restart DBI.

Local emulation passed; v7.4 has not been tested on Switch hardware.
Complete translation coverage is not claimed. Transfer failures are separate
from localization and are not fixed by this release.
