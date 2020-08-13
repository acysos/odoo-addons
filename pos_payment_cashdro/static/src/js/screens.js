/*
    POS Payment Cashdro module for Odoo
    Copyright (C) 2020 Acysos S.L. (www.acysos.com)
    Copyright (C) 2014-2016 Aurélien DUMAINE
    Copyright (C) 2014-2016 Akretion (www.akretion.com)
    @author: Ignacio Ibeas <ignacio@acysos.com>
    @author: Aurélien DUMAINE
    @author: Alexis de Lattre <alexis.delattre@akretion.com>
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

odoo.define('pos_payment_terminal.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');

    function sleep(duration) {
    	return new Promise(resolve => {
    		setTimeout(() => {
    			resolve()
    		}, duration * 1000)
    	})
    }
    
    screens.PaymentScreenWidget.include({

        render_paymentlines : function(){
            this._super.apply(this, arguments);
            var self = this;
            this.$('.paymentlines-container').unbind('click').on('click', '.payment-cashdro-start', function(event){
                self.pos.get_order().in_cashdro = true;
                self.order_changes();
                self.payment_cashdro($(this).data('cid'), self.pos.currency.name, self.pos.currency.decimals);
            });
            this.$('.payment-cashdro-stop').click(function(event){
            	self.payment_cashdro_stop(self.pos.get_order().cashdro_operationID);
            });          
        },
        
        payment_cashdro: async function(line_cid, currency_iso, currency_decimals){
        	var self = this;
            var line;
            var order = self.pos.get_order();
            var lines = order.get_paymentlines();
            for ( var i = 0; i < lines.length; i++ ) {
                if (lines[i].cid === line_cid) {
                    line = lines[i];
                }
            }
            var url_send = 'https://' + self.pos.config.cashdro_ip;
            url_send += '/Cashdro3WS/index.php?operation=startOperation';
            url_send += '&name=' + self.pos.config.cashdro_user;
            url_send += '&password=' + self.pos.config.cashdro_password;
            url_send += '&type=4';
            url_send += '&posid=pos-' + self.pos.pos_session.name;
            url_send += '&posuser=' + self.pos.get_cashier().id;
            var data = {
        		'amount' : order.get_due(line).toFixed(currency_decimals) * 100
            };
            url_send += '&parameters=' + JSON.stringify(data);
            console.log(url_send);
            var response_send = null;
            // Test
//            response_send = {'code': 1, 'data': 111}
            $.ajax({
            	  url: url_send,
            	  dataType: 'json',
            	  async: false,
            	  success: function(response) {
            		  response_send = response;
            	  }
            	});
            console.log(response_send);
            self.pos.get_order().cashdro_operationID = response_send['data']
            var url_start = 'https://' + self.pos.config.cashdro_ip;
            url_start += '/Cashdro3WS/index.php?operation=acknowledgeOperationId';
            url_start += '&name=' + self.pos.config.cashdro_user;
            url_start += '&password=' + self.pos.config.cashdro_password;
            url_start += '&operationId=' + response_send['data'];
            console.log(url_start);
            var response_start = null;
            $.ajax({
            	  url: url_start,
            	  dataType: 'json',
            	  async: false,
            	  success: function(response) {
            		  response_start = response;
            	  }
            	});
            // Test
//            response_start = {'code': 1, 'data': ''}
            console.log(response_start);
            var url_ask = 'https://' + self.pos.config.cashdro_ip;
            url_ask += '/Cashdro3WS/index.php?operation=askOperation';
            url_ask += '&name=' + self.pos.config.cashdro_user;
            url_ask += '&password=' + self.pos.config.cashdro_password;
            url_ask += '&operationId=' + response_send['data'];
            console.log(url_ask);
            var response_ask = null;
            $.ajax({
          	  url: url_ask,
          	  dataType: 'json',
          	  async: false,
          	  success: function(response) {
          		response_ask = response;
          	  }
          	});
            console.log(response_ask);
            var response_ask_data = jQuery.parseJSON(response_ask['data']);
            // Test
//            response_ask_data = {'code': 1};
//            response_ask_data['state'] = 'E';
            console.log(response_ask_data);
            while (response_ask_data['operation']['state'] != 'F') {
            	await sleep(5);
                $.ajax({
                	  url: url_ask,
                	  dataType: 'json',
                	  async: false,
                	  success: function(response) {
                		response_ask = response;
                	  }
                	});
                response_ask_data = jQuery.parseJSON(response_ask['data']);
//        		response_ask_data['state'] = 'F';
                console.log(response_ask_data)
            }
            if (response_ask_data['operation']['state'] == 'F') {
        		self.pos.get_order().in_cashdro = false;
//        		line.set_amount(order.get_due(line));
        		line.set_amount(response_ask_data['operation']['totalin']/100);
            }
            self.order_changes();
            self.render_paymentlines();
            self.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(response_ask_data['operation']['totalin']/100));
        },

        payment_cashdro_stop: async function(cashdro_operationID){
        	var self = this;
        	var url_stop = 'https://' + self.pos.config.cashdro_ip;
        	url_stop += '/Cashdro3WS/index.php?operation=finishOperation';
        	url_stop += '&name=' + self.pos.config.cashdro_user;
        	url_stop += '&password=' + self.pos.config.cashdro_password;
        	url_stop += '&operationId=' + cashdro_operationID;
        	url_stop += '&type=2';
            console.log(url_stop);
            var response_stop = null;
            $.ajax({
            	  url: url_stop,
            	  dataType: 'json',
            	  async: false,
            	  success: function(response) {
            		  response_stop = response;
            	  }
            	});
            // Test
//            response_stop = {'code': 1, 'data': ''}
            if (response_stop['data'] == '') {
            	self.pos.get_order().in_cashdro = false;
            	self.pos.get_order().cashdro_operationID = false;
            }
            self.order_changes();
        },

        order_changes: function(){
            this._super.apply(this, arguments);
            var order = this.pos.get_order();
            if (!order) {
                return;
            } else if (order.in_cashdro) {
                self.$('.next').html('<img src="/web/static/src/img/spin.png" style="animation: fa-spin 1s infinite steps(12);width: 20px;height: auto;vertical-align: middle;">');
                self.$('.payment-cashdro-start').addClass('oe_hidden');
                self.$('.payment-cashdro-stop').removeClass('oe_hidden');
            } else {
                self.$('.next').html('Validate <i class="fa fa-angle-double-right"></i>');
                self.$('.payment-cashdro-start').removeClass('oe_hidden');
                self.$('.payment-cashdro-stop').addClass('oe_hidden');
            }
        }
    });

});
