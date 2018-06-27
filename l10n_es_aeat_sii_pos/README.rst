.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================================================
Suministro Inmediato de Información en el IVA - Terminal Punto de Venta
=======================================================================

Módulo para la presentación inmediata del IVA, extensión para TPV.
http://www.agenciatributaria.es/AEAT.internet/SII.html

**PREPARADO PARA SII 1.1**

Installation
============

Para instalar esté módulo necesita:

#. Libreria Python Zeep, se puede instalar con el comando 'pip install zeep'
#. Libreria Python Requests, se puede instalar con el comando 'pip install requests'
#. Libreria pyOpenSSL, versión 0.15 o posterior

Módulos necesario:
* l10n_es_aeat_sii: https://www.odoo.com/apps/modules/11.0/l10n_es_aeat_sii/
* l10n_es_pos: https://github.com/acysos/odoo-addons/tree/11.0


Usage
=====

Cuando se procesa la venta por TPV se envia al SII. Si el tiqué en negativo se envia con clave rectificativa.


Known issues / Roadmap
======================

* 

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
