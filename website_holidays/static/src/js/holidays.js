odoo.define('website_holidays.timeoff_request', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');

    $(document).ready(function () {

        $(document).on("click", ".timeoff_req_btn", function(e) {
            ajax.jsonRpc("/timeoff/request", 'call', {}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
                test.find('.period_unit').hide();
                test.find('.div_unit_half').hide();
                test.find('.div_custom_hour').hide();

            });
        });

         $(document).on("click", ".holiday_req_btn", function(e) {
            ajax.jsonRpc("/holiday/request", 'call', {}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
                test.find('.period_unit').hide();
                test.find('.div_unit_half').hide();
                test.find('.div_custom_hour').hide();
            });
        });

        var req_unit = '';
        $(document).on("change", ".input_date_to", function(e) {
            var rf = $(this).parents('.timeoff_req_form').find('.input_date_from').val();
            var rt = $(this).parents('.timeoff_req_form').find('.input_date_to').val();
            var rpc = require('web.rpc')
            var employee_id = $(this).closest('form').find('#employee_id').val()
            console.log('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHh')
            console.log(employee_id)
            var self = this
            if(rf <= rt){
                rpc.query({model:'hr.leave', method: 'get_rpc_days', args:[rf, rt, employee_id] }).then(function(result){
                    $(self).parents('.timeoff_req_form').find('#number_of_days').val(result).change();

            });
            }
        });

        $(document).on("change", ".input_date_from", function(e) {
            $(this).parents('.timeoff_req_form').find('.input_date_to').val('');
            $(this).parents('.timeoff_req_form').find('#number_of_days').val(0);
        });

        function show_timeoff_fields(vals){
            if (vals == 'hour'){
                //$('.div_unit_half').show();
                //$('.div_custom_hour').show();
                $('.from_to_hours').show();
                $('.duration').show();
                $('.end_date').hide();
                $('.period_unit').hide();
            }
            else if(vals == 'half_day'){
                $('.div_unit_half').show();
                $('.div_custom_hour').hide();
                $('.period_unit').hide();
                $('.from_to_hours').hide();
                $('.duration').show();
                $('.end_date').show();
            }
            else if(vals == 'day'){
                $('.div_unit_half').hide();
                $('.div_custom_hour').hide();
                $('.period_unit').hide();
                $('.from_to_hours').hide();
                $('.end_date').show();
                $('.duration').show();
            }
        }

        $(document).on('change', "select[name='t_id']", function() {
            req_unit = $(this).parents('.timeoff_req_form').find('.request_unit').val();
            $(this).closest('form').find('#selecionado').text($(this).val()).change();
            ajax.jsonRpc("/timeoff/request/request_unit", 'call', {'timeoff_type': $(this).val()}).then(function (vals)
            {
                show_timeoff_fields(vals);
            });
        });
        $(document).on('change', "select[name='hf_id']", function() {
            $(this).closest('form').find('#selecionado_hf').text($(this).val()).change();
            var hf = parseFloat($(this).val())
            var ht = parseFloat($(this).parents('form').find('#selecionado_ht').text())
            var result = (ht - hf).toString()
            $(this).parents('.timeoff_req_form').find('#number_of_days').val(result).change();
        });
        $(document).on('change', "select[name='ht_id']", function() {
            $(this).closest('form').find('#selecionado_ht').text($(this).val()).change();
            var hf = parseFloat($(this).parents('form').find('#selecionado_hf').text())
            var ht = parseFloat($(this).val())
            var result = (ht - hf).toString()
            $(this).parents('.timeoff_req_form').find('#number_of_days').val(result).change();
        });

        $(document).on("click", "#btn_reload", function(e) {
            location.reload()
        });

        $(document).on("click", ".o_request_unit_hours", function(e) {
            if ($(this).is(":checked")) {
                $(this).parents('.timeoff_req_form').find('.period_unit').hide();
                $(this).parents('.timeoff_req_form').find('.from_to_hours').show();
            } else {
                $(this).parents('.timeoff_req_form').find('.from_to_hours').hide();
            }
        });

        $(document).on("click", "#timeoff_req_submit", function(e) {
            var $form = $(this).closest('form');
            $(".holy_buttons").hide()
            var request_date_from = $form.find('input[name="req_date_from"]').val();
            var request_date_to = $form.find('input[name="req_date_to"]').val();
            var duration = $form.find('input[name="number_of_days"]').val();
            var unit_hour = $(this).parents('.timeoff_req_form').find('#o_request_unit_hours').val();
            var period = $(this).parents('.timeoff_req_form').find('#rd_id').val();
            var holiday_status_id = $(this).parents('form').find('#selecionado').text();
            var hour_from = $(this).parents('form').find('#selecionado_hf').text();
            var hour_to = $(this).parents('form').find('#selecionado_ht').text();
            var msg = '';
            var attachment = $form.find('input[name="req_attach"]').val()
            var name = $form.find('textarea[name="name"]').val()

            if (name == "") {
                $form.find('textarea[name="name"]').addClass('is-invalid')
                $(".holy_buttons").hide().show()
                return false;
            }
            if (request_date_from == "") {
                $form.find('input[name="req_date_from"]').addClass('is-invalid')
                $(".holy_buttons").hide().show()
                return false;
            }
            if (holiday_status_id == "") {
                 $( "#t_id option:selected" ).addClass('is-invalid')
                 $(".holy_buttons").hide().show()
                return false;
            }
            ajax.jsonRpc("/timeoff/requests/submit", 'call', {
                'name':name, 'request_date_from': request_date_from, 'request_date_to': request_date_to,
                'duration': duration, 'holiday_status_id': holiday_status_id, 'unit_hour': unit_hour,
                'period':period, hour_from, hour_to, 'hour_from': hour_from, 'attach': attachment,
                'hour_to': hour_to}).then(function (vals)
            {
                $(".modal").modal('hide');
                $(vals).appendTo('body');
                $(vals).modal('show');
                return false;
            });
        });
        $(".edit_holiday").click(function() {
            var leave_id = $(this).prev('input').val();
            ajax.jsonRpc("/holidays/edit", 'call', {'leave_id':leave_id}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
                test.find('.period_unit').hide();
                //test.find('.from_to_hours').hide();
                test.find('.div_unit_half').hide();
                test.find('.div_custom_hour').hide();
            });
        });
         $(".edit_leave").click(function() {
            var leave_id = $(this).prev('input').val();
            ajax.jsonRpc("/leave/edit", 'call', {'leave_id':leave_id}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
                test.find('.period_unit').hide();
                //test.find('.from_to_hours').hide();
                test.find('.div_unit_half').hide();
                test.find('.div_custom_hour').hide();
            });
        });
        $(document).on('change', "select[name='et_id']", function() {
            ajax.jsonRpc("/timeoff/request/request_unit", 'call', {'timeoff_type': $(this).val()}).then(function (vals)
            {
                show_timeoff_fields(vals);
            });
        });

        $(document).on("click", "#timeoff_edit_submit", function(e) {
            var $form = $(this).closest('form');
            var leave_id = $(this).parents('.timeoff_req_form').find('#leave_id').val();
            var name = $(this).parents('.timeoff_req_form').find('#name').val();
            var request_date_from = $(this).parents('.timeoff_req_form').find('#request_date_from').val();
            var request_date_to = $(this).parents('.timeoff_req_form').find('#request_date_to').val();
            var duration = $(this).parents('.timeoff_req_form').find('#number_of_days').val();
            var unit_hour = $(this).parents('.timeoff_req_form').find('#o_request_unit_hours').val();
            var period = $(this).parents('.timeoff_req_form').find('#rd_id').val();
            var holiday_status_id = $('#et_id').find(":selected").val();
            var hour_from = $(this).parents('form').find('#selecionado_hf').text();
            var hour_to = $(this).parents('form').find('#selecionado_ht').text();
            //var attachment = $('#req_attach').val();
            var msg = '';
            if (name == "") {
                $form.find('textarea[name="name"]').addClass('is-invalid')
                return false;
            }
            if (request_date_from == "") {
                $form.find('input[name="request_date_from"]').addClass('is-invalid')
                return false;
            }
            if (holiday_status_id == "") {
                $( "#et_id option:selected" ).addClass('is-invalid')
                return false;
            }
            if (!name){
                name = ''
            }
            ajax.jsonRpc("/timeoff/edit/submit", 'call', {
                'leave_id':leave_id, 'name':name, 'request_date_from': request_date_from,
                'request_date_to': request_date_to, 'duration': duration, 'holiday_status_id': holiday_status_id,
                'period':period, 'hour_from':hour_from, 'unit_hour': unit_hour,
                'hour_to':hour_to}).then(function (vals)
            {
                $(".modal").modal('hide');
                $(vals).appendTo('body');
                $(vals).modal('show');
            });
        });
        $(".upload_leave_btn").click(function() {
            var leave_id = $(this).prev('input').val();
            ajax.jsonRpc("/employee/holidays/upload", 'call', {'leave_id':leave_id}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
            });
        });
    });
});
