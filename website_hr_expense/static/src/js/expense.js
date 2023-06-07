odoo.define('website_hr_expense.expense_request', function (require) {
	"use strict";
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');

    $(document).ready(function () {

        $(document).on("click", ".expense_req_btn", function(e) {
            ajax.jsonRpc("/expense/request", 'call', {}).then(function (vals)
            {
                $(vals).appendTo('body');
                $(vals).modal('show');
            });
        });
        $(document).on('change', "select[name='prod_id']", function() {
            $(this).closest('form').find('#selecionado_prod').text($(this).val()).change();
            var expense_node = $(this).closest('form').find('#expense_price')
            ajax.jsonRpc("/expenses/request/product_price", 'call', {'product_id': $(this).val()}).then(function (vals)
            {   
                var result = parseFloat(vals)
                expense_node.val(result).change();
            if(result != 0){
                expense_node.attr('readonly', 'true');
            }
            else{
                expense_node.prop('readonly', 0);
            }
            });
        });
        $(document).on('change', "expense_price", function() {
            if ($("expense_price").val() != 0){
                $("expense_price")
            }
        })
        $(document).on('change', "select[name='payer_id']", function() {
            $(this).closest('form').find('#selecionado_payer').text($(this).val()).change();
        });
        $(document).on("click", "#expense_req_submit", function(e) {
            var $form = $(this).closest('form');
            $(".expense_buttons").hide()
            var request_date = $form.find('input[name="req_date"]').val();
            var price_unit = $form.find('input[name="expense_price"]').val();
            var qty = $form.find('input[name="expense_qty"]').val();
            var msg = '';
            var product = $(this).parents('form').find('#selecionado_prod').text();
            var payer = $(this).parents('form').find('#selecionado_payer').text();
            var name = $form.find('textarea[name="name"]').val()
            if (name == "") {
                $form.find('textarea[name="name"]').addClass('is-invalid')
                $(".expense_buttons").hide().show()
                return false;
            }
            ajax.jsonRpc("/expense/requests/submit", 'call', {
                'name':name, 'request_date': request_date, 'price_unit': price_unit, 'qty': qty,
                'product':product, 'payer': payer}).then(function (vals)
            {
                $(".modal").modal('hide');
                $(vals).appendTo('body');
                $(vals).modal('show');
                return false;
            });
        });
        $(".edit_expense").click(function() {
            var expense_id = $(this).prev('input').val();
            ajax.jsonRpc("/expense/edit", 'call', {'expense_id':expense_id}).then(function (vals)
            {
                $(vals).appendTo('body');
                $(vals).modal('show');
            });
        });
        $(document).on("click", "#expense_edit_submit", function(e) {
            var $form = $(this).closest('form');
            var expense_id = $(this).parents('.expense_req_form').find('#expense_id').val();
            var name = $(this).parents('.expense_req_form').find('#name').val();
            var request_date = $(this).parents('.expense_req_form').find('#request_date').val();
            var unit_price = $(this).parents('.expense_req_form').find('#expense_price').val();
            var qty = $(this).parents('.expense_req_form').find('#expense_qty').val();
            var payer = $(this).parents('form').find('#selecionado_payer').text();
            var product = $(this).parents('form').find('#selecionado_prod').text();
            if (name == "") {
                $form.find('textarea[name="name"]').addClass('is-invalid')
                return false;
            }
            if (!name){
                name = ''
            }
            ajax.jsonRpc("/expense/edit/submit", 'call', {
                'expense_id':expense_id, 'name':name, 'request_date': request_date,
                'price_unit': unit_price, 'qty': qty,'payer':payer, 'product':product}).then(function (vals)
            {
                $(".modal").modal('hide');
                $(vals).appendTo('body');
                $(vals).modal('show');
            });
        });
    });
});
