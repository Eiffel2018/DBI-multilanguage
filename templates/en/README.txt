v7.5 adds the missing SaltyNX exclusion and patches menu labels. The NRO is unchanged from v7.4; translation.bin has changed. Replace both files if upgrading from an older release. Local tests only; hardware confirmation pending.

﻿DBI 912 unofficial translation v7.4 — English

Fixes the actual MTP multiline output: [storage name]\nСоздание объекта: path. The v7.3 hardware failure was reproduced through the native caller; v7.4 passes local native, multiline and screenshot checks. v7.4 was not tested on Switch hardware. The English v7.2 hardware confirmation is historical only; this does not prove all Russian messages are translated.
The v7.4 NRO changed from v7.3. Install or update by replacing both /switch/DBI/DBI.nro and translation.bin; you may keep dbi.config.


Install: completely exit DBI. Copy the switch folder to the SD card root,
replacing BOTH /switch/DBI/DBI.nro and translation.bin. Restart DBI.
You may keep your existing dbi.config instead of replacing it.

Includes the SAVE and Activity Log tab fixes, statistics column headers,
installation/cleanup messages, update prompts and MiB/s progress labels.
All six languages use the same NRO. The English v7.2 build was confirmed
working on a Switch by the requesting user. All six tables passed local checks.
This does not establish that every possible Russian message is covered.

In the combined package, copy translations/translation_<language>.bin to
/switch/DBI/translation.bin, then completely exit and restart DBI.
en English; zhtw Traditional Chinese; zhcn Simplified Chinese;
jp Japanese; fr French; es Spanish. The combined package defaults to English.

The built-in official updater may replace the patched NRO. Reapply this
package's NRO and BIN after an official update. Sources/notices: licenses/.
