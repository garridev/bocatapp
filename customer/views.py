from django.shortcuts import render_to_response, get_object_or_404
from customer.services import OrderService
from django.template import RequestContext
from django.http.response import HttpResponseRedirect
from customer.models import Order, OrderLine
from customer.forms.forms import OrderLineDoneForm

# Create your views here.

# This method is for testing the funcionality


def all_orders(request):
    try:
        orders = OrderService.find_all_orders()
        return render_to_response('orders.html', {'orders': orders}, context_instance=RequestContext(request))
    except Order.DoesNotExist:
        return render_to_response('error.html', context_instance=RequestContext(request))


def order_line_by_order(request, order_id):
    try:
        orders_line = OrderService.find_order_line_by_order(order_id)
        return render_to_response('ordersLine.html', {'lines': orders_line}, context_instance=RequestContext(request))
    except OrderLine.DoesNotExist:
        return render_to_response('error.html', context_instance=RequestContext(request))


def order_line_done_form(request, id1):
    order_line = get_object_or_404(OrderLine, pk=id1)
    if request.method == 'POST':
        form = OrderLineDoneForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/customer/ordersLine/" + str(order_line.order_id))
    else:
        form = OrderLineDoneForm(instance=order_line)
    return render_to_response('/customer/ordersLine/' + str(order_line.order_id), {'form': form},
                              context_instance=RequestContext(request))


def do_order_line(request, id1):
    order_line = get_object_or_404(OrderLine, pk=id1)
    if request.method == 'POST':
        order_line.status = True
        order_line.save()
        return HttpResponseRedirect("/customer/ordersLine/" + str(order_line.order_id))
    else:
        return render_to_response('/customer/orders')
