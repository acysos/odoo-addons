# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime, timedelta
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
    _inherit = {'mail.thread': 'mail_thread_id'}

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
    margin = fields.Integer(string='interlot margin', default=2000)

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
        self.set_sinc_day()
        self.connection.disconnect(conn)

    @api.multi
    def button_sinc_bom(self):
        conn = self.connection.connect()
        self.sincronize_products(conn)
        self.sincronize_bom(conn)
        self.connection.disconnect(conn)

    @api.multi
    def synchronize_cron(self):
        logger.info('Feed Machine Sinc')
        conectors = self.search([('state', '=', 'sinc')])
        for con in conectors:
            con.sincronize_data()

    @api.multi
    def set_sinc_day(self):
        for res in self:
            new_day = datetime.today() - timedelta(days=10)
            res.sincronization_start_day = new_day
    
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

    def find_product(self, conn, ifr_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + self.view_product +
                       " WHERE Codigo=%s" , ifr_id)
        products_tmpl_obj = self.env['product.template']
        proCateg_obj = self.env['product.category']
        for row in cursor:
            product = products_tmpl_obj.search(
                [('feed_machine_product_id', '=', row[0]),
                 ('active', '=', False)])
            if len(product) == 0:
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
                products_tmpl_obj.create({
                    'name': row[3],
                    'type': 'consu',
                    'categ_id': categ.id,
                    'uom_id': uom.id,
                    'uom_po_id': uom.id,
                    'feed_machine_product_id': row[0],
                    'prescription_required': pres,
                    'type': 'product'})
            else:
                product.active = True
                child_p = self.env['product_product'].search([
                    ('product_tmpl_id', '=', product.id)])
                for p in child_p:
                    p.active = True

    def sincronize_products(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + self.view_product +
                       " WHERE Tipo!=%s", 'Contacto')
        products_obj = self.env['product.template']
        proCateg_obj = self.env['product.category']
        for row in cursor:
            product = products_obj.search(
                [('feed_machine_product_id', '=', row[0]), '|',
                 ('active', '=', True), ('active', '=', False)])
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

        self.env.cr.commit()

    @api.multi
    def sincronize_product_inputs(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT top 100 * FROM " + self.view_product_input + 
                       " order by Ticket DESC")
        row = cursor.fetchone()
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        transfer_obj = self.env['stock.transfer_details']
        trasfer_line_obj = self.env['stock.transfer_details_items']
        lot_obj = self.env['stock.production.lot']
        for res in self:
            cont = 0
            while row:
                cont = cont +1
                sincDate = datetime.strptime(
                    res.sincronization_start_day, DFORMAT)
                rowDate = datetime.strptime(row[5], DMSSQLFORMAT)
                if sincDate < rowDate and str(row[10]) != 'OP':
                    old_move = pick_obj.search([
                        ('feed_machine_product_input_id', '=', int(row[0]))])
                    if len(old_move) == 0:
                        product_tmpl = product_tmpl_obj.search([
                            ('feed_machine_product_id', '=', row[3])
                            ])
                        if len(product_tmpl) == 0:
                            self.find_product(conn, row[3])
                            product_tmpl = product_tmpl_obj.search([
                                ('feed_machine_product_id', '=', row[3])
                                ])
                            if len(product_tmpl) == 0:
                                self.button_sinc_bom()
                        product = product_obj.search([
                            ('product_tmpl_id', '=', product_tmpl.id)])
                        lot = lot_obj.search([
                            ('feed_machine_lot', '=', row[13])])
                        if len(lot) == 0:
                            lot = lot_obj.create({
                                'product_id': product.id,
                                'feed_machine_lot': row[13],
                                'ref': row[16]})
                        prob = self.env['res.partner'].search([
                            ('feed_machine_ref', '=', row[10])])
                        move = move_obj.search([
                            ('state', '=', 'assigned'),
                            ('product_id', '=', product.id),
                            ('picking_id.partner_id', '=', prob.id)
                            ], order='date ASC')
                        if len(move) != 0:
                            mov = move[0]
                            if row[6] > (mov.product_qty + res.margin) and \
                                    len(move) > 1:
                                qty2 = row[6] - mov.product_qty
                                mov2 = move[1]
                                self.move_transfer(
                                    mov, product, product_tmpl,
                                    mov.product_qty, lot, row[0], row[16])
                                self.move_transfer(
                                    mov2, product, product_tmpl,
                                    qty2, lot, row[0], row[16])
                            else:
                                self.move_transfer(
                                    mov, product, product_tmpl,
                                    row[6], lot, row[0], row[16])
                        else:
                            provider = self.env['res.partner'].search([
                                ('feed_machine_ref', '=', str(row[10]))])
                            if len(provider) == 0:
                                self.send_msg_prov(
                                    str(row[10]), str(row[0]), str(row[10]),
                                    str(row[11].encode('UTF-8')))
                            else:
                                text = str(row[10]) + '-' + \
                                    str(row[11].encode('UTF-8'))
                                self.send_msg(str(row[0]), str(row[0]),
                                              text, product.name)
                row = cursor.fetchone()

    @api.multi
    def move_transfer(self, mov, product, tmpl, qty, lot, row0, row16):
        transfer_obj = self.env['stock.transfer_details']
        trasfer_line_obj = self.env['stock.transfer_details_items']
        transfer = transfer_obj.create({
            'picking_id': mov.picking_id.id,
            })
        trasfer_line_obj.create({
            'transfer_id': transfer.id,
            'product_id': product.id,
            'product_uom_id':
                tmpl.uom_id.id,
            'quantity': qty,
            'lot_id': lot.id,
            'sourceloc_id': mov.location_id.id,
            'destinationloc_id':
                mov.location_dest_id.id,
            })
        transfer.do_detailed_transfer()
        self.assing_fm_id(mov, int(row0), qty,
                          row16)
        mov.partner_id = mov.picking_id.partner_id
    
    def assing_fm_id(self, move, ref, weigth, lot):
        move.picking_id.feed_machine_product_input_id = ref
        move.picking_id.weigth = weigth
        move.picking_id.prov_lot = lot

    def send_msg(self, subject, ref, prov, prod):
        body = "Referencia: " + ref + ' Proveedor: ' + \
            prov, 'Producto: ' + prod
        old_msg = self.env['mail.message'].search([('subject', '=', subject)])
        if len(old_msg) == 0:
            group = self.env['res.groups'].search([
                ('category_id.name', '=', 'Farm')])
            recipient_partners = []
            for gr in group:
                for recipient in gr.users:
                    recipient_partners.append(
                        (4, recipient.partner_id.id))
            post_vars = {'subject': subject,
                         'partner_ids': recipient_partners}
            self.message_post(body=body,
                              type='comment',
                              **post_vars)

    def send_msg_prov(self, subject, ref, cod, prob):
        body = "Referencia: " + ref + ' codigo_Proveedor: ' + \
            cod, 'Nombre: ' + prob
        old_msg = self.env['mail.message'].search([
            ('subject', '=', (subject + 'p'))])
        if len(old_msg) == 0:
            group = self.env['res.groups'].search([
                ('category_id.name', '=', 'Farm')])
            recipient_partners = []
            for gr in group:
                for recipient in gr.users:
                    recipient_partners.append(
                        (4, recipient.partner_id.id))
            post_vars = {'subject': (subject + 'p'),
                         'partner_ids': recipient_partners}
            self.message_post(body=body,
                              type='comment',
                              **post_vars)

    @api.multi
    def sincronize_bom(self, conn):
        cursor = self.connection.selectView(
            self.connection.getNewCursor(conn), self.view_bom)
        bom_obj = self.env['mrp.bom']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        bom_line_obj = self.env['mrp.bom.line']
        new_boms = {}
        uom = self.env['product.uom'].search([
                    ('name', '=', 'kg')])
        row = cursor.fetchone()
        while row:
            product_tmpl = product_tmpl_obj.search([
                ('feed_machine_product_id', '=', row[0]),
                '|', ('active', '!=', True), ('active', '=', True)])
            if len(product_tmpl) > 1:
                d_product_tmpl = product_tmpl_obj.search([
                ('feed_machine_product_id', '=', row[0]),
                ('active', '!=', True)])
                if d_product_tmpl:
                    d_product_tmpl[0].unlink()
                product_tmpl = product_tmpl_obj.search([
                ('feed_machine_product_id', '=', row[0]),
                '|', ('active', '!=', True), ('active', '=', True)])
                if len(product_tmpl) > 1:
                    product_tmpl[-1].unlink()
                product_tmpl = product_tmpl_obj.search([
                ('feed_machine_product_id', '=', row[0]),
                '|', ('active', '!=', True), ('active', '=', True)])
            bom = bom_obj.search([
                ('product_tmpl_id', '=', product_tmpl.id),
                '|', ('active', '!=', True), ('active', '=', True)])
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
                                  'product_uom': uom.id,
                                  'product_efficiency': 1,
                                  })
            qty = 0.0
            for line in lines:
                raw_tmpl = product_tmpl_obj.search([
                    ('feed_machine_product_id', '=', line[1])])[0]
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
                       " WHERE Estado = 'Fin' and Fecha > " +
                       "Convert(datetime, %s, 121)", start_day)
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
                    self.find_product(conn, row[1])
                    product_tmpl = product_tmpl_obj.search([
                        ('feed_machine_product_id', '=', row[1])])
                if len(product_tmpl) == 0:
                    self.send_msg("Unactivate product", str(row[1]),
                                  '?', '?')
                else:
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
                            str(row[9]), adinser_lot, row[11]
                            ])
                    else:
                        productions[row[0]] = []
                        productions[row[0]].append([
                            product_tmpl, product,
                            bom, raw_mat_tmpl, raw_mat,
                            float(row[8]), production_lot,
                            str(row[9]), adinser_lot, row[11]
                            ])
            row = cursor.fetchone()
        lots_rel_obj = self.env['feed.machine.dosif.lot.relations']
        dosif_rel_obj = self.env['feed.machine.dosification']
        for l, lines in productions.iteritems():
            adinser_lot = lines[0][8]
            product_tmpl = lines[0][0]
            product = lines[0][1]
            bom = lines[0][2]
            total = lines[0][9]
            lots_rel = lots_rel_obj.search([
                    ('feed_machine_lot', '=', adinser_lot)])
            if len(lots_rel) == 0:
                new_lot = self.env['stock.production.lot'].create({
                    'product_id': product.id,
                    'feed_machine_lot': adinser_lot,
                    'life_date': datetime.today() + timedelta(days=90)})
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
                'product_qty': total,
                'machine_production_lot': l,
                })
            new_production.action_confirm()
            new_production.action_ready()
            lots_obj = self.env['stock.production.lot']
            new_wiz_production = wiz_product_produce_obj.create({
                'product_id': product.id,
                'product_qty': total,
                'mode': 'consume_produce',
                'lot_id': new_lot.id,
                })
            for line in lines:
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
            new_production.action_produce(
                total, 'consume_produce', new_wiz_production)
            new_production.action_production_end()
            self.env.cr.commit()


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
