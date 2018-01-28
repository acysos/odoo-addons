.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Web Hidden Fields
=================

This module allow hide fields to all users or groups, or to a specific user or
group, without change the views.

Installation
============

Copy this module to your addons path and go to Applications and Install.

Configuration
=============

Don't need any special configuration.

Usage
=====

Go to Configuration -> Hidden Fields -> Hidden Fields.
Create a new template and select the model and the fields that you want to 
hide. 
If you don't select any user or group, the field is hidden for all users. If
you select any user the field is hidden for these users. If you select any 
group the field is hidden for these groups. The user is more restrictive that 
the group.
If the field isn't required, it is removed from view. If it's required the
field is invisible.


Known issues / Roadmap
======================

*

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
