.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
AEAT Base CRLF
==============

Este módulo añade la posibilidad de terminar las líneas en los modelos AEAT
con salto de línea. Necesario para alguna haciendas forales.
Probado en la Comunidad Foral de Navarra y Gipuzkoa.

Installation
============

Módulos necesarios:
* l10n_es_aeat: https://www.odoo.com/apps/modules/11.0/l10n_es_aeat/



Configuration
=============

En Facturación -> Configuración -> AEAT -> Configuración de Exportación a BOE

Editar el modelo deseado y activar en la línea deseada del registro, la opción “Line CRLF”.

P.ej. en el modelo 349, el registro es de 500 caracteres.

Para añadir el CRLF en el sitio correcto, editar la línea “Sello electrónico (en blanco)” que inicia en la posición 488 y termina en la 500. Activar el campo “Line CRLF”. Guardar y exportar el fichero BOE.


Usage
=====

No tiene uso especial, solo exportar el modelo.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/acysos/odoo-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Ignacio Ibeas - Acysos S.L. <ignacio@acysos.com>


Maintainer
----------

.. image:: https://acysos.com/logo.png
   :alt: Acysos S.L.
   :target: https://www.acysos.com
