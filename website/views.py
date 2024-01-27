from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .forms import SignUpForm, AddRecordForm
from .models import company_information
from .models import Record
from django.conf import settings  # Importez les paramètres Django
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import os
import csv
import openpyxl
import pyotp
import qrcode

def model_table(table):
    # Filtrage des enregistrements
    if table == 'table1':
        model = company_information
    else:
        model = Record
    return model

def home(request):
    # Récupérez la valeur du paramètre de requête 'table'
    table = request.GET.get('table', 'table2')  # Si le paramètre 'table' n'est pas présent, utilisez 'table2' par défaut

    # Filtrage des enregistrements
    if table == 'table1':
        records_query = company_information.objects.all()
    else:
        records_query = Record.objects.all()

    model = model_table(table)

    # Obtenez les noms des champs du modèle
    field_names = [field.name for field in model._meta.get_fields()]
    # Récupérez la valeur du filtre depuis la requête GET
    search_value = request.GET.get('searchValue', '')

    # Triez le QuerySet
    records_query = records_query.order_by('id')

    if 'phone' in field_names and 'address' in field_names:
        # Récupérez les valeurs des filtres depuis la requête GET
        search_value = request.GET.get('searchValue')
        # Appliquez le filtre si la valeur n'est pas vide
        if search_value:
            # Utilisez Q pour effectuer une recherche sur plusieurs champs
            records_query = records_query.filter(Q(phone__icontains=search_value) | Q(address__icontains=search_value))

    if 'siren' in field_names and 'nom_entreprise' in field_names:
        # Récupérez les valeurs des filtres depuis la requête GET
        search_value = request.GET.get('searchValue')
        # Appliquez le filtre si la valeur n'est pas vide
        if search_value:
            # Utilisez Q pour effectuer une recherche sur plusieurs champs
            records_query = records_query.filter(Q(nom_entreprise__icontains=search_value) | Q(siren__icontains=search_value))

    # Pagination
    page = request.GET.get('page', 1)  # Par défaut, la première page est affichée
    paginator = Paginator(records_query, 200)  # Vous pouvez ajuster le nombre d'enregistrements par page

    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)
    record_count = records_query.count()

    # Check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('qrcode', username=username)
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {'table': table, 'records':records,'record_count':record_count, 'search_value': search_value})

def TOW_FA(request, username):
    key = pyotp.random_base32()
    uri = pyotp.totp.TOTP(key).provisioning_uri(name="CDX CRM")

    # Obtenez le chemin complet du répertoire `static` de votre application Django
    static_root = os.path.join(settings.BASE_DIR, 'website', 'templates', 'static')

    # Définissez le chemin complet du fichier `code.txt`
    file_path = os.path.join(static_root, 'code_' +username + ' .txt')

    # Définissez le chemin complet du fichier d'image (par exemple, static/qrcode.png)
    image_path = os.path.join(static_root, 'qrcode_' +username + '.png')

    # Générez le QR code et enregistrez-le avec le chemin d'accès complet
    qrcode.make(uri).save(image_path)

    # Écrivez la clé dans le fichier
    with open(file_path, 'w') as file:
        file.write(key)
    # Renvoyer le modèle HTML avec le chemin d'accès au QR code
    return redirect('qrcode', username=username)


def verify_code(request, username):
    if request.method == 'POST':
        # Récupérez la valeur du champ 'code' depuis la requête POST
        entered_code = request.POST.get('code')

        # Obtenez le chemin complet du répertoire `static` de votre application Django
        static_root = os.path.join(settings.BASE_DIR, 'website', 'templates', 'static')

        # Définissez le chemin complet du fichier `code.txt`
        file_path = os.path.join(static_root, 'code_' + username + ' .txt')

        # Lisez le contenu du fichier
        with open(file_path, 'r') as file:
            expected_code = file.read()

        expected_code = pyotp.TOTP(expected_code)

        # Vérifiez si le code entré correspond au code attendu
        if expected_code.verify(entered_code):
            print("ok")
            # Le code est correct
            return render(request, 'home.html')
        else:
            # Le code est incorrect
            print("ko")
            return HttpResponse('Code incorrect')

    return render(request, 'qrcode.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})

    return render(request, 'register.html', {'form':form})

def customer_record(request, pk):
    if request.user.is_authenticated:
        # Look Up Records
        customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record':customer_record})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')


def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_record = form.save()
                messages.success(request, "Record Added...")
                return redirect('home')
        return render(request, 'add_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect('home')
        return render(request, 'update_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="table_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Address', 'City', 'State', 'Zipcode', 'Created At', 'ID'])

    start = request.GET.get('start') or 0
    start = max(int(start), 0)
    end = request.GET.get('end') or 3
    end = int(end)

    records = Record.objects.all() # Récupérez les données de votre modèle

    for record in records:
        writer.writerow([record.first_name, record.email, record.phone, record.address, record.city,
                         record.state, record.zipcode, record.created_at, record.id])

    return response

def export_excel(request):
    # Créez un nouveau classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active

    # Écrivez l'en-tête du fichier Excel
    ws.append(['Name', 'Email', 'Phone', 'Address', 'City', 'State', 'Zipcode', 'Created At', 'ID'])

    records = Record.objects.all()  # Récupérez les données de votre modèle

    # Écrivez les données de la base de données dans le fichier Excel
    for record in records:
        # Assurez-vous que la date est sans information de fuseau horaire (tzinfo à None)
        created_at_without_tz = record.created_at.replace(tzinfo=None)

        ws.append([record.first_name, record.email, record.phone, record.address, record.city,
                   record.state, record.zipcode, created_at_without_tz, record.id])

    # Créez une réponse HTTP avec le contenu du fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table_data.xlsx"'

    # Écrivez le contenu du classeur Excel dans la réponse HTTP
    wb.save(response)

    return response