from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .forms import SignUpForm, AddRecordForm, AddRecordForm_compagny_information
from .models import company_information
from .models import Record
from django.conf import settings  # Importez les paramètres Django
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import json
import time
import os
import csv
import openpyxl
import pyotp
import qrcode
import datetime


def model_table(table):
    # Filtrage des enregistrements
    if table == 'table1':
        model = company_information
    else:
        model = Record
    return model


def query_and_filter_records(request, table, model, search_value=None, page=1, per_page=10):
    # Sélection du queryset
    if table == 'table1':
        records_query = company_information.objects.all()
    else:
        records_query = Record.objects.all()

    # Obtenez les noms des champs du modèle
    field_names = [field.name for field in model._meta.get_fields()]

    # Appliquer les filtres AVANT la pagination
    if search_value:
        if 'phone' in field_names and 'address' in field_names:
            records_query = records_query.filter(
                Q(phone__icontains=search_value) | Q(address__icontains=search_value)
            )
        if 'siren' in field_names and 'nom_entreprise' in field_names:
            records_query = records_query.filter(
                Q(nom_entreprise__icontains=search_value) | Q(siren__icontains=search_value)
            )

    # Trier par ID
    records_query = records_query.order_by('id')

    # Pagination
    paginator = Paginator(records_query, per_page)

    try:
        records_page = paginator.page(page)
    except PageNotAnInteger:
        records_page = paginator.page(1)  # Retourne la première page si `page` est invalide
    except EmptyPage:
        records_page = paginator.page(paginator.num_pages)  # Retourne la dernière page si `page` est trop grand
    print(records_page)
    # ✅ Retourne uniquement les objets paginés
    return records_page


def home(request):
    # Récupération des paramètres GET
    table = request.GET.get('table', 'table1')
    search_value = request.GET.get('searchValue', '').strip()
    page = request.GET.get('page', 1)
    per_page = request.GET.get('elementsPerPage', 10)

    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        page, per_page = 1, 10  # Valeurs par défaut si erreur de conversion

    # Filtrage et pagination
    model = model_table(table)
    records_query= query_and_filter_records(request, table, model, search_value=search_value, page=page, per_page=per_page)

    # Calcul du nombre total d'enregistrements après filtrage
    record_count = records_query.paginator.count

    # Check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if check_code_verified(request, username):  # Ensure this logic works as expected
                messages.success(request, "You Have Been Logged In!")
                return redirect('qrcode', username=username)
            else:
                logout(request)  # Logout if code verification fails
                messages.error(request, "Error with code verification. Please try again.")
                return redirect('home')
        else:
            messages.error(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {
            'table': table,
            'records': records_query,  # Contient les objets paginés
            'record_count': record_count,
            'search_value': search_value,
            'current_page': records_query.number,
            'total_pages': records_query.paginator.num_pages,
            'has_next': records_query.has_next(),
            'has_previous': records_query.has_previous(),
            'next_page': records_query.next_page_number() if records_query.has_next() else None,
            'previous_page': records_query.previous_page_number() if records_query.has_previous() else None,
            'elements_per_page': per_page,
        })
def TOW_FA(request, username):

    # Obtenez le chemin complet du répertoire `static` de votre application Django
    static_root = os.path.join(settings.BASE_DIR, 'website', 'static')

    # Définissez le chemin complet du fichier `code_{username}.json`
    file_path = os.path.join(static_root, f'code_{username}.json')

    # Définissez le chemin complet du fichier d'image (par exemple, static/qrcode.png)
    image_path = os.path.join(static_root, f'qrcode_{username}.png')


    if not os.path.exists(file_path) or not os.path.exists(image_path):
        key = pyotp.random_base32()
        uri = pyotp.totp.TOTP(key).provisioning_uri(name=f'CDX CRM:{username}')

        # Générez le QR code et enregistrez-le avec le chemin d'accès complet
        qrcode.make(uri).save(image_path)

        # Écrivez la clé dans le fichier JSON
        with open(file_path, 'w') as json_file:
            json.dump({'key': key, 'first_connexion': True, 'code_verified': False}, json_file)

    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
        # Mettez à jour la valeur de la clé 'first connexion'
        json_data['code_verified'] = False
        # Écrivez le contenu mis à jour dans le fichier JSON
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file)

    # Renvoyer le modèle HTML avec le chemin d'accès au QR code
    return render(request, 'qrcode.html', {"json_data": json_data, 'image_path': image_path, 'username': username})

