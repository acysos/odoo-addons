# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# Copyright (C) 2024  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Specie(models.Model):
    _name = 'farm.specie'

    name = fields.Char(string='name', required=True,
                       help='Name of the specie. ie. "Pig"')
    male_product = fields.Many2one(
        comodel_name='product.product', string="Male's Product")

    female_product = fields.Many2one(
        comodel_name='product.product',
        string="Female's Product", )

    individual_product = fields.Many2one(
        comodel_name='product.product',
        string="Individual's Product", )

    group_product = fields.Many2one(
        comodel_name='product.product', string="Group's Product")

    semen_product = fields.Many2one(
        comodel_name='product.product', string="Semen's Product",
        help="Product for the mixture of semen to raise the expected "
        "quality.\nIt is used in the Production lots produced in the "
        "Extraction Events and in the BoM containers for doses used in "
        "deliveries to farms for inseminations.")
    sale_product = fields.Many2one(comodel_name='product.product',
                                   string='Product denomination in sales',
                                   help='use when you sale animal units but'
                                   ' customer pay meat kilogram')
    breeds = fields.One2many(comodel_name='farm.specie.breed',
                             inverse_name='specie', string='Breeds')
    farm_lines = fields.One2many(comodel_name='farm.specie.farm_line',
                                 inverse_name='specie', string='Farms')
    removed_location = fields.Many2one(
        comodel_name='stock.location', string='Removed Location',
        domain=[('usage', '=', 'transit')],
        required=True,
        help='Virtual location where removed animals are moved to.')
    foster_location = fields.One2many(
        comodel_name='farm.foster.locations', inverse_name='specie',
        string='Foster Location',
        help='Virtual location where fostered animals are moved to.')
    lost_found_location = fields.One2many(
        comodel_name='farm.transit.locations', inverse_name='specie',
        string='Transit Location',
        help='Virtual location where lost or found animals are moved to.')
    future_maders_location = fields.One2many(
        comodel_name='farm.future_maders.locations', inverse_name='specie',
        string='Future maders location')
    feed_lost_found_location = fields.Many2one(
        comodel_name='stock.location', inverse_name='specie',
        string='Feed transit',
        domain=[('usage', '=', 'transit')])
    consumed_feed_location = fields.Many2one(
        comodel_name='stock.location', string='consumed feed location',
        required=True)

class Breed(models.Model):
    'Breed of Specie'
    _name = 'farm.specie.breed'

    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True,
                             ondelete='CASCADE')
    name = fields.Char(string='Name', required=True)


class SpecieFarmLine(models.Model):
    'Managed Farm of specie'
    _name = 'farm.specie.farm_line'

    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True,
                             ondelete='CASCADE')
    farm = fields.Many2one(comodel_name='stock.location',
                           string='Farm', required=True,
                           domain=[('usage', '=', 'view')])
    event_order_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Events Orders' Sequence", required=True, domain=[
            ('code', '=', 'farm.event.order')
            ],
        help="Sequence used for the Event Orders in this farm.")
    has_male = fields.Boolean(string='Males',
                              help="In this farm there are males.")
    male_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Males' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for male lots and animals.')
    semen_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Extracted Semen Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    dose_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Semen Dose Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    has_female = fields.Boolean(string='Females',
                                help="In this farm there are females.")
    female_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Females' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for female production lots and animals.')
    has_individual = fields.Boolean(string='Individuals',
                                    help="In this farm there are individuals.")
    individual_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Individuals' Sequence", domain=[('code', '=', 'farm.animal')],
        help="Sequence used for individual lots and animals.")
    has_group = fields.Boolean(string='Groups',
                               help="In this farm there are groups.")
    group_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Groups' Sequence",
        domain=[('code', '=', 'farm.animal.group')],
        help='Sequence used for group production lots and animals.')
    farm_lines = fields.One2many(comodel_name='farm.specie.farm_line',
                                 inverse_name='specie', string='Farms')

class SpecieFarmLine(models.Model):
    'Managed Farm of specie'
    _name = 'farm.specie.farm_line'

    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True,
                             ondelete='CASCADE')
    farm = fields.Many2one(comodel_name='stock.location',
                           string='Farm', required=True,
                           domain=[('usage', '=', 'view')])
    event_order_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Events Orders' Sequence", required=True, domain=[
            ('code', '=', 'farm.event.order')
        ],
        help="Sequence used for the Event Orders in this farm.")
    has_male = fields.Boolean(string='Males',
                              help="In this farm there are males.")
    male_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Males' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for male lots and animals.')
    semen_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Extracted Semen Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    dose_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Semen Dose Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    has_female = fields.Boolean(string='Females',
                                help="In this farm there are females.")
    female_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Females' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for female production lots and animals.')
    has_individual = fields.Boolean(string='Individuals',
                                    help="In this farm there are individuals.")
    individual_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Individuals' Sequence", domain=[('code', '=', 'farm.animal')],
        help="Sequence used for individual lots and animals.")
    has_group = fields.Boolean(string='Groups',
                               help="In this farm there are groups.")
    group_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Groups' Sequence",
        domain=[('code', '=', 'farm.animal.group')],
        help='Sequence used for group production lots and animals.')
