/******************************************************************************
 * Copyright (C) 2018 Acysos SL (<http://www.acysos.com>).
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 ******************************************************************************/

odoo.define('pos_open_cashbox_log.log_open', function (require) {
    "use strict";

  var Model = require('web.DataModel');
  var models = require('point_of_sale.models');
  var screens = require('point_of_sale.screens');

  // add `default_payment_method_id` to loaded pos config's fields
  models.load_fields("pos.config", "proxy");

  screens.PaymentScreenWidget.include({
	  renderElement: function(){
	      this._super();
	      self = this;
	      // activate open cashbox log method
	      this.$('.js_cashdrawer').click(function(){
	    	  var cashier = self.pos.cashier || self.pos.user;
	    	  var session_id = self.pos.pos_session.id;
	    	  new Model('pos.open.cashbox.log').call('open_cashbox', ['Manual open', 'Manual open', cashier ? cashier.id : 0, session_id]);
	      });
	  },
	  finalize_validation: function(){
		  this._super();
		  self = this;
          var order = this.pos.get_order();
          if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 
        	  var cashier = self.pos.cashier || self.pos.user;
	    	  var session_id = self.pos.pos_session.id;
	    	  new Model('pos.open.cashbox.log').call('open_cashbox', ['Validate open', 'Validate open', cashier ? cashier.id : 0, session_id]);
          }
	  }
  });

});
