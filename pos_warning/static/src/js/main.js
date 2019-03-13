// Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define('pos_warning', function (require) {
"use strict";

var core = require('web.core');
var models = require('point_of_sale.models');
var screen = require('point_of_sale.screens');
var _t = core._t;

models.load_fields("res.partner", "sale_warn");
models.load_fields("res.partner", "sale_warn_msg");
screen.ClientListScreenWidget = screen.ClientListScreenWidget.include({
	line_select: function(event,$line,id){
		var self = this
		var partner = this.pos.db.get_partner_by_id(id);
		if(partner.sale_warn === 'no-message' | $line.hasClass('highlight')){
			return this._super(event,$line,id);
			}
		else
			{
				self.gui.show_popup('alert',{
	           		title: _t(partner.sale_warn_msg)
				});
				if(partner.sale_warn === 'warning')
	           				{
	           					console.log('warning')
	           					self._super(event,$line,id);
	           				};
	           			

			}
		}
	});

	
});


