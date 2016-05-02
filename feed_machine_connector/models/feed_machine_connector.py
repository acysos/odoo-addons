# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime
import logging

DFORMAT = "%Y-%m-%d"
DMSSQLFORMAT = "%d/%m/%Y %H:%M:%S"
SINC_STATES = [
    ('desSinc', 'No Sincronized'),
    ('sinc', 'Sincronized'),
    ]
logger = logging.getLogger(__name__)


class FeedMachineConnector(models.Model):
    _name = 'farm.feed.machine.connector'

    connection = fields.Many2one(comodel_name='connector.sqlserver',
                                 string='Connection Name')
    view_product = fields.Char(string='Products View Name')
    view_bom = fields.Char(string='Boms View Name')
    view_production = fields.Char(string='Productions View Name')
    view_product_input = fields.Char(string='Product Input View Name')
    feed_machine_source = fields.Many2one(
        comodel_name='stock.location', string='Feed machine inputs location',
        domain=[('silo', '=', True)])
    feed_lost_found_location = fields.Many2one(
        comodel_name='stock.location', string='Feed machine output location',
        domain=[('usage', '=', 'transit')])
    sincronization_start_day = fields.Date(string='Sinc. Start day',
                                           help='Only load moves after '
                                           'this day')
    state = fields.Selection(string='State', selection=SINC_STATES,
                             default='desSinc')

    @api.multi
    def initial_sincronize(self):
        conn = self.connection.connect()
        self.sincronize_products(conn)
        self.sincronize_bom(conn)
        self.sincronize_product_inputs(conn)
        self.sincronize_production(conn)
        for sinc in self:
            sinc.state = 'sinc'
        self.connection.disconnect(conn)

    @api.multi
    def sincronize_data(self):
        conn = self.connection.connect()
        self.sincronize_product_inputs(conn)
        self.sincronize_production(conn)
        self.connection.disconnect(conn)

    @api.multi
    def synchronize_cron(self):
        logger.info('Feed Machine Sinc')
        conectors = self.search([('state', '=', 'sinc')])
        for con in conectors:
            con.sincronize_data()

    def send_notifycation(self, subject, message):
        groups = self.env['res.groups'].search([
            ('category_id.name', '=', 'Farm')])
        recipient_partners = []
        for group in groups:
            for recipient in group.users:
                recipient_partners.append(
                    (4, recipient.partner_id.id))
        post_vars = {'subject': subject,
                     'body': message,
                     'partner_ids': recipient_partners, }
        thread_obj = self.env['mail.thread']
        thread_obj.message_post(False, type='notyfication',
                                subtype='mt_comment', **post_vars)

    def sincronize_products(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + self.view_product +
                       " WHERE Tipo!=%s", 'Contacto')
        products_obj = self.env['product.template']
        proCateg_obj = self.env['product.category']
        for row in cursor:
            product = products_obj.search(
                [('feed_machine_product_id', '=', row[0])])
            if len(product) == 0 and row[4] != 'si':
                categ = proCateg_obj.search([
                        ('name', '=', row[2])])
                uom = self.env['product.uom'].search([
                    ('name', '=', 'kg')])
                if len(categ) == 0:
                    categ = proCateg_obj.create({'name': row[2]})
                if categ.name == 'Medicina' or categ.name == 'Medicac. ':
                    pres = True
                else:
                    pres = False
                products_obj.create({
                    'name': row[3],
                    'type': 'consu',
                    'categ_id': categ.id,
                    'uom_id': uom.id,
                    'uom_po_id': uom.id,
                    'feed_machine_product_id': row[0],
                    'prescription_required': pres,
                    'type': 'product'})

    @api.multi
    def sincronize_product_inputs(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + self.view_product_input)
        row = cursor.fetchone()
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        transfer_obj = self.env['stock.transfer_details']
        trasfer_line_obj = self.env['stock.transfer_details_items']
        lot_obj = self.env['stock.production.lot']
        for res in self:
            while row:
                sincDate = datetime.strptime(
                    res.sincronization_start_day, DFORMAT)
                rowDate = datetime.strptime(row[5], DMSSQLFORMAT)
                if sincDate < rowDate:
                    old_move = pick_obj.search([
                        ('feed_machine_product_input_id', '=', int(row[0]))])
                    if len(old_move) == 0:
                        product_tmpl = product_tmpl_obj.search([
                            ('feed_machine_product_id', '=', row[3])
                            ])
                        if len(product_tmpl) == 0:
                            self.sincronize_products(conn)
                            product_tmpl = product_tmpl_obj.search([
                                ('feed_machine_product_id', '=', row[3])
                                ])
                        product = product_obj.search([
                            ('product_tmpl_id', '=', product_tmpl.id)])
                        lot = lot_obj.search([
                            ('feed_machine_lot', '=', row[13])])
                        if len(lot) == 0:
                            lot = lot_obj.create({
                                'product_id': product.id,
                                'feed_machine_lot': row[13]})
                        move = move_obj.search([
                            ('state', '=', 'assigned'),
                            ('product_id', '=', product.id),
                            ])
                        if len(move) != 0:
                            transfer = transfer_obj.create({
                                'picking_id': move.picking_id.id,
                                })
                            trasfer_line_obj.create({
                                'transfer_id': transfer.id,
                                'product_id': product.id,
                                'product_uom_id': product_tmpl.uom_id.id,
                                'quantity': row[6],
                                'lot_id': lot.id,
                                'sourceloc_id': move.location_id.id,
                                'destinationloc_id': move.location_dest_id.id,
                                })
                            transfer.do_detailed_transfer()
                            move.picking_id.feed_machine_product_input_id = \
                                int(row[0])
                        else:
                            print 'no encontrado'
                            print row[0]
                row = cursor.fetchone()

    @api.multi
    def sincronize_bom(self, conn):
        cursor = self.connection.selectView(
            self.connection.getNewCursor(conn), self.view_bom)
        bom_obj = self.env['mrp.bom']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        bom_line_obj = self.env['mrp.bom.line']
        new_boms = {}
        row = cursor.fetchone()
        while row:
            product_tmpl = product_tmpl_obj.search([
                ('feed_machine_product_id', '=', row[0])])
            bom = bom_obj.search([
                ('product_tmpl_id', '=', product_tmpl.id)])
            if len(bom) == 0:
                bom_line = []
                for r in range(1, 6):
                    result = row[r].encode('ascii', 'ignore')
                    bom_line.append(result)
                bom_line.append(product_tmpl.uom_id.id)
                if product_tmpl.id in new_boms:
                    new_boms[product_tmpl.id].append(bom_line)
                else:
                    new_boms[product_tmpl.id] = []
                    new_boms[product_tmpl.id].append(bom_line)
            row = cursor.fetchone()
        for p, lines in new_boms.iteritems():
            prod = product_obj.search([('product_tmpl_id', '=', p)])
            bom = bom_obj.create({'name': lines[0][0],
                                  'type': 'normal',
                                  'product_tmpl_id': p,
                                  'product_id': prod.id,
                                  'product_qty': 1,
                                  'product_uom': lines[0][5],
                                  'product_efficiency': 1,
                                  })
            qty = 0.0
            for line in lines:
                raw_tmpl = product_tmpl_obj.search([
                    ('feed_machine_product_id', '=', line[1])])
                product = product_obj.search([
                    ('product_tmpl_id', '=', raw_tmpl.id)])
                aux = line[4].replace(',', '.')
                bom_line_obj.create({'product_id': product.id,
                                     'product_qty': aux,
                                     'bom_id': bom.id,
                                     'product_uom': raw_tmpl.uom_id.id,
                                     })
                qty += float(aux)
            bom.product_qty = qty

    @api.multi
    def sincronize_production(self, conn):
        cursor = conn.cursor()
        aux = datetime.strptime(self.sincronization_start_day, DFORMAT)
        start_day = str(aux)
        cursor.execute('SELECT * FROM ' + self.view_production +
                       " WHERE Fecha > Convert(datetime, %s, 121)", start_day)
        row = cursor.fetchone()
        bom_obj = self.env['mrp.bom']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        produce_line_obj = self.env['mrp.product.produce.line']
        production_obj = self.env['mrp.production']
        wiz_product_produce_obj = self.env['mrp.product.produce']
        productions = {}
        while row:
            production_lot = row[0]
            production = production_obj.search([
                    ('machine_production_lot', '=', production_lot)])
            if len(production) == 0:
                product_tmpl = product_tmpl_obj.search([
                    ('feed_machine_product_id', '=', row[1])])
                adinser_lot = str(row[3])
                if len(product_tmpl) == 0:
                    self.sincronize_products(conn)
                    product_tmpl = product_tmpl_obj.search([
                        ('feed_machine_product_id', '=', row[1])])
                bom = bom_obj.search([
                    ('product_tmpl_id', '=', product_tmpl.id)])
                if len(bom) == 0:
                    self.sincronize_bom(conn)
                    bom = bom_obj.search([
                        ('product_tmpl_id', '=', product_tmpl.id)])
                product = product_obj.search([
                    ('product_tmpl_id', '=', product_tmpl.id)])
                raw_mat_tmpl = product_tmpl_obj.search([
                    ('feed_machine_product_id', '=', row[5])])
                raw_mat = product_obj.search([
                    ('product_tmpl_id', '=', raw_mat_tmpl.id)])
                if row[0] in productions:
                    productions[row[0]].append([
                        product_tmpl, product,
                        bom, raw_mat_tmpl, raw_mat,
                        float(row[8]), production_lot,
                        str(row[9]), adinser_lot
                        ])
                else:
                    productions[row[0]] = []
                    productions[row[0]].append([
                        product_tmpl, product,
                        bom, raw_mat_tmpl, raw_mat,
                        float(row[8]), production_lot,
                        str(row[9]), adinser_lot
                        ])
            row = cursor.fetchone()
        out_total = 0
        lots_rel_obj = self.env['feed.machine.dosif.lot.relations']
        dosif_rel_obj = self.env['feed.machine.dosification']
        for l, lines in productions.iteritems():
            adinser_lot = lines[0][8]
            product_tmpl = lines[0][0]
            product = lines[0][1]
            bom = lines[0][2]
            lots_rel = lots_rel_obj.search([
                    ('feed_machine_lot', '=', adinser_lot)])
            if len(lots_rel) == 0:
                new_lot = self.env['stock.production.lot'].create({
                    'product_id': product.id,
                    'feed_machine_lot': adinser_lot, })
                new_lots_rel = lots_rel_obj.create({
                    'feed_machine_lot': adinser_lot,
                    'lot': new_lot.id})
                dosif_rel_obj.create({
                    'dosif_rel': new_lots_rel.id,
                    'dosification': l})
            else:
                new_lot = lots_rel.lot
                dosif_rel_obj.create({
                    'dosif_rel': lots_rel.id,
                    'dosification': l})
            new_production = production_obj.create({
                'product_id': product.id,
                'bom_id': bom.id,
                'product_uom': product_tmpl.uom_id.id,
                'location_src_id': self.feed_machine_source.id,
                'location_dest_id': self.feed_lost_found_location.id,
                'product_qty': bom.product_qty,
                'machine_production_lot': l,
                })
            new_production.action_confirm()
            new_production.action_ready()
            lots_obj = self.env['stock.production.lot']
            new_wiz_production = wiz_product_produce_obj.create({
                'product_id': product.id,
                'product_qty': bom.product_qty,
                'mode': 'consume_produce',
                'lot_id': new_lot.id,
                })
            for line in lines:
                out_total = out_total + line[5]
                raw_mat = line[4]
                qty = line[5]
                lot = lots_obj.search([('feed_machine_lot', '=', line[7])])
                if len(lot) > 1:
                    lot = lot[0]
                produce_line_obj.create({
                    'product_id': raw_mat.id,
                    'product_qty': qty,
                    'lot_id': lot.id,
                    'produce_id': new_wiz_production.id,
                    })
            new_wiz_production.product_qty = out_total
            new_production.product_qty = out_total
            new_production.action_produce(
                bom.product_qty,
                'consume_produce', new_wiz_production)
            new_production.action_production_end()


class dosif_lot_relations(models.Model):
    _name = 'feed.machine.dosif.lot.relations'

    feed_machine_lot = fields.Char(string='Feed machine lot')
    dosification = fields.One2many(string='Dosifications',
                                   comodel_name='feed.machine.dosification',
                                   inverse_name='dosif_rel')
    lot = fields.Many2one(string='ODOO Lot',
                          comodel_name='stock.production.lot')


class feed_machine_dosification(models.Model):
    _name = 'feed.machine.dosification'
    
    dosif_rel = fields.Many2one(
        comodel_name='feed.machine.dosif.lot.relations', string='Lot relation')
    dosification = fields.Char(string='Dosification')
            