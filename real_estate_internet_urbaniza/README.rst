.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Real Estate Urbaniza
====================

This module extends Real Estate to create an export XML for the Spanish portal
Urbaniza

Installation
============

Urbaniza doesn't support https. Disallow https for the urls:

* http://<domain>/realestateportal/urbaniza.xml
* http://<domain>/website/image/<model>/<id>/<field>/image.jpg
* http://<domain>/website/image/<model>/<id>/<field>/image.JPG
* http://<domain>/website/image/<model>/<id>/<field>/image.gif
* http://<domain>/website/image/<model>/<id>/<field>/image.GIF
* http://<domain>/website/image/<model>/<id>/<field>/image.png
* http://<domain>/website/image/<model>/<id>/<field>/image.PNG
* http://<domain>/website/pdf/<model>/<field>/<id>/<filename_field>/pdf.pdf
* http://<domain>/website/pdf/<model>/<field>/<id>/<filename_field>/pdf.PDF

Usage
=====

The xml url is http://<domain>/realestateportal/urbaniza.xml

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
* Daniel Pascal - Acysos S.L. <daniel@acysos.com>


Maintainer
----------

.. image:: https://acysos.com/logo.png
   :alt: Acysos S.L.
   :target: https://www.acysos.com
