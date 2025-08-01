/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { Component } from "@odoo/owl";

publicWidget.registry.websiteFarmAnimalSearch = publicWidget.Widget.extend({
    selector: '.animal_search',
    events: Object.assign({}, {}, {
        'change #name': '_onchangelabel',
        }),
        init: function(){
            this._super.apply(this, arguments);
            this.rpc = this.bindService("rpc");


        },
        async start() {

            const def = this._super(...arguments);
            return def;
            },
            destroy() {
                    this._super.apply(this, arguments);
                },
        _onchangelabel: function(ev) {

            var label = $(ev.target).parents('.animal_search').find('#name').val();
            $(ev.target).parents('.animal_search').find('#type').text('').change();
                     $(ev.target).parents('.animal_search').find('#farm').text('').change();
                     $(ev.target).parents('.animal_search').find('#arrival_date').text('').change();
                     $(ev.target).parents('.animal_search').find('#origin').text('').change();
                     $(ev.target).parents('.animal_search').find('#last_farrowing').text('').change();
                        $(ev.target).parents('.animal_search').find('#mother').text('').change();
                     if(label == ''){
                        $(ev.target).parents('.animal_search').find('.error-label').text('').change();

                     }
                     else{
                        jsonrpc("/farm/search/animal", {'farm_label': label}).then(function (vals){
                                    console.log(vals);
                                    if('error' in vals){
                                        $(ev.target).parents('.animal_search').find('.error-label').text(vals['error']).change();
                                    }else{
                                        $(ev.target).parents('.animal_search').find('.error-label').text('').change();
                                        $(ev.target).parents('.animal_search').find('#type').text(vals['type']).change();
                                        $(ev.target).parents('.animal_search').find('#farm').text(vals['farm']).change();
                                        $(ev.target).parents('.animal_search').find('#arrival_date').text(vals['arrival_date']).change();
                                        $(ev.target).parents('.animal_search').find('#origin').text(vals['origin']).change();
                                        $(ev.target).parents('.animal_search').find('#last_farrowing').text(vals['last_farrowing']).change();
                                        $(ev.target).parents('.animal_search').find('#mother').text(vals['mother']).change();
                                    }
                                    });
                     }
        }
});