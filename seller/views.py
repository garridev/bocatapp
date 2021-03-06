# -*- coding: utf-8 -*-
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import edit
from datetime import datetime, timedelta
import itertools
from bocatapp.views import home

from seller.forms.packsForms import PackForm
from seller.models import Product, Local, Category, Pack, ProductLine, LocalCategory
from customer.models import Order, OrderLine
from django.shortcuts import get_list_or_404, render_to_response, render, redirect, get_object_or_404

from forms.forms import LocalForm, CategoryForm, ProductForm

from forms.forms import LocalForm
from bocatapp.decorators import permission_required
from customer.models import Order
from customer.services import CommentService
from django.utils.translation import ugettext_lazy as _

# Create your views here.

# Lista el menu de productos de un local
def menu_list(request, pk):
    local = get_list_or_404(Local, id=pk)[0]
    categories = {c: c.product_set.all() for c in getLocalCategories(pk)}
    return render(request, 'menu.html',
                  {'categories': categories, 'local': local})


def getLocalCategories(pk):
    return Category.objects.filter(local=pk)


# Lista las categorias de un local
def category_list(request, pk):
    categories = getLocalCategories(pk)
    return render(request, 'category_list.html',
                  {'categories': categories, 'local_pk': pk})


def product_list_category(request, pk):
    productos = Product.objects.filter(category=pk)
    category = Category.objects.get(pk=pk)
    local = Local.objects.get(pk=category.local.pk)
    categories = {category: productos}
    return render(request, 'menu.html',
                  {'categories': categories, 'local': local})


# Vista para la creacion de una nueva categoria
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def category_new(request, pk):
    local = Local.objects.get(pk=pk)

    if local.seller.pk == request.user.pk:
        if request.method == "POST":
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.local = local
                category.save()
                messages.success(request, _('Category created correctly'))
                return redirect('category_list', pk=local.pk)
        else:
            form = CategoryForm()

        return render(request, 'category_new.html', {'form': form, 'local': local})
    else:
        messages.warning(request, unicode(_('The category has not been created because it does not belong to you.')))
        return redirect('/')


# Editar una categoria
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def category_edit(request, pk):
    category = Category.objects.get(pk=pk)
    local = category.local

    if local.seller.pk == request.user.pk:
        if request.method == "POST":
            form = CategoryForm(request.POST, instance=category)
            # aqui se comprueba que el vendedor es el que esta logueado
            if form.is_valid() and category.local.seller == request.user:
                category = form.save(commit=False)
                category.save()
                messages.success(request, unicode(_('Category updated correctly')))
                return redirect('category_list', pk=category.local.pk)
        else:
            form = CategoryForm(instance=category)

        return render(request, 'category_edit.html', {'category_id':category.pk, 'form': form, 'local': local})
    else:
        messages.warning(request, unicode(_('The category has not been edited because it does not belong to you.')))
        return redirect('/')

@permission_required('bocatapp.seller', message=_('You are not a seller'))
def category_delete(request, pk):
    category = Category.objects.get(pk=pk)
    local = category.local

    if local.seller.pk == request.user.pk:
        category.delete()
        messages.success(request, unicode(_('Category successfully deleted. ')))
        return redirect('category_list', pk=local.pk)
    else:
        messages.warning(request, unicode(_('The category has not been deleted because it does not belong to you.')))
        return redirect('/')


# Vista para la creacion de un nuevo producto
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def product_new(request, pk):
    local = get_object_or_404(Local, pk=pk)

    if local.seller.pk == request.user.pk:
        if request.method == "POST":
            form = ProductForm(request.POST, pk=pk)
            if form.is_valid() and local.seller == request.user:
                product = form.createProduct()
                product.local = local
                product.save()
                return redirect('menu_list', pk=product.local.id)
        else:
            form = ProductForm(pk=pk)

        return render(request, 'product_edit.html', {'form': form,'pk':pk})
    else:
        messages.warning(request, unicode(_('You can not create a product in this local because it does not belong to you.')))
        return redirect("/")


