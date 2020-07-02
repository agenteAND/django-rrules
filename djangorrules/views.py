from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.utils import timezone

from djangorrules.forms import RulseFormSet


def test_form(request):
    timezone.activate("America/La_Paz")
    if request.POST:
        formset = RulseFormSet(request.POST, prefix='rule-form')
        if formset.is_valid():
            print(formset.cleaned_data)
            instances = formset.save()
            return HttpResponseRedirect(reverse('create-rule'))
        else:
            print("errors", formset.errors)

    else:
        formset = RulseFormSet(prefix='rule-form')
    return render(request, "djangorrules/create-rule.html", {'formset': formset})
