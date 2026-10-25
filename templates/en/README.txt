DBI 912 unofficial translation v7.6 — English

Fixes a translation-induced save backup restore failure and translates the text editor unsaved-changes confirmation. Internal INI data stays unchanged; UI labels remain translated. Replace BOTH DBI.nro and translation.bin, then restart DBI. Local native tests passed; actual restoration and dialog behavior await Switch confirmation.

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
