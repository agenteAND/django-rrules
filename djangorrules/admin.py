from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.utils import timezone
from .models import Recurrence, Rule, RDate
from .forms import RuleForm


class RuleAdmin(admin.TabularInline):
    model = Rule
    extra = 0
    form = RuleForm


class RDateAdmin(admin.TabularInline):
    model = RDate
    extra = 0


class RecurrenceAdmin(admin.ModelAdmin):
    model = Recurrence
    inlines = [RuleAdmin, RDateAdmin]

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            tz_form = RuleForm(request.POST)
            if tz_form.is_valid():
                timezone.activate(tz_form.cleaned_data['timezone'])
        else:
            timezone.deactivate()
        return super().add_view(request, form_url, extra_context)

    # Override change view so we can peek at the timezone they've entered and
    # set the current time zone accordingly before the form is processed
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'POST':
            tz_form = RuleForm(request.POST)
            if tz_form.is_valid():
                timezone.activate(tz_form.cleaned_data['timezone'])
        else:
            obj = self.get_object(request, unquote(object_id))
            timezone.activate(obj.timezone)
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(Recurrence, RecurrenceAdmin)
