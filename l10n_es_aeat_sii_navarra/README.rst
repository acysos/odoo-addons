.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================================
Suministro Inmediato de Información en el IVA - Navarra
=======================================================

Módulo para la presentación inmediata del IVA, extensión para la Comunidad Foral
de Navarra.
https://www.navarra.es/home_es/Gobierno+de+Navarra/Organigrama/Los+departamentos/Economia+y+Hacienda/Organigrama/Estructura+Organica/Hacienda/Suministro+Inmediato+de+Informacion+del+IVA.htm

AVISO: Solo entorno de pruebas

Installation
============

Para instalar esté módulo necesita:

#. Libreria Python Zeep, se puede instalar con el comando 'pip install zeep'
#. Libreria Python Requests, se puede instalar con el comando 'pip install requests'
#. Libreria Python Requests con directivas de seguridad, se puede instalar con
el siguiente comando 'pip install -U requests[security]'
#. Libreria pyOpenSSL, versión 0.15 o posterior

Módulos necesario:
* l10n_es_aeat_sii: https://www.odoo.com/apps/modules/11.0/l10n_es_aeat_sii/


Usage
=====

Se utiliza igual que el módulo general de SII, pero presenta en la Hacienda
Foral de Navarra.


Known issues / Roadmap
======================

* Hacienda Foral de Navarra no ha publicado el entorno de producción

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
