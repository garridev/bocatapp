from django.conf.urls import include, url

urlpatterns = [
    # Users URLs
    # url(r'^register$', RegistrationView.as_view(), name='guest_register')
    url(r'^orders/$', 'customer.views.all_orders'),
    url(r'^ordersLine/(?P<order_id>[0-9]+)/$', 'customer.views.order_line_by_order'),
    url(r'^do_order_line/(?P<id1>[0-9]+)/$', 'customer.views.do_order_line'),
    url(r'^comment/(?P<pk>[0-9]+)/$', 'customer.views.comment_new', name="comment_new"),
    url(r'^comments/(?P<pk>[0-9]+)/$', 'customer.views.comment_list', name="comment_list"),
    url(r'^report/(?P<pk>[0-9]+)/$', 'customer.views.report_new', name="report_new"),
    url(r'^reports/(?P<pk>[0-9]+)/$', 'customer.views.report_list', name="report_list"),
    url(r'^report/accept/(?P<pk>[0-9]+)/$', 'customer.views.report_accept', name="report_accept"),
    url(r'^report/decline/(?P<pk>[0-9]+)/$', 'customer.views.report_decline', name="report_decline"),
    url(r'^orders/(?P<pk>[0-9]+)/$', 'customer.views.orders_by_customer', name="orders_by_customer"),
    url(r'^checkout/$', 'customer.views.checkout', name="checkout"),
    url(r'^checkout/save/$', 'customer.views.do_checkout', name="do_checkout"),
    url(r'^dashboard/$', 'customer.views.customer_dashboard', name='dashboard'),
    url(r'^search/(?P<local_id>[0-9]+)/$', 'customer.views.search_product', name="search_product")
]
