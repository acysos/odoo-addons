# -*- coding: utf-8 -*-
# Copyright (c) 2010 Ángel Moya <angel.moya@domatix.com>
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from django.utils.encoding import smart_text


class FileExport():

    _sizes = []

    # fill a variable with blank spaces to fit the desired size
    def fill_with_char(
            self, var, desired_size, char=' ', char_position='right',
            out_char_sep=None):
        if not var:
            var = ''
        var = smart_text(var)
        if out_char_sep:
            var += out_char_sep
        else:
            if len(var) < desired_size:
                actual_size = len(var)
                for i in range(actual_size, desired_size):
                    if char_position == 'right':
                        var += char
                    else:
                        var = char + var
        return var

    def generate_txt(self, file_vars, out_char_sep=None):
        # default output
        output = ''
        # complete every field to fit exactly specification chars
        for size in self._sizes:
            field_name = size[0]
            field_size = size[1]
            # if field has no decimal part will be processed as text (extra
            # positions will be spaces)
            if len(size) == 2:
                string = self.fill_with_char(
                    file_vars[field_name], field_size, ' ', 'right',
                    out_char_sep)
            # if field has decimal part will be processed as number (zeroe
            # added instead of spaces)
            elif len(size) == 3:
                field_decimals = size[2]
                number = file_vars[field_name]
                if number == 0.0:
                    edi_number = ''
                else:
                    edi_number = str(int(number))
                    if field_decimals != 0:
                        # convert decimals to integer
    #                     if field_name in ['SUMBRUTO', 'TOTAL', 'SUMNETOS', 'IMPVTO1']:
    #                         dec_part = int(
    #                             round((number - int(number)), 2) * (
    #                                 10 ** field_decimals))
    #                     else:
    #                         dec_part = int(
    #                             (number - int(number)) * (10 ** field_decimals))
#                         dec_part = int(
#                             round((number - int(number)), 2) * (10 ** field_decimals))
                        dec_part = str(
                            round((number - int(number)), field_decimals))
                        dec_part = dec_part.replace('0.', '')
                        dec_part = dec_part.ljust(field_decimals, '0')
    
                        # insert decimal separator to string
                        # TODO use company
                        edi_number += ','
                        edi_number += str(dec_part)
                string = self.fill_with_char(
                    edi_number, field_size, ' ', 'right', out_char_sep)
            output += string
        output += '\r\n'
        return output
