# -*- coding: utf-8 -*-
# © 2018 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM aeat_sii_map WHERE name='SII'
        """)