def verify_code(request, username):
    # Obtenez le chemin complet du répertoire `static` de votre application Django
    static_root = os.path.join(settings.BASE_DIR, 'website', 'static')
    image_path = os.path.join(static_root, f'qrcode_{username}.png')
    if request.method == 'POST':
        # Récupérez la valeur du champ 'code' depuis la requête POST
        entered_code = request.POST.get('code')

        # Obtenez le chemin complet du répertoire `static` de votre application Django
        static_root = os.path.join(settings.BASE_DIR, 'website', 'static')

        # Définissez le chemin complet du fichier `code_username.json`
        file_path = os.path.join(static_root, f'code_{username}.json')

        # Lisez le contenu du fichier JSON
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)

        # Récupérez la clé à partir du contenu JSON
        expected_code = json_data.get('key', '')
        # Générer le TOTP avec un décalage de 160 secondes
        expected_code = pyotp.TOTP(expected_code)  # interval is the time step in seconds
        current_time = int(time.time())
        expected_code = expected_code.at(current_time) # + 215
        # print(expected_code)
        # Vérifiez si le code entré correspond au code attendu
        if expected_code == entered_code:
            # Écrivez la clé dans le fichier JSON
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                # Mettez à jour la valeur de la clé 'first connexion'
                json_data['first_connexion'] = False
                json_data['code_verified'] = True

            # Écrivez le contenu mis à jour dans le fichier JSON
            with open(file_path, 'w') as json_file:
                json.dump(json_data, json_file)

            # Le code est correct
            if not check_code_verified(request, username):
                logout(request)
            return redirect('home')
        else:
            # Le code est incorrect
            return HttpResponse('Code incorrect')

    return render(request, 'qrcode.html', {'image_path': image_path, 'username': username})


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
            if check_code_verified(request, username):
                messages.success(request, "You Have Successfully Registered! Welcome!")
            else:
                logout(request)
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})

    return render(request, 'register.html', {'form':form})

def customer_record(request, pk):
    table = request.GET.get('table', 'table1')  # Extract 'table' from the request
    if request.user.is_authenticated:
        if table == 'table1':
            customer_record = company_information.objects.get(id=pk)
        else:
            customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record':customer_record, 'table': table})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

def delete_record(request, pk):
    table = request.GET.get('table', 'table1')  # Extract 'table' from the request

    if request.user.is_authenticated:
        if table == 'table2':
            delete_it = company_information.objects.get(id=pk)
        else:
            delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')


def add_record(request):
    table = request.GET.get('table', 'table1')  # Extract 'table' from the request

    if table == 'table1':
        form = AddRecordForm_compagny_information(request.POST or None)
    else:
        form = AddRecordForm(request.POST or None)

    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_record = form.save()
                messages.success(request, "Record Added...")
                return redirect('home')
        return render(request, 'add_record.html', {'form': form, 'table': table})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


def update_record(request, pk):
    table = request.GET.get('table', 'table1')  # Extract 'table' from the request

    if request.user.is_authenticated:
        if table == 'table1':
            current_record = company_information.objects.get(id=pk)
            form = AddRecordForm_compagny_information(request.POST or None, instance=current_record)
        else:
            current_record = Record.objects.get(id=pk)
            form = AddRecordForm(request.POST or None, instance=current_record)

        if form.is_valid():
            form.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect(reverse('home') + f'?table={table}')
        return render(request, 'update_record.html', {'form': form, 'table': table, 'pk': pk})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="table_data.csv"'

    # Récupérer les paramètres de la requête
    table = request.GET.get('table', 'table2')
    search_value = request.GET.get('searchValue', '').strip()
    page = request.GET.get('page', 1)  # Valeur par défaut = 1
    per_page = request.GET.get('elementsPerPage', 10)  # Valeur par défaut = 10

    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        page, per_page = 1, 10  # Sécurité en cas d'erreur de conversion

    # Récupération du modèle et des enregistrements filtrés
    model = model_table(table)
    records_query = query_and_filter_records(request, table, model, search_value=search_value, page=page, per_page=per_page)

    # Obtenir les noms des champs du modèle
    field_names = [field.name for field in model._meta.get_fields()]

    # Créer un writer CSV
    writer = csv.writer(response)
    writer.writerow(field_names)  # Écriture des en-têtes

    # Écriture des lignes de données
    for record in records_query:
        writer.writerow([getattr(record, field) for field in field_names])

    return response

def export_excel(request):
    # Créez un nouveau classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active

    # Récupération des paramètres GET
    table = request.GET.get('table', 'table2')
    search_value = request.GET.get('searchValue', '').strip()
    page = request.GET.get('page', 1)
    per_page = request.GET.get('elementsPerPage', 10)

    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        page, per_page = 1, 10  # Sécurité en cas d'erreur de conversion

    # Récupération du modèle et des enregistrements filtrés
    model = model_table(table)
    records_query =  query_and_filter_records(request, table, model, search_value=search_value, page=page, per_page=per_page)

    # Obtenir les noms des champs du modèle
    field_names = [field.name for field in model._meta.get_fields()]
    ws.append(field_names)  # Ajout de l'en-tête

    # Remplissage des données
    for record in records_query:
        row_data = []
        for field in field_names:
            value = getattr(record, field, '')  # Récupérer la valeur ou une chaîne vide si None
            if isinstance(value, (datetime.date, datetime.datetime)):
                value = value.replace(tzinfo=None)  # Retirer le fuseau horaire si nécessaire
            row_data.append(value)
        ws.append(row_data)

    # Création de la réponse HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table_data.xlsx"'

    # Écrire le fichier Excel dans la réponse HTTP
    wb.save(response)
    return response

def check_code_verified(request,username):
    static_root = os.path.join(settings.BASE_DIR, 'website', 'static')
    file_path = os.path.join(static_root, f'code_{username}.json')
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)
        # Mettez à jour la valeur de la clé 'first connexion'
        if json_data['code_verified'] == False:
            logout(request)
    return json_data['code_verified']