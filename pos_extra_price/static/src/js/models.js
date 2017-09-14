function pos_extra_price_models(instance, module) {
	var round_pr = instance.web.round_precision
	module.Order = module.Order.extend({
		addProduct: function(product, options){
			if(this._printed){
                this.destroy();
                return this.pos.get('selectedOrder').addProduct(product, options);
            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            var last_orderline = this.getLastOrderline();
            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                last_orderline.merge(line);
            }else{
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
			if(product.extra_price !== 0){
				var product_extra = this.pos.db.get_product_by_id(product.product_id_extra[0]);
				var extraline = new module.Orderline({}, {pos: this.pos, order: this, product: product_extra});
				if(options.quantity !== undefined){
	                extraline.set_quantity(options.quantity * product.extra_price_qty);
	            }else{
	            	extraline.set_quantity(product.extra_price_qty);
	            }
	            if(options.price !== undefined){
	                extraline.set_unit_price(product.extra_price);
	            }
	            this.get('orderLines').add(extraline);
			}
		}
	});
	module.Orderline = module.Orderline.extend({
		get_extra_line: function(){
			if(this.order === null){
				return null
			}
			var orderlines = this.order.get('orderLines').models;
            for(var i = 0; i < orderlines.length; i++){
                if(orderlines[i].id === this.id +1){
                    return orderlines[i];
                }
            }
            return null;
		},
		set_quantity: function(quantity){
			if(quantity === 'remove'){
				if(this.product !== null && this.product.extra_price !== 0){
					var extraline = this.get_extra_line();
					this.order.removeOrderline(extraline);
				}
                this.order.removeOrderline(this);
                return;
            }else{
            	if (this.product && this.product.extra_price !== 0){
            		var extraqty = quantity * this.product.extra_price_qty;
            		var extraline = this.get_extra_line();
            		if( extraline !== null){
            			extraline.set_quantity(extraqty);}
            	}
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();

                if(unit){
                    if (unit.rounding) {
                        this.quantity    = round_pr(quant, unit.rounding);
                        var decimals = Math.ceil(Math.log(1.0 / unit.rounding) / Math.log(10));
                        this.quantityStr = openerp.instances[this.pos.session.name].web.format_value(this.quantity, { type: 'float', digits: [69, decimals]});
                    } else {
                        this.quantity    = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                }else{
                    this.quantity    = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }
            this.trigger('change',this);
        }



		}
	);
	module.PosModel.prototype.models.push(
		{model:'product.product',
		fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                     'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                     'product_tmpl_id', 'product_id_extra', 'extra_price', 'extra_price_qty'],
        domain: [['sale_ok','=',true],['available_in_pos','=',true]],
            context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
            loaded: function(self, products){
                self.db.add_products(products);
            }
        }
    );
	
	

}