v7.5 traduce las opciones que faltaban en el menú de exclusiones y parches de SaltyNX. El NRO es idéntico al de v7.4; translation.bin ha cambiado. Desde una versión anterior, sustituya ambos archivos. Pruebas locales superadas; pendiente de confirmar en consola.

﻿DBI 912 — Traducción no oficial v7.4 — Español predeterminado

Corrige el mensaje MTP real de varias líneas: [almacenamiento]\nСоздание объекта: ruta. El seguimiento del llamador nativo reprodujo el fallo de v7.3 observado en Switch; v7.4 supera las comprobaciones locales nativas, multilínea y de capturas. v7.4 no se probó en hardware Switch. La confirmación de hardware de v7.2 en inglés es histórica; esto no demuestra que se hayan traducido todos los mensajes rusos.
El NRO de v7.4 cambió respecto a v7.3. Para instalar o actualizar, reemplaza DBI.nro y translation.bin en /switch/DBI/; puedes conservar dbi.config.


Instalación: cierra DBI por completo. Copia la carpeta switch a la raíz de
la tarjeta SD. Sustituye DBI.nro Y translation.bin en /switch/DBI/ y reinicia DBI.
Puedes conservar tu propio dbi.config.

Incluye las correcciones de las pestañas de partidas guardadas y del registro
de actividad, los encabezados de estadísticas, los mensajes de instalación
y limpieza, las confirmaciones de actualización y las unidades MiB/s.
Se conservan las correcciones de espacios en chino. Los seis idiomas usan
el mismo NRO. El usuario confirmó que la versión inglesa v7.2 funciona en Switch.
Las seis tablas superaron las comprobaciones locales. Aún pueden aparecer
mensajes rusos en situaciones que no se han cubierto.

El paquete multilingüe usa inglés por defecto. Copia el BIN elegido desde
translations a /switch/DBI/translation.bin; cierra DBI por completo y reinícialo.
en inglés; zhtw chino tradicional; zhcn chino simplificado; jp japonés;
fr francés; es español.

La actualización oficial integrada puede sustituir el NRO modificado. Vuelve
a instalar el NRO y el BIN de este paquete después de actualizar. Fuentes: licenses/.
