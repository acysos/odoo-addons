# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class Veterinarian(models.Model):
    _name = 'farm.veterinarian'
    _rec_name = 'user'

    user = fields.Many2one(comodel_name='res.users', string='user')
    collegiate_number = fields.Char(string='Collegiate Number')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    prescription_required = fields.Boolean(string='Prescription requiered',
                                           default=False)


class Product(models.Model):
    _inherit = 'product.product'

    prescription_template = fields.Many2one(
        comodel_name='farm.prescription.template',
        string='Prescription Template')


class PrescriptionMixin(models.Model):
    _name = 'farm.prescription.mixin'
    _auto = False

    specie = fields.Many2one(comodel_name='farm.specie', string='Specie')
    product = fields.Many2one(comodel_name='product.product', string='Product',
                              domain=[('prescription_required', '=', True)],
                              required=True,
                              help='The product for which this recipe is made.'
                              'This can be a drug or a feed to which are added'
                              'the additives or medications defined in the'
                              'lines of this recipe.')
    unit = fields.Many2one(comodel_name='product.uom', string='unit',
                           digits=(16, 2))
    quantity = fields.Float(string='Quantity', digits=(16, 2), required=True)
    afection = fields.Char(string='Afection')
    dosage = fields.Char(string='Dosage')
    waiting_period = fields.Integer(string='Waiting Period',
                                    help='The number of days that must pass'
                                    'since the produced feed is given to'
                                    'animals and they are slaughtered.')
    expiry_period = fields.Integer(string='Expiry Period')
    n_lines = fields.Integer(string='Num of Lines', compute='get_nlines')
    note = fields.Text(string='Note')
    medicated_feed_lot = fields.Many2one(comodel_name='stock.production.lot')

    @api.one
    @api.onchange('waiting_period')
    def on_change_waiting_period(self):
        if self.lines and len(self.lines) > 1:
            self.waiting_period = 28

    @api.one
    def get_nlines(self):
        self.n_lines = len(self.lines)


class PrescriptionLineMixin(models.Model):
    _name = 'farm.prescription.line_mixin'
    _auto = False

    product = fields.Many2one(comodel_name='product.product', string='Product',
                              domain=[('prescription_required', '=', True)],
                              required=True)
    unit = fields.Many2one(comodel_name='product.uom', string='Unit',
                           required=True)
    quantity = fields.Float(string='Quantity', digits=(16, 2), required=True)


class Template(models.Model):
    _name = 'farm.prescription.template'
    _inherit = {'farm.prescription.mixin': 'PrescriptionMixin_id'}
    _rec_name = 'product'
    _auto = True

    lines = fields.One2many(comodel_name='farm.prescription.template.line',
                            inverse_name='prescription', string='Lines')


class TemplateLine(models.Model):
    _name = 'farm.prescription.template.line'
    _inherit = {'farm.prescription.line_mixin': 'PrescriptionLineMixin_id'}
    _auto = True

    prescription = fields.Many2one(comodel_name='farm.prescription.template',
                                   string='Prescription', required=True,
                                   ondelete='CASCADE')


