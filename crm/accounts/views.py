from django.shortcuts import render, redirect
from django.http import  HttpResponse
from django.db import connection
from .forms import OrderForm
from .models import *
from .filters import OrderFilter
# Create your views here.
def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
def home(request):
    c = connection.cursor()
    try:
        c.execute('SELECT COUNT(id) as total_order FROM `accounts_order`')
        total_order = dictfetchall(c)
        c.execute('SELECT COUNT(id) as total_order_delivered FROM `accounts_order` WHERE status ="Delivered"')
        total_order_delivered = dictfetchall(c)
        c.execute('SELECT COUNT(id) as total_order_pending FROM `accounts_order` WHERE status ="Pending"')
        total_order_pending = dictfetchall(c)
        c.execute('SELECT c.id, c.name, COUNT(o.product_id) as total_order from accounts_order as o INNER JOIN accounts_customer as c ON o.customer_id = c.id GROUP BY o.customer_id')
        customer_order_details = dictfetchall(c)
        c.execute('SELECT o.id, p.name,o.date_created,o.status FROM accounts_product as p INNER JOIN accounts_order AS o ON o.product_id = p.id ORDER BY o.product_id DESC LIMIT 5')
        last_5_orders = dictfetchall(c)
        # print(total_order_delivered)
    finally:
        c.close()
    context = {
        'total_order': total_order[0]['total_order'],
        'total_order_delivered': total_order_delivered[0]['total_order_delivered'],
        'total_order_pending': total_order_pending[0]['total_order_pending'],
        'customer_order_details':customer_order_details,
        'last_5_orders': last_5_orders
    }
    return render(request,'accounts/dashboard.html',context=context)

def products(request):
    p = connection.cursor()
    p.execute('SELECT * FROM `accounts_product`')
    result = dictfetchall(p)
    return render(request,'accounts/products.html',{'products':result})

def customer(request,pk):
    c = connection.cursor()
    try:
        c.execute('SELECT * FROM `accounts_customer` WHERE id = %s',[pk])
        customer_details = dictfetchall(c)
        c.execute('SELECT COUNT(id) as total_order FROM `accounts_order` WHERE customer_id = %s',[pk])
        total_order = dictfetchall(c)
        c.execute('SELECT o.id, o.status, o.date_created, p.name,p.category FROM `accounts_order` AS o LEFT JOIN accounts_product AS p ON p.id = o.product_id WHERE o.customer_id = %s',[pk])
        product_details = dictfetchall(c)
    finally:
        c.close()
    # myfilter = OrderFilter(request.GET,queryset=product_details)
    # product_details = myfilter.qs
    context = {
            'customer_details' : customer_details[0],
            'total_order' : total_order[0],
            'product_details': product_details,
            # 'myfilter' : myfilter
        }
    return render(request,'accounts/customer.html',{'context':context})

def createOrder(request,pk):
    customer = Customer.objects.get(id=pk)
    form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('Printing post data', request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request,'accounts/order_from.html',context)

def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST,instance= order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request,'accounts/order_from.html',context)

def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        delete_order = Order.objects.get(id=pk)
        delete_order.delete()
        return redirect('/')
    context = {'item':order, 'pk':pk}
    return render(request,'accounts/delete.html',context)


def login(request):
    context = {}
    return render(request,'accounts/login.html',context)
def register(request):
    context = {}
    return render(request,'accounts/register.html',context)