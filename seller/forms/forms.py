# -*- coding: utf-8 -*-
from django import forms
from ..models import Local, Category, Product
from django.utils.translation import ugettext_lazy as _

class LocalForm(forms.ModelForm):

    phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$',
                             error_message=(
                                 _("Must have 999999999 format")))

    def __init__(self, *args, **kwargs):
        super(LocalForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = unicode(_('Name'))
        self.fields['description'].label = unicode(_('Description'))
        self.fields['address'].label = unicode(_('Address'))
        self.fields['phone'].label = unicode(_('Phone'))
        self.fields['postalCode'].label = unicode(_('Postal code'))
        self.fields['photo'].label = unicode(_('Photo'))

    class Meta:
        model = Local
        fields = ('name', 'description', 'address', 'phone', 'postalCode', 'photo')


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = unicode(_('Name'))
        self.fields['description'].label = unicode(_('Description'))

    class Meta:
        model = Category
        fields = ('name', 'description')


class ProductForm(forms.ModelForm):
    nombre = forms.CharField()
    precio = forms.DecimalField()
    ingredientes = forms.CharField()
    categoria = forms.ModelChoiceField(queryset=Category.objects.none(), required=True)


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        if pk:
            self.local = Local.objects.get(pk=pk)
            self.fields['categoria'].queryset = self.local.category_set.all()

    def createProduct(self):
        result = Product(name=self.cleaned_data['nombre'],
                         price=self.cleaned_data['precio'],
                         ingredients=self.cleaned_data['ingredientes'],
                         category=self.cleaned_data['categoria'],
                         local=self.local)
        result.save()
        return result



    class Meta:
        model = Product
        fields = ('nombre', 'precio', 'categoria', 'ingredientes')
