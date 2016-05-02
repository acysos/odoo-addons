# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import Warning
import logging

DFORMAT = "%Y-%m-%d"
DTFORMAT = "%Y-%m-%d %H:%M:%S"
SINC_STATES = [
    ('desSinc', 'No Sincronized'),
    ('sinc', 'Sincronized'),
    ]
logger = logging.getLogger(__name__)


class Connector(models.Model):
    _name = 'farm.ifr.connector'

    connection = fields.Many2one(comodel_name='connector.sqlserver',
                                 string='Connection Name')
    farms_relations = fields.One2many(comodel_name='farm.ifr.farms.relation',
                                      inverse_name='ifr_connector',
                                      string='Farm name relations')
    state = fields.Selection(string='State', selection=SINC_STATES,
                             default='desSinc')
    last_remov_id = fields.Integer(string='IFR last removal ID', default=0)
    last_foster_day = fields.Datetime(string='last foster date')

    @api.multi
    def synchronize_cron(self):
        logger.info('IFR Sinc')
        conectors = self.search([('state', '=', 'sinc')])
        for con in conectors:
            con.sincronize()

    def sincronize(self):
        conn = self.connection.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_GRANJA, ID_ANIMAL FROM dbo.REPRO")
        row = cursor.fetchone()
        animal_obj = self.env['farm.animal']
        animals = []
        while row:
            for farm in self.farms_relations:
                        if farm.ifr_farm_name == row[0]:
                            current_farm = farm
            animal = animal_obj.search([
                ('ifr_sequence', '=', row[1]),
                ('farm', '=', current_farm.farm.id)])
            if len(animal) == 1:
                animals.append([animal, row[0]])
            row = cursor.fetchone()
        for animal in animals:
            self.sincronize_female(conn, animal[0], animal[1])
        self.sincronize_removals(conn)
        self.connection.disconnect(conn)

    @api.multi
    def sincronize_removals(self, conn):
        conn = self.connection.connect()
        cursor = conn.cursor()
        for res in self:
            cursor.execute(
                "SELECT idgranja, idanimal, c.descripcion, "
                "t.descripcion, c.tipobaja, fecha"
                " from dbo.b_bajareproductores b inner join dbo.C_CBAJA c "
                "on b.causa=c.codigo inner join dbo.C_TIPBAJ t "
                "on b.tipobaja= t.codigo "
                "where id>" + str(res.last_remov_id))
            row = cursor.fetchone()
            while row:
                if row[4] != 1:
                    for farm in res.farms_relations:
                        if farm.ifr_farm_name == row[0]:
                            current_farm = farm
                    animal = self.env['farm.animal'].search([
                        ('ifr_sequence', '=', row[1]),
                        ('farm', '=', current_farm.farm.id)])
                    if len(animal) != 0:
                        removal_res_obj = self.env['farm.removal.reason']
                        removal_res = removal_res_obj.search([
                            ('name', '=', row[2])])
                        if len(removal_res) == 0:
                            removal_res = removal_res_obj.create(
                                {'name': row[2]})
                        new_removal = self.env['farm.removal.event'].create({
                            'animal': animal.id,
                            'specie': animal.specie.id,
                            'animal_type': animal.type,
                            'farm': current_farm.farm.id,
                            'timestamp': row[5],
                            'from_location': animal.location.id,
                            'quantity': 1,
                            'reason': removal_res.id,
                            })
                        new_removal.confirm()
                row = cursor.fetchone()

    def sincronize_female(self, conn, animal, farm):
        control = 0
        for cfarm in self.farms_relations:
                        if cfarm.ifr_farm_name == farm:
                            current_farm = cfarm
        last_insemina = self.env['farm.insemination.event'].search([
            ('animal', '=', animal.id),
            ], order='timestamp DESC')
        if len(last_insemina) != 0:
            control = 1
            insemina_day = datetime.strptime(
                    last_insemina[0].timestamp, DTFORMAT)
            last_abort = self.env['farm.abort.event'].search([
                ('animal', '=', animal.id),
                ], order='timestamp DESC')
            if len(last_abort) != 0:
                abort_day = datetime.strptime(
                    last_abort[0].timestamp, DFORMAT)
                if abort_day > insemina_day:
                    control = 0
            if control == 1:
                last_farrow = self.env['farm.farrowing.event'].search([
                    ('animal', '=', animal.id),
                    ], order='timestamp DESC')
                if len(last_farrow) != 0:
                    far_day = datetime.strptime(
                        last_farrow[0].timestamp, DTFORMAT)
                    if far_day > insemina_day:
                        control = 3
                        last_wean = self.env[
                            'farm.weaning.event'].search([
                                ('animal', '=', animal.id),
                                ], order='timestamp DESC')
                        if len(last_wean) != 0:
                            wean_day = datetime.strptime(
                                last_wean[0].timestamp, DTFORMAT)
                            if wean_day > far_day:
                                control = 6
                        else:
                            control = 3
                    else:
                        control = 3
                else:
                    control = 2
        if control == 0:
            insemina = self.lastInsemination(animal, conn, cfarm.ifr_farm_name)
            if insemina[0]:
                insemina_day = insemina[1]
            else:
                control = 6
        if control < 3:
            abort = self.lastAbort(animal, conn, insemina_day, cfarm.ifr_farm_name)
            if abort:
                control = 6
        if control < 3:
            farrow = self.lastFarrowing(animal, conn, insemina_day, cfarm.ifr_farm_name)
            if farrow[0]:
                far_day = farrow[1]
            else:
                control = 6
        if control < 4:
            ref_day = far_day
            last_foster = self.env['farm.foster.event'].search([
                ('animal', '=', animal.id),
                ('farm', '=', current_farm.farm.id)], order='timestamp DESC')
            if len(last_foster) != 0:
                foster_day = datetime.strptime(
                    last_foster[0].timestamp, DFORMAT)
                if foster_day > far_day:
                    ref_day = foster_day
            self.lastFosters(animal, conn, ref_day, farm)
            ref_day = far_day
            self.lastPigletsRemovals(animal, conn, ref_day, farm)
            self.lastWeaning(animal, conn, far_day, farm)

    @api.multi
    def initial_sincronize(self):
        conn = self.connection.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT codi FROM dbo.granjas where codi!='PRUEBA'")
        row = cursor.fetchone()
        farm_code = ''
        control1 = False
        while row:
            control2 = True
            for res in self:
                for farm in res.farms_relations:
                    if row[0] == farm.ifr_farm_name:
                        control2 = False
            if control2:
                control1 = True
                farm_code += row[0] + ' '
            row = cursor.fetchone()
        if control1:
            raise Warning(
                _("farms with code " + farm_code + 'not found'))
        cursor2 = conn.cursor()
        cursor2.execute("select top 1 id from dbo.b_bajareproductores "
                               "order by id desc")
        lastrem = cursor2.fetchone()[0]
        self.initial_males_load(conn)
        self.initial_females_load(conn)
        for res in self:
            res.state = 'sinc'
            res.last_remov_id = lastrem
        self.connection.disconnect(conn)

    def load_last_events(self, conn, animal, farm, initalSinc=False):
        last_insemina = self.lastInsemination(animal, conn, farm, initalSinc)
        if last_insemina[0]:
            last_abort = self.lastAbort(animal, conn, last_insemina[1], farm)
            if not last_abort:
                last_farrow = self.lastFarrowing(
                    animal, conn, last_insemina[1], farm)
                if last_farrow[0]:
                    self.lastFosters(animal, conn, last_farrow[1], farm)
                    self.lastPigletsRemovals(
                        animal, conn, last_farrow[1], farm)
                    self.lastWeaning(animal, conn, last_farrow[1], farm)

    @api.multi
    def initial_males_load(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_GRANJA, ID_ANIMAL, DAT_NAC, DAT_ENTR, loc1,"
            " descripcion FROM dbo.REPRO r inner join dbo.C_CASAGEN c "
            "on r.CASA_GENETICA=c.codigo WHERE SEXO=2"
            "and DAT_ENTR > DAT_BAJ")
        animal_obj = self.env['farm.animal']
        specie_obj = self.env['farm.specie'].search([(True, '=', True)])
        breed_obj = self.env['farm.specie.breed']
        lot_obj = self.env['stock.production.lot']
        row = cursor.fetchone()
        while row:
            raza = breed_obj.search(
                [('name', '=', row[5])])
            if len(raza) == 0:
                raza = breed_obj.create({
                    'specie': specie_obj[0].id,
                    'name': row[5]})
            new_lot = lot_obj.create({
                'product_id': specie_obj[0].male_product.id,
                'animal_type': 'male',
                })
            for res in self:
                for farm in res.farms_relations:
                    if farm.ifr_farm_name == row[0]:
                        current_farm = farm
            animal_obj.create({
                'type': 'male',
                'specie': specie_obj[0].id,
                'breed': raza.id,
                'location': current_farm.loc3.id,
                'farm': current_farm.farm.id,
                'origin': 'raised',
                'lot': [(0, 0, {'lot': new_lot.id})],
                'arrival_date': row[3],
                'initial_location': current_farm.loc3.id,
                'birthdate': row[2],
                'sex': 'male',
                'ifr_sequence': row[1],
                })
            logger.info('Male Sinc')
            row = cursor.fetchone()

    @api.multi
    def initial_females_load(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_GRANJA, ID_ANIMAL, DAT_NAC, DAT_ENTR, descripcion"
            " FROM dbo.REPRO r inner join dbo.C_CASAGEN c "
            "on r.CASA_GENETICA=c.codigo WHERE SEXO=1 and ID_ANIMAL!='       3' "
            "and DAT_ENTR > DAT_BAJ")
        animal_obj = self.env['farm.animal']
        specie_obj = self.env['farm.specie'].search([(True, '=', True)])
        breed_obj = self.env['farm.specie.breed']
        lot_obj = self.env['stock.production.lot']
        row = cursor.fetchone()
        new_females = []
        while row:
            raza = breed_obj.search(
                [('name', '=', row[4])])
            if len(raza) == 0:
                raza = breed_obj.create({
                    'specie': specie_obj[0].id,
                    'name': row[4]})
            new_lot = lot_obj.create({
                'product_id': specie_obj[0].female_product.id,
                'animal_type': 'female',
                })
            for res in self:
                for farm in res.farms_relations:
                    if farm.ifr_farm_name == row[0]:
                        current_farm = farm
            new_animal = animal_obj.create({
                'type': 'female',
                'specie': specie_obj[0].id,
                'breed': raza.id,
                'location': current_farm.loc1.id,
                'farm': current_farm.farm.id,
                'origin': 'raised',
                'lot': [(0, 0, {'lot': new_lot.id})],
                'arrival_date': row[2],
                'initial_location': current_farm.loc1.id,
                'birthdate': row[3],
                'sex': 'female',
                'ifr_sequence': row[1],
                })
            logger.info('Female Sinc')
            new_females.append([new_animal, row[0]])
            row = cursor.fetchone()
        for female in new_females:
            self.load_last_events(conn, female[0], female[1], True)
            logger.info('event Sinc')

    @api.multi
    def lastFosters(self, animal, conn, farrowData, farm):
        for res in self:
            quants_obj = self.env['stock.quant']
            cursor = conn.cursor()
            cursor.execute(
                'SELECT FECHA, ADOPTADOS, RETIRADOS from dbo.adopretir'
                " where ID_ANIMAL='" + animal.ifr_sequence +
                "' and  FECHA > convert(datetime, '" +
                str(farrowData) + "', 121) and ID_GRANJA='"+farm +
                "' order by FECHA ASC")
            row = cursor.fetchone()
            if row:
                new_last_foster = row[0]
            else:
                if res.last_foster_day:
                    new_last_foster = datetime.strptime(
                        res.last_foster_day, DTFORMAT)
                else:
                    new_last_foster = datetime.strptime(
                        '2009-01-01 00:00:00', DTFORMAT)
            while row:
                control = True
                if res.last_foster_day:
                    fost_day = row[0]
                    last_day = datetime.strptime(
                        res.last_foster_day, DTFORMAT)
                    control = fost_day > last_day
                if control:
                    if animal.current_cycle.state == 'lactating':
                        c_f = animal.current_cycle.farrowing_event.event
                        group = c_f.produced_group.animal_group
                        dif = row[1] - row[2]
                        group.quantity = group.quantity + dif
                        target_quant = quants_obj.search([
                            ('lot_id', '=', group.lot.lot.id),
                            ('location_id', '=', group.location.id),
                            ])
                        for q in target_quant:
                            q.qty + dif
                    else:
                        cur_cy = animal.cycles[-1]
                        cur_cy.state = 'lactating'
                        foster_locations = []
                        for loc in animal.specie.foster_location:
                            foster_locations.append(loc.id)
                        foster_loc = self.env['farm.foster.locations'].search(
                            [('location.location_id', '=', animal.farm.id),
                             ('id', 'in', foster_locations),
                             ],
                            ).location
                        self.get_female_move(animal, foster_loc)
                        new_group = self.env['farm.animal.group'].create({
                            'specie': animal.specie.id,
                            'breed': animal.breed.id,
                            'location': animal.location.id,
                            'farm': animal.farm.id,
                            'initial_quantity': row[1] - row[2],
                            'quantity': row[1] - row[2],
                            'origin': 'raised',
                            'arrival_date': fost_day,
                            'initial_location': animal.location.id,
                            'state': 'lactating',
                            })
                        c_f = cur_cy.farrowing_event.event
                        self.env['farm.farrowing.event_group'].create({
                            'event': c_f.id,
                            'animal_group': new_group.id})
                fosterday = row[0]
                if fosterday > new_last_foster:
                    new_last_foster = fosterday
                row = cursor.fetchone()
            res.last_foster_day = new_last_foster

    @api.one
    def get_female_move(self, animal, foster_loc):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        target_quant = quants_obj.search([
            ('lot_id', '=', animal.lot.lot.id),
            ('location_id', '=', animal.location.id),
            ])
        fem_move = moves_obj.create({
            'name': 'foster-mother-' + animal.lot.lot.name,
            'create_date': fields.Date.today(),
            'date': fields.Date.today(),
            'product_id': animal.lot.lot.product_id.id,
            'product_uom_qty': 1,
            'product_uom':
                animal.lot.lot.product_id.product_tmpl_id.uom_id.id,
            'location_id': animal.location.id,
            'location_dest_id': foster_loc.id,
            'company_id': animal.farm.company_id.id, })
        for q in target_quant:
            q.reservation_id = fem_move.id
        fem_move.action_done()
        self.female_move = fem_move
        animal.location = foster_loc
        tags_obj = self.env['farm.tags']
        tag = tags_obj.search([
                ('name', '=', animal.farm.name+'-mated')])
        tag.animal = [(3, animal.id)]
        new_tag = tags_obj.search([
            ('name', '=', animal.farm.name + '-lact')])
        if len(new_tag) == 0:
            new_tag = tags_obj.create({'name': animal.farm.name + '-lact',
                                       })
        animal.tags = [(6, 0, [new_tag.id, ])]

    @api.multi
    def lastWeaning(self, animal, conn, farrowData, farm):
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_GRANJA, DAT_DEST FROM dbo.UltimoMovimiento '
            "WHERE DAT_DEST > convert(datetime, '" +
            str(farrowData) + "' , 121) and ID_GRANJA='" + farm + "'" +
            " and ID_ANIMAL='" + animal.ifr_sequence + "'")
        row = cursor.fetchone()
        if row:
            for res in self:
                for farm in res.farms_relations:
                    if farm.ifr_farm_name == row[0]:
                        current_farm = farm
            c_c = animal.current_cycle
            group = c_c.farrowing_event.event.produced_group.animal_group
            weaning_obj = self.env['farm.weaning.event']
            today_wean = weaning_obj.search([
                ('timestamp', '=', str(row[1])),
                ('farm', '=', current_farm.farm.id)])
            if len(today_wean) != 0:
                group_dest = today_wean[0].weared_group
            else:
                group_dest = group
            group = c_c.farrowing_event.event.produced_group.animal_group
            if c_c.state == 'lactating':
                new_wean = self.env['farm.weaning.event'].create({
                    'animal': animal.id,
                    'specie': animal.specie.id,
                    'animal_type': 'female',
                    'farm': current_farm.farm.id,
                    'timestamp': row[1],
                    'weared_group': group_dest.id,
                    'farrowing_group': group.id,
                    'female_to_location': current_farm.loc1.id,
                    'weaned_to_location': current_farm.loc2.id,
                    })
                new_wean.confirm()

    @api.multi
    def lastPigletsRemovals(self, animal, conn, farrowData, farm):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, idgranja, descripcion, mbaja, fecha, nlechones"
            " from dbo.b_bajalechones b inner join dbo.C_MBLECHON m"
            " on b.mbaja=m.codigo where idanimal='" +
            animal.ifr_sequence +
            " 'and fecha > convert(datetime, '" +
            str(farrowData) + "', 121) and idgranja='"+farm +
            "' order by fecha ASC")
        row = cursor.fetchone()
        remo_obj = self.env['farm.removal.event']
        while row:
            old_rem = remo_obj.search([('ifr_id', '=', row[0])])
            if len(old_rem) == 0:
                for res in self:
                    for farm in res.farms_relations:
                        if farm.ifr_farm_name == row[1]:
                            current_farm = farm
                    removal_res_obj = self.env['farm.removal.reason']
                    removal_res = removal_res_obj.search([
                        ('name', '=', row[2])])
                    if len(removal_res) == 0:
                        removal_res = removal_res_obj.create(
                            {'name': row[2]})
                    c_f = animal.current_cycle.farrowing_event.event
                    group = c_f.produced_group.animal_group
                    new_removal = remo_obj.create({
                        'animal_group': group.id,
                        'specie': animal.specie.id,
                        'animal_type': 'group',
                        'farm': current_farm.farm.id,
                        'timestamp': row[4],
                        'from_location': group.location.id,
                        'quantity': row[5],
                        'reason': removal_res.id,
                        'ifr_id': row[0]
                        })
                    new_removal.confirm()
            row = cursor.fetchone()

    @api.multi
    def lastFarrowing(self, animal, conn, diagData, farm):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT top 1 ID_GRANJA, FPARTO, NM, NMM, NV "
            "from dbo.V_DatosOrdenAnim where ID_ANIMAL='" +
            animal.ifr_sequence +
            "' and FPARTO> convert(datetime, '" +
            str(diagData) + "', 121) and ID_GRANJA='" +
            farm + "' order by FPARTO DESC")
        row = cursor.fetchone()
        if row:
            for res in self:
                for farm in res.farms_relations:
                    if farm.ifr_farm_name == row[0]:
                        current_farm = farm
            if len(animal.cycles)>0:
                current_cycle = animal.cycles[-1]
            else:
                current_cycle = None
            if (len(current_cycle)==0 or current_cycle.diagnosis_events or
                    current_cycle.farrowing_event):
                female_clYcle_obj = self.env['farm.animal.female_cycle']
                f_c = female_clYcle_obj.create(
                    {'animal': animal.id, })
            new_farrow = self.env['farm.farrowing.event'].create({
                'animal': animal.id,
                'specie': animal.specie.id,
                'animal_type': 'female',
                'farm': current_farm.farm.id,
                'timestamp': row[1],
                'live': row[4],
                'stillborn': row[2],
                'mummified': row[3],
                })
            new_farrow.confirm()
            return (True, row[1])
        else:
            return (False, None)

    @api.multi
    def lastAbort(self, animal, conn, diagData, farm):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT top 1 idgranja, fecha from dbo.b_abortos"
            " where idanimal='" + animal.ifr_sequence +
            "' and fecha > convert(datetime, '" +
            str(diagData) + "', 121) and idgranja='"+ farm+"' order by fecha DESC")
        row = cursor.fetchone()
        if row:
            for res in self:
                for farm in res.farms_relations:
                    if farm.ifr_farm_name == row[0]:
                        current_farm = farm
            new_abort = self.env['farm.abort.event'].create({
                'animal': animal.id,
                'especie': animal.specie.id,
                'animal_type': 'female',
                'farm': current_farm.farm.id,
                'timestamp': row[1],
            })
            new_abort.confirm()
            return True
        else:
            return False

    @api.multi
    def lastInsemination(self, animal, conn, farm, initialSinc=False):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT top 1 N_CUBRI, ID_ANIMAL, ID_GRANJA,N_ORDEN, DAT_CUBRI, "
            "lote from dbo.CUBRI where ID_ANIMAL='" +
            animal.ifr_sequence + "' and ID_GRANJA='"+farm +
            "' order by DAT_CUBRI DESC")
        row = cursor.fetchone()
        if row:
            for res in self:
                    for farm in res.farms_relations:
                        if farm.ifr_farm_name == row[2]:
                            current_farm = farm
            if initialSinc:
                current_cycle = animal.current_cycle
                if (len(current_cycle)==0 or current_cycle.diagnosis_events or
                        current_cycle.farrowing_event):
                    female_clicle_obj = self.env['farm.animal.female_cycle']
                    current_cycle = female_clicle_obj.create(
                        {'animal': animal.id, })
                animal.state = 'mated'
                current_cycle.state = 'mated'
                dose_bom = self.env['mrp.bom'].search([
                        ('specie', '=', animal.specie.id),
                        ('semen_dose', '=', True)])
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', dose_bom.product_tmpl_id.id)])
                insemination_ev = self.env['farm.insemination.event'].create({
                    'animal': animal.id,
                    'specie': animal.specie.id,
                    'animal_type': 'female',
                    'farm': current_farm.farm.id,
                    'timestamp': row[4],
                    'dose_product': product.id,
                    'female_cycle': current_cycle.id,
                    'dose_bom': dose_bom.id})
                insemination_ev.state = 'validated'
                tags_obj = self.env['farm.tags']
                tag = tags_obj.search([
                    ('name', '=', current_farm.farm.name + '-unmated')])
                tag.animal = [(3, animal.id)]
                new_tag = tags_obj.search([
                    ('name', '=', current_farm.farm.name + '-mated')])
                if len(new_tag) == 0:
                    new_tag = tags_obj.create({
                        'name': current_farm.farm.name + '-mated', })
                animal.tags = [(6, 0, [new_tag.id, ])]
            else:
                cursor2 = conn.cursor()
                cursor2.execute(
                    'SELECT COD_VERRO FROM dbo.MONTAS WHERE N_CUBRI=' +
                    str(row[0]))
                row2 = cursor2.fetchone()
                if row2:
                    male = self.env['farm.animal'].search([
                        ('ifr_sequence', '=', row2[0])])
                    semen_extrac = self.env['farm.semen_extraction.event'].search([
                        ('animal', '=', male.id)], order='timestamp DESC')
                else:
                    semen_extrac = []
                job_order_obj = self.env['farm.event.order']
                job_order = job_order_obj.search(
                    [('ifr_id', '=', row[3]), ('farm', '=', current_farm.farm.id)])
                if len(job_order) == 0:
                    job_order = job_order_obj.create({
                        'ifr_id': row[3],
                        'animal_type': 'female',
                        'specie': animal.specie.id,
                        'event_type': 'insemination',
                        'farm': current_farm.farm.id,
                        'timestamp': row[4],
                        'notes': _('Autogenerated order by irf program')
                        })
                control = True
                if len(semen_extrac) != 0:
                    semen_extracti = semen_extrac[0]
                    self.env['insemination.event'].create({
                        'animal': animal.id,
                        'specie': animal.specie.id,
                        'animal_type': 'female',
                        'farm': current_farm.farm.id,
                        'job_order': job_order.id,
                        'timestamp': row['DAT_CUBRI'],
                        'dose_product': semen_extracti.doses[0].dose_product.id,
                        'dose_lot': semen_extracti.doses[0].lot.id,
                        'dose_bom': semen_extracti.dose_bom})
                else:
                    dose_bom = self.env['mrp.bom'].search([
                        ('specie', '=', animal.specie.id),
                        ('semen_dose', '=', True)])
                    product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', dose_bom.product_tmpl_id.id)])
                    lots = self.env['stock.quant'].search([
                        ('product_id', '=', product.id)])
                    if len(lots)==0:
                        control = False
                    else:
                        lot = lots[0].lot_id
                        self.env['farm.insemination.event'].create({
                            'animal': animal.id,
                            'specie': animal.specie.id,
                            'animal_type': 'female',
                            'farm': current_farm.farm.id,
                            'job_order': job_order.id,
                            'dose_lot': lot.id,
                            'timestamp': row[4],
                            'dose_product': product.id,
                            'dose_bom': dose_bom.id})
                if control:
                    job_order.confirm()
                else:
                    logger.info('No hay stock de semen disponible')
                    return (False, None)
            return (True, row[4])
        else:
            return (False, None)


class FarmsRelation(models.Model):
    _name = 'farm.ifr.farms.relation'

    ifr_connector = fields.Many2one(comodel_name='farm.ifr.connector',
                                    string='ifr.connector')
    farm = fields.Many2one(comodel_name='stock.location',
                           domain=[('usage', '=', 'view'), ])
    loc1 = fields.Many2one(comodel_name='stock.location',
                           string='Females Yard',
                           domain=[('usage', '=', 'internal')])
    loc2 = fields.Many2one(comodel_name='stock.location',
                           string='Transit Location',
                           domain=[('usage', '=', 'transit')])
    loc3 = fields.Many2one(comodel_name='stock.location',
                           string='stallion location',
                           domain=[('usage', '=', 'internal')])
    ifr_farm_name = fields.Char(string='code in IFR program')
