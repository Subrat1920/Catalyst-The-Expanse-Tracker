from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
import datetime
from .models import UserIncome  # Import the Expense model if not already imported
from django.http import JsonResponse
import datetime
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)




@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if UserPreference exists for the current user
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        # Handle the case where UserPreference does not exist
        currency = None  # or set a default currency
    
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)



@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')


# def expense_category_summary(request):
#     todays_date = datetime.date.today()
#     six_months_ago = todays_date-datetime.timedelta(days=30*6)
#     expenses = expenses.objects.filter(owner=request.user,date__gte=six_months_ago, date__lte=todays_date)
#     finalrep = {}

#     def get_category(expense):
#         return expense.category
#     category_list = list(set(map(get_category, expenses)))

#     def get_expense_category_amount(category):
#         amount = 0
#         filtered_by_category = expenses.filter(category=category)

#         for item in filtered_by_category:
#             amount += item.amount
#         return amount

#     for x in expenses:
#         for y in category_list:
#             finalrep[y] = get_expense_category_amount(y)

#     return JsonResponse({'expense_category_data': finalrep}, safe=False)

from .models import UserIncome
import datetime

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    incomes = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(income):
        return income.source

    category_list = list(set(map(get_category, incomes)))

    def get_income_category_amount(category):
        amount = 0
        filtered_by_category = incomes.filter(source=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for y in category_list:
        finalrep[y] = get_income_category_amount(y)

    return JsonResponse({'income_category_data': finalrep}, safe=False)


def inc_stats(request):
    return render(request, 'income/inc_stats.html')