class Prescription(models.Model):
    _name = 'farm.prescription'
    _inherit = {'farm.prescription.mixin': 'PrescriptionMixin_id'}
    _rec_name = 'reference'
    _auto = True

    template = fields.Many2one(comodel_name='farm.prescription.template',
                               string='Template')
    reference = fields.Char(string='Reference', select=True,
                            help='If there is a real prescription; put its'
                            'reference here. Otherwise, leave it blank and'
                            'it will be computed automatically with '
                            'the configured sequence.')
    date = fields.Date(string='Date', required=True,
                       default=fields.Date.today())
    farm = fields.Many2one(comodel_name='stock.location', string='farm',
                           required=True,
                           domain=[('usage', '=', 'view'), ])
    delivery_date = fields.Date(string='Delivery Date', required=True,
                                default=fields.Date.today())
    veterinarian = fields.Many2one(comodel_name='farm.veterinarian',
                                   string='Veterinarian')
    lot = fields.Many2one(comodel_name='stock.production.lot', string='Lot')
    animals = fields.One2many(comodel_name='farm.prescription.animal',
                              inverse_name='prescription', column1='animal',
                              string='Animals')
    animal_group = fields.One2many(
            comodel_name='farm.prescription.animal_group',
            inverse_name='prescription', colum1='party',
            string='Animal Groups')
    lines = fields.One2many(comodel_name='farm.prescription.line',
                            inverse_name='prescription', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ], string='State', readonly=True, default='draft', select=True)
    origin = fields.Many2one(comodel_name='farm.medication.event',
                             string='origin')
    num_of_animals = fields.Integer(compute='get_num_animals',
                                    string='Num. of medicated animals')

    @api.multi
    def get_num_animals(self):
        for res in self:
            result = len(res.animals)
            for party in res.animal_group:
                result = result + party.party.quantity
            res.num_of_animals = result

    @api.one
    @api.onchange('template')
    def on_change_template(self):
        self.waiting_period = self.template.waiting_period
        self.dosage = self.template.dosage
        self.expiry_period = self.template.expiry_period
        self.specie = self.template.specie
        self.quantity = self.template.quantity
        self.unit = self.template.unit
        self.product = self.template.product
        self.afection = self.template.afection
        self.note = self.template.note

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(Prescription, self).create(vals)
        res.reference = self.env['ir.sequence'].get('farm.prescription')
        if len(res.lines) == 0 and res.template:
            pre_lines_obj = self.env['farm.prescription.line']
            for line in res.template.lines:
                pre_lines_obj.create({
                        'prescription': res.id,
                        'quantity': line.quantity,
                        'product': line.product.id,
                        'unit': line.unit.id})
        return res

    @api.one
    def get_animal_lots(self):
        lots = []
        for animal in self.animals:
            lots.append(animal.animal.lot.lot.id)
        for group in self.animal_group:
            for lot in group.party.lot:
                lots.append(lot.lot.id)
        return lots

    def get_origin(self):
        model_obj = self.env['ir.model']
        models = []
        models = model_obj.search([
                ('model', 'in', models),
                ])
        return [('', '')] + [(m.model, m.name) for m in models]

    @api.one
    def confirm(self):
        for pres in self:
            if not pres.veterinarian:
                raise Warning(
                    _('asing veterinarian is necesary'))
            if not pres.lines:
                raise Warning(
                    _('no lines in prescription'))
            if not pres.lot:
                raise Warning(
                    _('no lot selected'))
            pres.state = 'validated'


class PrescriptionAnimal(models.Model):
    _name = 'farm.prescription.animal'

    prescription = fields.Many2one(comodel_name='farm.prescription',
                                   string='Prescription', select=True,
                                   required=True, ondelete='CASCADE')
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             select=True, required=True, ondelete='CASCADE')

    @api.onchange('animal')
    def onchange_party(self):
        return {'domain': {
                    'animal': [('farm', '=', self.prescription.farm.id)]}}


class PrescriptionAnimalGroup(models.Model):
    _name = 'farm.prescription.animal_group'

    prescription = fields.Many2one(comodel_name='farm.prescription',
                                   string='Prescription', select=True,
                                   required=True, ondelete='CASCADE')
    party = fields.Many2one(comodel_name='farm.animal.group',
                            string='Animal Group', select=True,
                            required=True, ondelete='CASCADE')

    @api.onchange('party')
    def onchange_party(self):
        return {'domain': {
                    'party': [('farm', '=', self.prescription.farm.id)]}}


class PrescriptionLine(models.Model):
    _name = 'farm.prescription.line'
    _inherit = {'farm.prescription.line_mixin': 'PrescriptionLineMixin_id'}
    _auto = True

    prescription = fields.Many2one(comodel_name='farm.prescription',
                                   string='Prescription', required=True,
                                   ondelete='CASCADE')


class MedicationEvent(models.Model):
    _inherit = 'farm.medication.event'

    prescription = fields.Many2one(
                            comodel_name='farm.prescription',
                            string='Prescription', select=True,
                            domain=[('state', '=', 'validated')])

    @api.one
    def confirm(self):
        if self.feed_product.product_tmpl_id.prescription_required:
            if len(self.prescription) == 0:
                raise Warning(
                    _('this medication required prescription'))
            else:
                self.confirm_prescription()
        super(MedicationEvent, self).confirm()

    @api.one
    def confirm_prescription(self):
        if self.farm != self.prescription.farm:
            raise Warning(
                    _('this prescription it is not for this farm'))
        if self.animal:
            controlA = False
            for lot in self.prescription.get_animal_lots()[0]:
                print lot
                if self.animal.lot.lot.id == lot:
                    controlA = True
            if not controlA:
                raise Warning(
                    _('this prescription not contains medicated animal'))
            if self.animal_group:
                for lot in self.animal_group.lot:
                    if lot.lot.id not in self.prescription.get_animal_lots():
                        raise Warning(
                            _('this prescription not contains '
                              'medicated group'))
        if not self.prescription.origin:
            self.prescription.origin = self
