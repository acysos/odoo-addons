/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { Component } from "@odoo/owl";
$(document).on('change', '#live', function(ev) {
    var live = parseInt($('#live').val());

    if (live < 1) {
        $('.div_label1, .div_label2, .div_label3, .div_label4, .div_label5').hide();
    } else if (live == 1) {
        $('.div_label1').show();
        $('.div_label2, .div_label3, .div_label4, .div_label5').hide();
    } else if (live == 2) {
        $('.div_label1, .div_label2').show();
        $('.div_label3, .div_label4, .div_label5').hide();
    } else if (live == 3) {
        $('.div_label1, .div_label2, .div_label3').show();
        $('.div_label4, .div_label5').hide();
    } else if (live == 4) {
        $('.div_label1, .div_label2, .div_label3, .div_label4').show();
        $('.div_label5').hide();
    } else if (live == 5) {
        $('.div_label1, .div_label2, .div_label3, .div_label4, .div_label5').closest('.form-row').show();
    }
    $('.next_farrowing').show();
});

publicWidget.registry.websiteFarmFarrowingModal = publicWidget.Widget.extend({
    selector: '.farrowing_modal',
    events: Object.assign({}, {}, {
        'change #live': '_onchangelive',
        'click #next_farrowing': '_onclicknext',
        'click #farrowing_req_submit': '_onclicksubmit',

        }),
        init: function(){
            this._super.apply(this, arguments);
            this.rpc = this.bindService("rpc");

        },
        async start() {
            jsonrpc("/farm/farrowing/request").then(function (vals){
                        $('.farrow_body').html(vals);
                        var test = $('.modal').modal('show');
                        test.find('.div_label1').hide();
                        test.find('.div_label2').hide();
                        test.find('.div_label3').hide();
                        test.find('.div_label4').hide();
                        test.find('.div_label5').hide();
                        test.find('.next_farrowing').hide();

                        });


            const def = this._super(...arguments);
            var self = this;
            $(document).on('click', '#next_farrowing', function(ev) {

                self._next_farrowing(ev);
            });
            $(document).on('click', '#farrowing_req_submit', function(ev) {
                self._onclicksubmit(ev);
            });
            $(document).on('change', '#name', function(ev) {
                self._onchangename(ev);
            });

            return def;
            },
        destroy() {
                this._super.apply(this, arguments);
            },
    _onchangename: function(ev){
         var label = $(ev.target).parents('.farrowing_req_form').find('#name').val();
         $(ev.target).parents('.farrowing_req_form').find('#farm').text('').change();
         $(ev.target).parents('.farrowing_req_form').find('#arrival_date').text('').change();
         $(ev.target).parents('.farrowing_req_form').find('#origin').text('').change();
         $(ev.target).parents('.farrowing_req_form').find('#last_farrowing').text('').change();
         if(label == ''){
            $(ev.target).parents('.farrowing_req_form').find('.error-label').text('').change();

         }
         else{
         jsonrpc("/farm/search/animal", {'farm_label': label}).then(function (vals){

            if('error' in vals){
                $(ev.target).parents('.farrowing_req_form').find('.error-label').text(vals['error']).change();
            }else{

            if(vals['type'] == 'group'){
                $(ev.target).parents('.farrowing_req_form').find('.error-label').text('Crotal de Cordero').change();

            }
            else{
                $(ev.target).parents('.farrowing_req_form').find('.error-label').text('').change();
                $(ev.target).parents('.farrowing_req_form').find('#farm').text(vals['farm']).change();
                $(ev.target).parents('.farrowing_req_form').find('#arrival_date').text(vals['arrival_date']).change();
                $(ev.target).parents('.farrowing_req_form').find('#origin').text(vals['origin']).change();
                $(ev.target).parents('.farrowing_req_form').find('#last_farrowing').text(vals['last_farrowing']).change();
            }}
         });
            }
    },
    _onclicksubmit: function(ev){
        console.log('submit');
        var farm_label = $(ev.target).parents('.farrowing_req_form').find('.farm').val();

        var live = $(ev.target).parents('.farrowing_req_form').find('#live').val();
        var label = $(ev.target).parents('.farrowing_req_form').find('#name').val();
        var order = $(ev.target).parents('.farrowing_req_form').find('#order_id').val();
        if(label != '' && live != 0){

            var employee_id = $(ev.target).closest('form').find('#employee_id').val()
            var label1 = $(ev.target).parents('.farrowing_req_form').find('#label1').val();
            var label2 = $(ev.target).parents('.farrowing_req_form').find('#label2').val();
            var label3 = $(ev.target).parents('.farrowing_req_form').find('#label3').val();
            var label4 = $(ev.target).parents('.farrowing_req_form').find('#label4').val();
            var label5 = $(ev.target).parents('.farrowing_req_form').find('#label5').val();
            if($(ev.target).parents('.farrowing_req_form').find('#male1').checked){
                var sex1 = 'male';
            }else{
                var sex1 = 'female';
            }
            if($(ev.target).parents('.farrowing_req_form').find('#male2').checked){
                var sex2 = 'male';
            }else{
                var sex2 = 'female';
            }
            if($(ev.target).parents('.farrowing_req_form').find('#male3').checked){
                var sex3 = 'male';
            }else{
                var sex3 = 'female';
            }

            console.log(sex1)
            console.log($(ev.target).parents('.farrowing_req_form').find('#male11'))

            var values = {'farm_label': label, 'live': live, 'order': order, 'label1': label1, 'label2':
            label2, 'label3': label3, 'label4': label4, 'label5': label5, 'sex1': sex1, 'sex2': sex2,
            'sex3': sex3, 'sex4': sex4, 'sex5': sex5}
            console.log(values);
            jsonrpc("/farm/next_farrowing", values).then(function (vals){
                if(vals){
                    console.log(vals);
                    console.log($(ev.target).parents('.farrowing_req_form').find('.error-label'));
                    $(ev.target).parents('.farrowing_req_form').find('.error-label').text(vals['error']).change();
                    return false;
                }
                else{
                    $(ev.target).parents('.farrowing_req_form').find('#live').val(0).change();
                    $(ev.target).parents('.farrowing_req_form').find('.#name').val('').change();
                    $(ev.target).parents('.error-div').find('.error-label').val('').change();
                    $('#label1').val('').change();
                    $('#label2').val('').change();
                    $('#label3').val('').change();
                    $('#label4').val('').change();
                    $('#label5').val('').change();
                    $(ev.target).parents('.farrowing_req_form').find('.next_farrowinf').text('').change();
                     jsonrpc("/farm/farrowing/submit", {'order': order}).then(function (vals){
                                $(".modal").modal('hide');
                                $(vals).appendTo('body');
                                //$(vals).modal('show');
                                return false;
                    });
                    }
                });
        }
        else{
        console.log('submit');
        jsonrpc("/farm/farrowing/submit", {'order': order}).then(function (vals){
            $(".modal").modal('hide');
            $(vals).appendTo('body');
            //$(vals).modal('show');
            return false;
        });
        }
        },

    _next_farrowing: function(ev){
        var farm_label = $(ev.target).parents('.farrowing_req_form').find('.farm').val();
        var employee_id = $(ev.target).closest('form').find('#employee_id').val()
        var label = $(ev.target).parents('.farrowing_req_form').find('#name').val();
        var live = $(ev.target).parents('.farrowing_req_form').find('#live').val();
        var order = $(ev.target).parents('.farrowing_req_form').find('#order_id').val();
        var label1 = $(ev.target).parents('.farrowing_req_form').find('#label1').val();
        var label2 = $(ev.target).parents('.farrowing_req_form').find('#label2').val();
        var label3 = $(ev.target).parents('.farrowing_req_form').find('#label3').val();
        var label4 = $(ev.target).parents('.farrowing_req_form').find('#label4').val();
        var label5 = $(ev.target).parents('.farrowing_req_form').find('#label5').val();
        var label1 = $(ev.target).parents('.farrowing_req_form').find('#label1').val();
        var label2 = $(ev.target).parents('.farrowing_req_form').find('#label2').val();
        var label3 = $(ev.target).parents('.farrowing_req_form').find('#label3').val();
        var label4 = $(ev.target).parents('.farrowing_req_form').find('#label4').val();
        var label5 = $(ev.target).parents('.farrowing_req_form').find('#label5').val();
        var sex1 = document.querySelector('input[name="sex1"]:checked').value;
        var sex2 = document.querySelector('input[name="sex2"]:checked').value;
        var sex3 = document.querySelector('input[name="sex3"]:checked').value;
        var sex4 = document.querySelector('input[name="sex4"]:checked').value;
        var sex5 = document.querySelector('input[name="sex5"]:checked').value;

        console.log(sex1)

        console.log(document.querySelector('input[name="sex1"]:checked').value)

        var values = {'farm_label': label, 'live': live, 'order': order, 'label1': label1, 'label2':
        label2, 'label3': label3, 'label4': label4, 'label5': label5, 'sex1': sex1, 'sex2': sex2,
        'sex3': sex3, 'sex4': sex4, 'sex5': sex5}
        console.log(values);
        jsonrpc("/farm/next_farrowing", values).then(function (vals){
            if(vals){
                console.log(vals);
                console.log($(ev.target).parents('.farrowing_req_form').find('.error-label'));
                $(ev.target).parents('.farrowing_req_form').find('.error-label').text(vals['error']).change();
            }
            else{
                $(ev.target).parents('.farrowing_req_form').find('#live').val(0).change();
                $(ev.target).parents('.farrowing_req_form').find('.farm_label').val('').change();
                $(ev.target).parents('.error-div').find('.error-label').val('').change();
                $('#label1').val('').change();
                $('#label2').val('').change();
                $('#label3').val('').change();
                $('#label4').val('').change();
                $('#label5').val('').change();


            }
        });

},


});
publicWidget.registry.websiteFarm = publicWidget.Widget.extend({
    selector: '.farrowing_menu',
    events: Object.assign({}, {}, {
        'click .farrowing_req_btn': '_onclick_open_farrowing',
        }),
        init: function(){
            console.log('init');
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

    _onclick_open_farrowing: function(ev){
        var PublicWidgetFarrowingModalExtend = new publicWidget.registry.websiteFarmFarrowingModal(this);
            PublicWidgetFarrowingModalExtend.appendTo($(".farrowing_modal"));
            return publicWidget.registry.websiteFarmFarrowingModal;
                },



        });
