from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Expense
import csv
import datetime
import xlwt


from django.db.models import Sum


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


import os
from django.http import HttpResponse
from django.template.loader import render_to_string

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from django.db.models import Sum
import tempfile


from io import BytesIO

from django.http import JsonResponse


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


    
@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        # If UserPreference does not exist, set a default currency
        currency = 'USD'  # You can change this to any default currency you prefer

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)






@login_required(login_url='/authentication/login')
def add_expense(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'values': {}  # Empty dictionary for initial form values
        }
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        # Validation
        if not amount:
            messages.error(request, 'Amount is required')
            return redirect('add-expense')  # Redirect to the same page
        if not description:
            messages.error(request, 'Description is required')
            return redirect('add-expense')  # Redirect to the same page
        if not category:
            messages.error(request, 'Category is required')
            return redirect('add-expense')  # Redirect to the same page

        # Creating Expense object
        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('add-expense')  # Redirect to the same page after successful submission


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')







def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)

    finalrep = {}
    for expense in expenses:
        if expense.category in finalrep:
            finalrep[expense.category] += expense.amount
        else:
            finalrep[expense.category] = expense.amount

    return JsonResponse({'expense_category_data': finalrep})



def stats_view(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        # Format the date as string in the desired format
        formatted_date = expense.date.strftime('%Y-%m-%d')
        writer.writerow([expense.amount, expense.description, expense.category, formatted_date])

    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="expenses.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(column)):
        ws.write(row_num, col_num, column[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount','description','category','date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response






def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename="expenses.pdf"'

    expenses = Expense.objects.filter(owner=request.user)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Create a temporary directory for ReportLab to write the PDF file
    temp_dir = tempfile.mkdtemp()

    # Construct the path to the temporary PDF file
    pdf_file_path = os.path.join(temp_dir, 'expenses.pdf')

    # Create PDF using ReportLab
    c = canvas.Canvas(pdf_file_path, pagesize=A4)

    # Draw company logo
    logo_path = "UPDATE WITH YOUR IMAGE"  # Update this with the path to your company logo
    logo_width, logo_height = 200, 100  # Width and height of the logo
    logo_x = (A4[0] - logo_width) / 2  # Calculate x-coordinate to center the logo horizontally
    logo_y = 700  # Set y-coordinate just above the company name
    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

    # Draw company name at the middle of the page
    c.setFont("Helvetica-Bold", 16)
    company_name = "Catalyst"
    company_name_width = c.stringWidth(company_name)
    company_name_x = (A4[0] - company_name_width) / 2
    company_name_y = 650  # Adjust the y-coordinate as needed
    c.drawString(company_name_x, company_name_y, company_name)

    c.setFont("Helvetica", 12)

    # Draw expenses table
    c.drawString(50, 600, "Expenses")  # Title
    c.drawString(50, 580, "No.")
    c.drawString(100, 580, "Amount")
    c.drawString(200, 580, "Category")
    c.drawString(300, 580, "Description")
    c.drawString(450, 580, "Date")  # Adjusted x-coordinate for date

    y = 560  # Initial y-coordinate
    for i, expense in enumerate(expenses, start=1):
        c.drawString(50, y, str(i))
        c.drawString(100, y, str(expense.amount))
        c.drawString(200, y, expense.category)
        c.drawString(300, y, expense.description)
        c.drawString(450, y, str(expense.date))  # Adjusted x-coordinate for date
        y -= 20

    # Draw total
    c.drawString(50, y, "Total")
    c.drawString(100, y, str(total))

    c.save()

    # Read the generated PDF file and write it to the response
    with open(pdf_file_path, 'rb') as pdf_file:
        response.write(pdf_file.read())

    # Delete the temporary directory and its contents
    os.remove(pdf_file_path)
    os.rmdir(temp_dir)

    return response