# Listado de locales dado un seller
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def get_my_locals(request):
    locals = Local.objects.filter(seller=request.user.pk)
    ratings = []
    for local in locals:
        ratings.append(CommentService.get_stars(local.pk))

    ratings.reverse()

    return render(request, 'local_list.html',
                  {'locals': locals, 'ratings': ratings})


# Vista para el lisstado de locales
def local_list(request):
    locals = Local.objects.all()
    if request.GET.get('list_by') == 0:
        locals = Local.objects.all().order_by("avg_rating")
    if request.GET.get("list_by") == 1:
        locals = Local.objects.all().order_by("-avg_rating")
    return render(request, 'local_list.html', {'locals': locals})


# Vista para las orders de un local
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def local_orders(request, pk):
    if request.user.local_set.filter(pk=pk):
        local = get_object_or_404(Local, pk=pk)

        # Pending orders
        orders_not_do = local.order_set.all().filter(status=False, cancelled=False)
        orders_pending = {o: o.orderline_set.all() for o in orders_not_do}
        # Done orders
        orders_do = local.order_set.all().filter(status=True, cancelled=False)
        orders_done = {o: o.orderline_set.all() for o in orders_do}
        # Cancel orders
        orders_cancel = local.order_set.all().filter(status=False, cancelled=True)
        orders_cancelled = {o: o.orderline_set.all() for o in orders_cancel}

        return render(request, 'orders.html', {'orders_pending': orders_pending, 'orders_done': orders_done, 'orders_cancelled': orders_cancelled})
    else:
        return render(request, '../templates/forbidden.html')

@permission_required('bocatapp.seller', message=_('You are not a seller'))
def do_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.user.local_set.filter(pk=order.local_id):
        order.status = True
        order.save()
        return redirect('local_orders', pk=order.local_id)
    else:
        return render(request, '../templates/forbidden.html')

# Vista para la creacion de un nuevo local
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def local_new(request):
    if request.method == "POST":
        form = LocalForm(request.POST)
        if form.is_valid():
            local = form.save(commit=False)
            local.seller = request.user
            local.isActive = True
            local.save()
            return redirect('seller.views.get_my_locals')
    else:
        form = LocalForm()

    return render(request, 'local_edit.html', {'form': form})


# Vista para los detalles de un local
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def local_detail(request, pk):
    local = get_object_or_404(Local, pk=pk)

    if local.seller.pk == request.user.pk:
        category_form = CategoryForm()
        return render(request, 'local_detail.html', {'local': local, 'form': category_form})
    else:
        return redirect("/")


# Vista para los detalles de un local
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def local_charts(request, pk):
    local = get_object_or_404(Local, pk=pk)

    if local.seller.pk == request.user.pk:
        orders = Order.objects.filter(local=pk)
        # General
        done_orders = sum([1 for order in orders if order.status is True])
        pending_orders = len(orders) - done_orders
        # Last week
        label_dates = [(datetime.now() - timedelta(days=counter)).strftime('%d/%m') for counter in range(7)][::-1]
        orders = Order.objects.filter(local=pk, moment__gte=datetime.now() - timedelta(days=7))
        grouped = itertools.groupby(orders, lambda record: record.moment.strftime("%d/%m"))
        orders_by_day = {day: len(list(jobs_this_day)) for day, jobs_this_day in grouped}
        # orders_by_day_result = [(date, orders_by_day.get(date, 0)) for date in label_dates]
        orders_by_day_result = [orders_by_day.get(date, 0) for date in label_dates]

        return render(request, 'local_charts.html',
                      {'local': local, 'orders': orders,
                       'pending_orders': pending_orders,
                       'done_orders': done_orders,
                       'label_dates': label_dates,
                       'orders_by_day': orders_by_day_result})
    else:
        return redirect("/")


