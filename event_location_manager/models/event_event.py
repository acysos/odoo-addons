# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DFORMAT


class EventTrackLocation(models.Model):
    _inherit = 'event.track.location'

    def _get_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(string='Company', comodel_name='res.company',
                                 default=_get_company)
    capacity = fields.Integer(string='Capacity', required=True)
    reservation_days = fields.One2many(
        string='Reservation days',
        comodel_name='event.track.location.reservation',
        inverse_name='et_location_id')


class EventTrackLocationReservation(models.Model):
    _name = 'event.track.location.reservation'

    @api.depends('day', 'duration')
    @api.multi
    def _get_end_date(self):
        for res in self.filtered('day'):
            date = datetime.strptime(res.day, DFORMAT)
            res.end_date = date + timedelta(hours=res.duration)
    et_location_id = fields.Many2one(string='Location',
                                     comodel_name='event.track.location',
                                     required=True)
    day = fields.Datetime(string='start date', requiered=True)
    duration = fields.Float(string='duration')
    end_date = fields.Datetime(string='End date', compute='_get_end_date',
                               store=True)
    track_id = fields.Many2one(string='Session', comodel_name='event.track')

    def check_availability(self, location, day, ide, duration):
        date = datetime.strptime(day, DFORMAT)
        date_end = date + timedelta(hours=duration)
        reservations = self.env[
            'event.track.location.reservation'].search([
                ('et_location_id', '=', location.id),
                ('id', '!=', ide), ('day', '<', date_end.strftime(DFORMAT)),
                ('end_date', '>=', date_end.strftime(DFORMAT))])
        if len(reservations) == 0:
            reservations = self.env[
                'event.track.location.reservation'].search([
                    ('et_location_id', '=', location.id),
                    ('id', '!=', ide), ('day', '<=', day),
                    ('day', '<=', day), ('end_date', '>', day)])
            if len(reservations) == 0:
                reservations = self.env[
                    'event.track.location.reservation'].search([
                        ('et_location_id', '=', location.id),
                        ('id', '!=', ide), ('day', '<=', day),
                        ('day', '>', day),
                        ('end_date', '<', date_end.strftime(DFORMAT))])
        if len(reservations) > 0:
            raise UserError(_(
                'this place is reserved for this date, place: ' +
                ' %s date: %s') % (location.name, day))

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(EventTrackLocationReservation, self).create(vals)
        if res.et_location_id:
            self.check_availability(
                res.et_location_id, res.day, res.id,
                res.duration)
        return res

    @api.multi
    def write(self, vals):
        result = super(EventTrackLocationReservation, self).write(vals)
        for res in self:
            if res.et_location_id:
                self.check_availability(res.et_location_id, res.day, res.id,
                                        res.duration)
        return result


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.multi
    def do_reservation(self, location, day, duration, track):
        self.env['event.track.location.reservation'].create({
            'et_location_id': location.id,
            'day': day,
            'duration': duration,
            'track_id': track})

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(EventTrack, self).create(vals)
        if res.location_id:
            self.do_reservation(
                res.location_id, res.date, res.duration, res.id)
        return res

    @api.multi
    def write(self, vals):
        for res in self:
            location = False
            reservation = False
            if res.location_id:
                location = res.location_id
                reservation = self.env[
                    'event.track.location.reservation'].search([
                        ('et_location_id', '=', location.id),
                        ('day', '=', res.date)])
            result = super(EventTrack, res).write(vals)
            if (res.location_id and not location) or (
                    location != res.location_id):
                self.do_reservation(res.location_id, res.date, res.duration,
                                    res.id)
                if reservation:
                    reservation.unlink()
        return result
