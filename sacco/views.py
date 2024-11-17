from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from sacco.app_forms import CustomerForm, DepositForm
from sacco.models import Customer, Deposit


# Create your views here.
def test(request):
    #save a customer
    # c1 = Customer(first_name='Saida', last_name='Ali',
    #               email='saida@x.com', dob='2000-11-28', gender='Female', weight=62)
    # c1.save()
    #
    # c2 = Customer(first_name='Jake', last_name='Juma',
    #               email='juma@x.com', dob='1999-11-28', gender='Male', weight=62)
    # c2.save()
    customer_count = Customer.objects.count()
    # fetching one customer
    c1 = Customer.objects.get(id=1) # select * from customers where id=1
    print(c1)
    d1 = Deposit(amount=1000, status=True, customer=c1)
    d1.save()
    deposit_count = Deposit.objects.count()
    return HttpResponse(f"Ok, Done, We have {customer_count} customers and {deposit_count} deposits")

# http://localhost:8000/
# http://localhost:8000/test
# python manage.py runserver 8001

def customers(request):
    data = Customer.objects.all().order_by('id').values()# ORM select * from customers
    paginator = Paginator(data, 15)
    page = request.GET.get('page', 1)
    try:
      paginated_data = paginator.page(page)
    except  EmptyPage:
        paginated_data = paginator.page(1)
    return render(request, "customers.html", {"data": paginated_data})


def delete_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id) # select * from customers where id=7
    customer.delete() # delete from customers where id=7
    messages.info(request, f"Customer {customer.first_name} was deleted!!")
    return redirect('customers')


def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer {form.cleaned_data['first_name']} was added!")
            return redirect('customers')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {"form": form})


def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer {form.cleaned_data['first_name']} was updated!")
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_update_form.html', {"form": form})



def search_customer(request):
    search_term = request.GET.get('search')
    data = Customer.objects.filter( Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term) | Q(email__icontains=search_term)  )
    return render(request, "search.html", {"customers": data})


def deposit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            depo = Deposit(amount=amount, status=True, customer=customer)
            depo.save()
            messages.success(request, 'Your deposit has been successfully saved')
            return redirect('customers')
    else:
        form = DepositForm()
    return render(request, 'deposit_form.html', {"form": form, "customer": customer})


def customer_details(request,customer_id):
    customer = Customer.objects.get(id=customer_id)
    deposits = customer.deposits.all()
    total = Deposit.objects.filter(customer=customer).filter(status=True).aggregate(Sum('amount'))['amount__sum']
    return render(request, 'details.html', {'customer': customer, 'deposits': deposits, 'total': total})

# pip install Pillow