from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet, modelformset_factory
from django.utils.translation import gettext_lazy as _
# from crispy_forms.helper import FormHelper
from django_select2.forms import Select2MultipleWidget
from .models import Recurrence, Rule


class HTML5DateInput(forms.DateInput):
    input_type = 'date'


class HTML5DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    format = 'yyyy-MM-ddThh:mm'


class RuleForm(forms.ModelForm):
    """
    grouping from index 1 because optgroup not showing
    index 0 use only in INTERVAL CHOICES
    """
    (__YEARLY, __MONTHLY, __WEEKLY, __DAILY) = range(1, 5)
    INTERVAL_CHOICES = [
        (None, "Select a Interval"),
        # group yearly
        (__YEARLY, (
            (1, _('Every year')),
            (2, _('Every other year')),
            (3, _('Every 3rd year')),
            (4, _('Every 4th year')),
            (5, _('Every 5th year')),
            (6, _('Every 6th year')),
            (7, _('Every 7th year')),
            (8, _('Every 8th year')),
            (9, _('Every 9th year')),
            (10, _('Every 10th year'))
        )),
        # group monthly
        (__MONTHLY, (
            (1, _('Every month')),
            (2, _('Every other month')),
            (3, _('Every 3rd month')),
            (4, _('Every 4th month')),
            (5, _('Every 5th month')),
            (6, _('Every 6th month')),
            (7, _('Every 7th month')),
            (8, _('Every 8th month')),
            (9, _('Every 9th month')),
            (10, _('Every 10th month')),
            (11, _('Every 11th month')),
            (12, _('Every 12th month')),
            (18, _('Every 18th month')),
            (24, _('Every 24th month')),
            (36, _('Every 36th month')),
            (48, _('Every 48th month'))
        )),
        # group weekly
        (__WEEKLY, (
            (1, _('Every week')),
            (2, _('Every other week')),
            (3, _('Every 3rd week')),
            (4, _('Every 4th week')),
            (5, _('Every 5th week')),
            (6, _('Every 6th week')),
            (7, _('Every 7th week')),
            (8, _('Every 8th week')),
            (9, _('Every 9th week')),
            (10, _('Every 10th week')),
            (11, _('Every 11th week')),
            (12, _('Every 12th week')),
            (13, _('Every 13th week')),
            (14, _('Every 14th week')),
            (15, _('Every 15th week')),
            (16, _('Every 16th week')),
            (17, _('Every 17th week')),
            (18, _('Every 18th week')),
            (19, _('Every 19th week')),
            (20, _('Every 20th week')),
            (21, _('Every 21st week')),
            (22, _('Every 22nd week')),
            (23, _('Every 23rd week')),
            (24, _('Every 24th week')),
            (25, _('Every 25th week')),
            (26, _('Every 26th week'))
        )),

        # group daily
        (__DAILY, (
            (1, _('Every day')),
            (2, _('Every other day')),
            (3, _('Every 3rd day')),
            (4, _('Every 4th day')),
            (5, _('Every 5th day')),
            (6, _('Every 6th day')),
            (7, _('Every 7th day')),
            (8, _('Every 8th day')),
            (9, _('Every 9th day')),
            (10, _('Every 10th day')),
            (11, _('Every 11th day')),
            (12, _('Every 12th day')),
            (13, _('Every 13th day')),
            (14, _('Every 14th day')),
            (15, _('Every 15th day')),
            (16, _('Every 16th day')),
            (17, _('Every 17th day')),
            (18, _('Every 18th day')),
            (19, _('Every 19th day')),
            (20, _('Every 20th day')),
            (21, _('Every 21st day')),
            (22, _('Every 22nd day')),
            (23, _('Every 23rd day')),
            (24, _('Every 24th day')),
            (25, _('Every 25th day')),
            (26, _('Every 26th day')),
            (27, _('Every 27th day')),
            (28, _('Every 28th day')),
            (29, _('Every 29th day')),
            (30, _('Every 30th day'))
        ))
    ]

    advance_options = forms.BooleanField(label=_('advance options'), required=False)
    utc_until = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=HTML5DateTimeInput(attrs={
            'class': 'must-hide'
        },
            format='%Y-%m-%dT%H:%M'
        ), required=False
    )
    interval = forms.TypedChoiceField(
        label=_('interval'), choices=INTERVAL_CHOICES, coerce=int, empty_value=None,
        widget=forms.Select(attrs={
            'class': 'optgroup-label-hidden',
        })
    )

    class Meta:
        model = Rule
        fields = ['recurrence', 'dtstart', 'freq', 'year_month_mode',
                  'interval', 'wkst', 'bymonth', 'bymonthday', 'byweekday', 'freq_type', 'count', 'utc_until',
                  'advance_options', 'bysetpos'
                  ]

        widgets = {
            'dtstart': HTML5DateInput,
            'year_month_mode': forms.Select(attrs={'class': 'must-hide'}),
            'bymonth': Select2MultipleWidget,
            'bymonthday': Select2MultipleWidget(attrs={'class': 'must-hide'}),
            'byweekday': Select2MultipleWidget(attrs={'class': 'must-hide'}),
            'naive_until_date': forms.HiddenInput,
            'naive_until_time': forms.HiddenInput,
            'freq_type': forms.RadioSelect,
            'count': forms.NumberInput(attrs={'class': 'must-hide'}),
            'bysetpos': Select2MultipleWidget(attrs={'class': 'must-hide is_advance-option'})
        }

    class Media:
        css = {
            'all': (
                '/static/djangorrules/css/main.css',
            ),
        }
        js = ('/static/djangorrules/js/apps.js',)


class BaseRuleFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            freq = form.cleaned_data.get('freq')
            mode = form.cleaned_data.get('year_month_mode', None)
            freq_type = form.cleaned_data.get('freq_type', None)
            if freq == Rule.YEARLY or freq == Rule.MONTHLY:
                if mode == RuleForm.BY_DATE:
                    self.required_field(['bymonthday'], form)
                elif mode == RuleForm.BY_DAY:
                    self.required_field(['byweekday'], form)
                else:
                    self.required_field(['year_month_mode'], form)
            elif freq == Rule.WEEKLY:
                self.required_field(['byweekday'], form)

            # if freq_type == Rule.OCCURRENCES:
            #     self.required_field(["count"], form)
            # elif freq_type == Rule.UNTIL:
            #     self.required_field(["utc_until"], form)

    @staticmethod
    def required_field(fields, form):
        for field in fields:
            if not form.cleaned_data.get(field, None):
                msj = ValidationError(
                    _('%(field)s is required '),
                    code='required',
                    params={'field': field}
                )
                form.add_error(field, msj)


RulseFormSet = modelformset_factory(Rule, form=RuleForm, extra=1, can_delete=True)
