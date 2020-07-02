(function ($) {
    const YEARLY = 0
    const MONTHLY = 1
    const WEEKLY = 2
    const DAILY = 3

    const BY_DATE = 1
    const BY_DAY = 2


    //custom function remove this form here
    //this is a replacement for compatbility with all browser
    function includes(array, value) {
        // console.log(array, value, array.indexOf(value) >= 0)
        return array.indexOf(value) >= 0
    }

    // using var, I prefer keep old browser compatibility
    var freq_id, year_month_mode_id, interval_id, byweekday_id, bymonthday_id, freq_type_name,
        utc_until_id, count_id, advace_options_id, bysetpost_id
    $('#rule-formset').on('formAdded', function (e) {
        console.log(e.target)
        const prefix = $(e.target).data('formset__formPrefix')

        /* hide element with value empty with class must-hide*/
        $('.must-hide').each(function (i, element) {
            var elementSelector = $('#' + element.id + '')
            console.log(elementSelector.val())
            if (!elementSelector.val().length > 0) {
                elementSelector.hide().next('.select2-container').hide()
                $('label[for="' + element.id + '"]').hide()
            }
        })

        /* check if freq has a value and disable all optgroup unnecessary
        * add + 1 to freq_selected because optgroup label with 0 not showing
        * */
        var freq_selected = $('#id_' + prefix + '-freq').val()
        var intervalField = $('#id_' + prefix + '-interval')
        var intervalSelected = intervalField.val()
        if (freq_selected) {
            intervalField.find('optgroup').not('[label="' + (parseInt(freq_selected) + 1) + '"]').prop('disabled', true)
            intervalField.find('optgroup[label="' + (parseInt(freq_selected) + 1) + '"]').find('option').eq(parseInt(intervalSelected) - 1).prop('selected', true)
        } else {
            $('#id_' + prefix + '-interval optgroup').prop('disabled', true)
        }


        /* advance option check*/
        $('.is_advance-option').each(function () {
            if ($(this).val() !== "") {
                $('#id' + prefix + '-advance_options').prop('checked', true)
                return false
            }
        })

    }).on('change', function (event) {
        let element = event.target;
        console.log($(element).parents('div[data-formset-form]').data('formset__formPrefix'))
        const prefix = $(element).parents('div[data-formset-form]').data('formset__formPrefix')
        let elementAttr = element.id
        console.log(element.name)
        console.log("empezando", elementAttr)

        if ($(element).is('input[type="radio"]')) {
            elementAttr = element.name
        }
        if (!includes(['id_' + prefix + '-freq', 'id_' + prefix + '-year_month_mode', 'id_' + prefix + '-byweekday',
            'id_' + prefix + '-advance_options', prefix + '-freq_type'], elementAttr)) {
            console.log("detener")
            return null
        }

        //get field for current form
        freq_id = 'id_' + prefix + '-freq'
        year_month_mode_id = 'id_' + prefix + '-year_month_mode'
        interval_id = 'id_' + prefix + '-interval'
        byweekday_id = 'id_' + prefix + '-byweekday'
        bymonthday_id = 'id_' + prefix + '-bymonthday'
        freq_type_name = prefix + '-freq_type'
        utc_until_id = 'id_' + prefix + '-utc_until'
        count_id = 'id_' + prefix + '-count'
        advace_options_id = 'id_' + prefix + '-advance_options'
        bysetpost_id = 'id_' + prefix + '-bysetpos'

        /*get target field to call function with it's name
        *  slicing from  "id_".length + prefix.length + "-".length
        * but input radio haven't id_ prefix
        */
        var targetField = elementAttr.slice(4 + prefix.length)

        if (elementAttr === freq_type_name) {
            targetField = elementAttr.slice(prefix.length + 1)
        }

        console.log(elementAttr, targetField)
        HandleEventFieldFormset[targetField + "FieldChange"]()
    })

    var HandleEventFieldFormset = {

        freqFieldChange: function () {
            console.log('freq changing')
            //YEARLY or MONTHLY freq
            let freq = parseInt($('#' + freq_id).val())
            console.log('frequency', freq, typeof freq)
            if (freq === YEARLY || freq === MONTHLY) {
                $('#' + year_month_mode_id).trigger('change').show()
                $('label[for="' + year_month_mode_id + '"]').show()
            } else {
                $('#' + year_month_mode_id).val(null).trigger('change').hide()
                $('label[for="' + year_month_mode_id + '"]').hide()
            }

            if (freq === WEEKLY) {
                $('#' + byweekday_id).val(null).next('.select2-container').show()
                $('label[for="' + byweekday_id + '"]').show()
                $('#' + byweekday_id + ' optgroup[label="nth-weekday"]').prop('disabled', true)
            }

            //add + 1 to freq because optgroup label with 0 not showing
            var intervalField = $('#' + interval_id)
            intervalField.val(null).trigger('change').find('optgroup').prop('disabled', true)
            intervalField.find('optgroup[label="' + (freq + 1) + '"]').prop("disabled", false).find('option').eq(0).prop('selected', true).trigger('change')
            console.log(intervalField.next('.select2-container'))

        },

        year_month_modeFieldChange: function () {
            let year_month_mode = parseInt($('#' + year_month_mode_id).val())
            if (year_month_mode === BY_DATE) {
                $('#' + bymonthday_id).next('.select2-container').show()
                $('label[for="' + bymonthday_id + '" ]').show()
                $('#' + byweekday_id).val(null).trigger('change').next('.select2-container').hide()
                $('label[for="' + byweekday_id + '"]').hide()
            } else if (year_month_mode === BY_DAY) {
                $('#' + byweekday_id).next('.select2-container').show()
                $('label[for="' + byweekday_id + '"]').show()
                $('#' + byweekday_id + ' optgroup[label="nth-weekday"]').prop('disabled', false)
                $('#' + bymonthday_id).val(null).trigger('change').next('.select2-container').hide()
                $('label[for="' + bymonthday_id + '" ]').hide()
            } else {
                $('#' + bymonthday_id).val(null).trigger('change').next('.select2-container').hide()
                $('label[for="' + bymonthday_id + '" ]').hide()
                $('#' + byweekday_id).val(null).trigger('change').next('.select2-container').hide()
                $('label[for="' + byweekday_id + '"]').hide()
            }
        },

        byweekdayFieldChange: function () {
            if (parseInt($('#' + freq_id).val()) === WEEKLY) {
                $('#' + byweekday_id + ' optgroup[label="nth-weekday"]').prop('disabled', true)
                return null
            }
            var optgroupLabel = $('#' + byweekday_id).find("option:selected").parent().prop('label')
            if (optgroupLabel) {
                $('#' + byweekday_id + ' optgroup').not('[label="' + optgroupLabel + '"]').prop('disabled', true)
            } else {
                $('#' + byweekday_id + ' optgroup').prop('disabled', false)
            }
        },

        advance_optionsFieldChange: function () {
            if ($('#' + advace_options_id).is(":checked")) {
                $('#' + bysetpost_id).show()
                $('label[for="' + bysetpost_id + '"]').show()
            } else {
                $('#' + bysetpost_id).hide().val('')
                $('label[for="' + bysetpost_id + '"]').hide()
            }
        },

        freq_typeFieldChange: function () {
            let freq_type = $('input[type="radio"][name="' + freq_type_name + '"]:checked').val()
            if (freq_type === 'until') {
                $('#' + utc_until_id).show()
                $('label[for="' + utc_until_id + '"]').show()
                $('#' + count_id).hide().val('')
                $('label[for="' + count_id + '"]').hide()
            } else if (freq_type === 'count') {
                $('#' + count_id).show()
                $('label[for="' + count_id + '"]').show()
                $('#' + utc_until_id).hide().val('')
                $('label[for="' + utc_until_id + '"]').hide()
            } else {
                $('#' + count_id).hide().val('')
                $('label[for="' + count_id + '"]').hide()
                $('#' + utc_until_id).hide().val('')
                $('label[for="' + utc_until_id + '"]').hide()
            }
        }
    }
})(window.jQuery)