# Vista para la creacion de un local
@permission_required('bocatapp.seller', message=_('You are not a seller'))
def local_edit(request, pk):
    if request.user.local_set.filter(pk=pk):
        local = get_object_or_404(Local, pk=pk)
        if request.method == "POST":
            form = LocalForm(request.POST, instance=local)
            if form.is_valid():
                local = form.save(commit=False)
                local.seller = request.user
                local.isActive = True
                local.save()
                return redirect('seller.views.get_my_locals')
        else:
            form = LocalForm(instance=local)
            return render(request, 'local_edit.html', {'form': form,'pk':pk})
    else:
        return render(request, '../templates/forbidden.html')


def search(request):
    ### COMPROBAR PRIMERO LA COCINA Y ENTONCES ORDENAR POR ESTRELLAS SI AUX
    input_search = request.GET.get("postcode")

    if input_search != "":
        #print (LocalCategory.objects.filter(locals__id=68))
        supercats = find_different_cats()
        if input_search and input_search.isdigit():
            locals = Local.objects.all().filter(postalCode=input_search)
            aux = request.GET.get('list_by')
            cocina = request.GET.get("cuisine")
            if cocina:
                locals = sort_locals(cocina)
            if aux == u'1':
                locals = locals.order_by("avg_rating")
            elif aux == u'0':
                locals = locals.order_by("-avg_rating")
        elif not isinstance(input_search, int):
            locals = []
        else:
            locals = Local.objects.all()

        return render(request, 'cp_search.html', {'locals': locals, 'supercats': supercats})

    else:
        messages.warning(request, unicode(_('You must enter a zip code')))
        return redirect(home.home)


def find_different_cats():
    aux = LocalCategory.objects.all()
    res = []
    checked = []

    for c in aux:
        if not checked.__contains__(c.name):
            checked.append(c.name)
            res.append(c)

    return res

def sort_locals(cocina):
    aux = LocalCategory.objects.get(name=cocina)
    return aux.locals.get_queryset()


def search2(request, pk):
    code = get_object_or_404(Local, pk=pk).postalCode
    locals = Local.objects.all().filter(postalCode=code)
    return render(request, 'cp_search.html', {'locals': locals})


# Packs--------------------------------------------------------------------------
def packs_list(request):
    packs = get_list_or_404(Pack)
    return render(request, 'pack/list.html',
                  {'packs': packs})


def local_packs(request, pk):
    packs = Local.objects.get(id=pk).pack_set.all()
    local = Local.objects.get(id=pk)
    return render(request, 'pack/list.html',
                  {'packs': packs, 'local': local})


def pack_details(request, pk):
    pack = get_object_or_404(Pack, id=pk)
    return render(request, 'pack/details.html',
                  {'pack': pack})


class EditPack(edit.View):
    # @permission_required('bocatapp.seller', message='You are not a seller')
    def get(self, request, local_pk):
        pack_form = PackForm()
        local_products = get_object_or_404(Local, id=local_pk).product_set.all()
        context = {
            'pack_form': pack_form,
            'local_products': local_products,
            'local_pk': local_pk
        }
        return render(request, 'pack/edit.html', context)

        # @permission_required('bocatapp.seller', message='You are not a seller')

    @transaction.atomic
    def post(self, request, local_pk):
        if request.user.is_authenticated():
            pack_form = PackForm(request.POST)
            local_products = get_object_or_404(Local, id=local_pk).product_set.all()
            if pack_form.is_valid():
                pack = pack_form.create(local_pk)
                pack.save()

                for product in local_products:
                    quantity = request.POST.get(str(product.id))
                    if quantity and int(quantity) > 0:
                        product_line = ProductLine(quantity=int(quantity), product=product, pack=pack)
                        product_line.save()
                return redirect('local_packs', local_pk=local_pk)
            else:
                message = ""
                for field, errors in pack_form.errors.items():
                    for error in errors:
                        message += error

                return render(request, 'pack/edit.html', {
                    'local_pk': local_pk, 'pack_form': pack_form, 'local_products': local_products, 'message': message})

        else:
            return render(request, '../templates/forbidden.html')
