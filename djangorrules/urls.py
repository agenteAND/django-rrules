from django.urls import path
from .views import test_form

urlpatterns = [
    path('rule', test_form, name='create-rule')
]
