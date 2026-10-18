DBI 912 — Traduction non officielle v7.4 — Français par défaut

Corrige le véritable affichage MTP sur plusieurs lignes : [stockage]\nСоздание объекта: chemin. Le suivi de l’appel natif a reproduit l’échec v7.3 observé sur Switch ; v7.4 réussit les contrôles locaux natifs, multilignes et de capture d’écran. v7.4 n’a pas été testé sur Switch. La validation matérielle anglaise de v7.2 est historique ; cela ne prouve pas que tous les messages russes sont traduits.
Le NRO v7.4 diffère de v7.3. Pour installer ou mettre à jour, remplacez DBI.nro et translation.bin dans /switch/DBI/ ; dbi.config peut être conservé.


Installation : quittez complètement DBI. Copiez le dossier switch à la racine
de la carte SD. Remplacez DBI.nro ET translation.bin dans /switch/DBI/,
puis relancez DBI. Vous pouvez conserver votre propre dbi.config.

Inclut les corrections des onglets des sauvegardes et du journal d'activité,
des en-têtes statistiques, des messages d'installation et de nettoyage,
des confirmations de mise à jour et des unités MiB/s. Les corrections
d'espacement en chinois sont conservées. Les six langues utilisent le même NRO.
L'utilisateur a confirmé le fonctionnement de la version anglaise v7.2 sur Switch.
Les six tables ont passé les vérifications locales. Certains messages russes
peuvent encore apparaître dans des situations non couvertes.

Le pack multilingue est en anglais par défaut. Copiez le BIN souhaité depuis
translations vers /switch/DBI/translation.bin, puis quittez et relancez DBI.
en anglais ; zhtw chinois traditionnel ; zhcn chinois simplifié ; jp japonais ;
fr français ; es espagnol.

La mise à jour officielle intégrée peut remplacer le NRO modifié. Réinstallez
le NRO et le BIN de ce pack après une mise à jour officielle. Sources : licenses/.
