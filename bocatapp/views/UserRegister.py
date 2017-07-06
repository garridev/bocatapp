from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.models import Permission
from django.views.generic import FormView
from bocatapp.forms import UserRegistrationForm
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


class RegistrationCustomerView(FormView):
    def get(self, request):
        if not request.user.is_authenticated():
            form = UserRegistrationForm()
            _next = request.GET.get('next', '')
            context = {'type': 'Registro',
                       'form': form,
                       'next': _next
                       }
            return render(request, '../templates/forms/register_form.html', context)
        else:
            return render(request, '../templates/forbidden.html')

    @transaction.atomic
    def post(self, request):
        if not request.user.is_authenticated():
            form = UserRegistrationForm(request.POST or None)
            _next = request.GET.get('next', '/')
            if form.is_valid():
                user = form.create_user()
                password = form.cleaned_data.get('password')
                user.set_password(password)
                save_customer(user)
                return HttpResponseRedirect(_next)
            else:
                message = ""
                for field, errors in form.errors.items():
                    for error in errors:
                        message += error
                context = {
                    'type': _('Register'),
                    'form': form, 'message': message,
                    'next': _next
                }
                return render(request, '../templates/forms/register_form.html', context)
        else:
            return render(request, '../templates/forbidden.html')


class RegistrationSellerView(FormView):
    def get(self, request):
        if not request.user.is_authenticated():
            form = UserRegistrationForm()
            context = {'type': _('Seller register'),
                       'form': form,
                       }
            return render(request, '../templates/forms/register_form.html', context)
        else:
            return render(request, '../templates/forbidden.html')

    @transaction.atomic
    def post(self, request):
        if not request.user.is_authenticated():
            form = UserRegistrationForm(request.POST or None)
            if form.is_valid():
                user = form.create_user()
                password = form.cleaned_data.get('password')
                user.set_password(password)
                save_seller(user)
                return HttpResponseRedirect("/")
            else:
                message = ""
                for field, errors in form.errors.items():
                    for error in errors:
                        message += error
                context = {'type':  _('Seller register'),
                           'form': form, 'message': message
                           }
                return render(request, '../templates/forms/register_form.html', context)
        else:
            return render(request, '../templates/forbidden.html')


def save_customer(user):
    user.save()
    user.user_permissions.add(Permission.objects.get(codename="customer"))


def save_seller(user):
    user.save()
    user.user_permissions.add(Permission.objects.get(codename="seller"))
