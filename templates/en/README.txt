DBI 912 unofficial translation v7.7 — English

Completes the editor unsaved-changes title and translates the missing Patch meta version installation option. All six languages updated. The NRO is identical to v7.6; replace translation.bin and restart DBI. From older versions replace both files. Backup restoration with v7.6 is user-confirmed. New labels passed local native drawing tests; Switch display confirmation pending.

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
