.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Hacienda Foral de Navarra
=========================

Módulo para la presentación de modelos de Navarra (https://www.navarra.es/es/hacienda):

- F66-F69
- F50-347
- 349
- SII

**COMPATIBLE con Community, Enterprise y Odoo.sh**

Instalación
===========

Para instalar esté módulo necesita (https://github.com/OCA/l10n-spain/tree/17.0):

- l10n_es_aeat
- l10n_es_aeat_sii_oca
- l10n_es_aeat_mod347
- l10n_es_aeat_mod349

Uso
===

Para la configuración de los modelos de Navarra, es necesario tener instalado el módulo y solicitar una clave de acceso
en https://navarradoo.com

Dicha clave debe ser introducida en la configuración de la compañía en la pestaña de "Navarra", en el campo
"Clave IAP Navarra". También en la pestaña de "AEAT" indique que usa Hacienda Foral de Navarra.

Los módelos F66-F69 se habilitan dentro del menu de Declaraciones de AEAT. Los otros módulos usan el funcionamiento
estándar de los módulos indicados. En el caso de los modelos F50-F347 y 349, tienen un nuevo botón que se llama
"Exportar Hacienda Navarra" que genera un fichero en el formato de Hacienda Navarra.


Roadmap
=======

* Modelo 715
* Modelo 759


Bug Tracker
===========

Bugs tienen que ser enviados a soporte@navarradoo.com


Créditos
========

Autores
-------

* Acysos S.L. <soporte@navarradoo.com>


Mantenedor
----------

.. image:: https://acysos.com/logo.png
   :alt: Acysos S.L.
   :target: https://www.acysos.com
