/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { Component } from "@odoo/owl";

publicWidget.registry.websiteRemovalEvent = publicWidget.Widget.extend({
    selector: '.removal_req_form',
    events: Object.assign({}, {}, {
        'click .removal_req_btn': '_onclick_removal_event',
        "change select[name='reason_id']": '_onchange_reason',
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

        _onchange_reason: function(ev) {

            $(ev.currentTarget).closest('form').find('#selecionado').text($(ev.currentTarget).val()).change();
        },
        _onclick_removal_event: function(ev) {
            var removal_label = $(ev.currentTarget).parents('.removal_req_form').find('.farm_label').val();
            var employee_id = $(ev.currentTarget).parents('.removal_req_form').find('#employee_id').val();
            var reason = $(ev.currentTarget).parents('.removal_req_form').find('#selecionado').text();
            jsonrpc("/farm/removal/submit", {
                'employee_id': employee_id, 'tag': removal_label, 'reason': reason
            }).then(function (vals){
                console.log(vals);


            });
        }
});