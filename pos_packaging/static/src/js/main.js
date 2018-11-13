// Copyright (c) 2018 Alexander Ezquevo <alexander@acysos.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define('pos_product_packaging', function (require) {
"use strict";

var DB = require('point_of_sale.DB');
var models = require('point_of_sale.models');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;


var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
	initialize: function(session, attributes) {
        _super_posmodel.initialize.apply(this, arguments);
        var self = this;
        this.packages = [];
    },
	scan_product: function(parsed_code){
		console.log("scan")
		var selectedOrder = this.get_order();
		var pro_package = this.db.get_packaging_by_barcode(parsed_code)
		if (!pro_package){
			console.log(pro_package)
			console.log("super")
			return _super_posmodel.scan_product.apply(this, arguments);
		}
		else{
			for(var i = 0, len=pro_package.qty; i < len; i++){
				console.log("for")
				console.log(pro_package.product_id)
				selectedOrder.add_product(this.db.get_product_by_id(pro_package.product_id[0]));
			}
			return true;
		}
		}
	});

models.load_models({
        model: 'product.packaging',
        fields: ['id','product_id', 'barcode', 'qty'],
        domain: [],
        loaded: function(self, packages) {
            self.packages = packages;
            self.db.add_pakaging(packages);
        }
    });
DB.include({
	init: function( options ){
        this._super(options);
        this.product_packaging_by_barcode = {}
 },
 	add_pakaging: function(packages){
 		if(!packages instanceof Array){
 			packages = [pakages]
 		}
 		for(var i = 0, len = packages.length; i < len; i++){
 			var pro_package = packages[i]
 			this.product_packaging_by_barcode[pro_package.barcode] = pro_package
 		}
 	},
 	get_packaging_by_barcode: function(barcode){
        if(this.product_packaging_by_barcode[barcode.code]){
            return this.product_packaging_by_barcode[barcode.code];
        } else {
            return undefined;
        }
    },
});
});
		