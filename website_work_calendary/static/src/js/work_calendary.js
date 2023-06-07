odoo.define('website_work_calendary.open_day', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    $(document).ready(function () {

        $(document).on("click", ".c_work_day", function(e) {
            e.preventDefault();
            var day = $(this).parents('.work_day_td').find('.work_date').text();
            ajax.jsonRpc("/calendario/dia", 'call', {'day': day}).then(function (vals)
            {
                $(vals).appendTo('body');
                var test = $(vals).modal('show');
            });
        });
});
});