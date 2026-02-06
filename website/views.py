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
from django.views.decorators.cache import never_cache
import json
import time
import os
import csv
import openpyxl
import pyotp
import qrcode
import datetime
from functools import wraps
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('qrcode', username=username)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'login.html')
def require_code_verified(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        username = request.user.username  # récupérer le username de l'utilisateur connecté
        static_root_jscode = os.path.join(settings.BASE_DIR, 'website', 'static', 'jscode')
        file_path = os.path.join(static_root_jscode, f'code_{username}.json')

        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            messages.error(request, "Code QR non généré. Veuillez vous reconnecter.")
            return redirect('home')

        # Lire le JSON
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)

        if json_data.get('code_verified') is False:
            messages.error(request, "Vous devez vérifier votre code avant de continuer.")
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


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


@login_required(login_url='login')  # Redirige vers login si non connecté
def home(request):
    """
    Affiche la page principale avec le tableau filtré et paginé.
    """

    # --- Récupération des paramètres GET ---
    table = request.GET.get('table', 'table1')
    search_value = request.GET.get('searchValue', '').strip()

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        per_page = int(request.GET.get('elementsPerPage', 10))
    except ValueError:
        per_page = 10

    # --- Récupération du modèle ---
    model = model_table(table)
    if model is None:
        # Si le modèle n'existe pas, renvoyer 404 ou fallback
        from django.http import Http404
        raise Http404("Table inconnue")

    # --- Filtrage et pagination ---
    records_query = query_and_filter_records(
        request,
        table,
        model,
        search_value=search_value,
        page=page,
        per_page=per_page
    )

    # --- Calcul du nombre total d'enregistrements ---
    record_count = records_query.paginator.count

    # --- Contexte pour le template ---
    context = {
        'table': table,
        'records': records_query,
        'record_count': record_count,
        'search_value': search_value,
        'current_page': records_query.number,
        'total_pages': records_query.paginator.num_pages,
        'has_next': records_query.has_next(),
        'has_previous': records_query.has_previous(),
        'next_page': records_query.next_page_number() if records_query.has_next() else None,
        'previous_page': records_query.previous_page_number() if records_query.has_previous() else None,
        'elements_per_page': per_page,
    }

    return render(request, 'home.html', context)
def TOW_FA(request, username):

    # Obtenez le chemin complet du répertoire `static` de votre application Django
    static_root_qrcode = os.path.join(settings.BASE_DIR, 'website', 'static', 'qrcode')
    static_root_jscode = os.path.join(settings.BASE_DIR, 'website', 'static', 'jscode')
    # Définissez le chemin complet du fichier `code_{username}.json`
    file_path = os.path.join(static_root_jscode, f'code_{username}.json')

    # Définissez le chemin complet du fichier d'image (par exemple, static/qrcode.png)
    image_path = os.path.join(static_root_qrcode , f'qrcode_{username}.png')


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

    static_root_qrcode = os.path.join(settings.BASE_DIR, 'website', 'static', 'qrcode')

    image_path = os.path.join(static_root_qrcode, f'qrcode_{username}.png')
    if request.method == 'POST':
        # Récupérez la valeur du champ 'code' depuis la requête POST
        entered_code = request.POST.get('code')

        # Obtenez le chemin complet du répertoire `static` de votre application Django
        static_root_jscode = os.path.join(settings.BASE_DIR, 'website', 'static', 'jscode')

        # Définissez le chemin complet du fichier `code_username.json`
        file_path = os.path.join(static_root_jscode, f'code_{username}.json')

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
    if request.user.is_authenticated:
        username = request.user.username

        # Définir code_verified à False
        static_root = os.path.join(settings.BASE_DIR, 'website', 'static', 'jscode')
        file_path = os.path.join(static_root, f'code_{username}.json')

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)

            data['code_verified'] = False

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

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
@require_code_verified
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
@require_code_verified
def delete_record(request, pk):
    table = request.GET.get('table', 'table1')  # Extract 'table' from the request

    if request.user.is_authenticated:
        if table == 'table1':
            delete_it = company_information.objects.get(id=pk)
        else:
            delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')

@require_code_verified
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

@require_code_verified
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
@require_code_verified
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
@require_code_verified
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

def check_code_verified(request, username):
    """
    Vérifie si l'utilisateur a validé le code 2FA
    et si la vérification date de moins de 30 minutes.
    Si expiré ou non vérifié, met code_verified = False.
    """

    # 1️⃣ Vérifie la session
    last_verified = request.session.get(f'{username}_last_verified')
    if last_verified:
        try:
            # Convertir la string ISO en datetime aware
            last_verified_time = timezone.make_aware(timezone.datetime.fromisoformat(last_verified))
            if timezone.now() - last_verified_time < timedelta(minutes=30):
                return True  # Toujours valide
        except Exception:
            pass  # Ignore erreurs de parsing

    # 2️⃣ Lire le JSON
    static_root = os.path.join(settings.BASE_DIR, 'website', 'static', 'jscode')
    file_path = os.path.join(static_root, f'code_{username}.json')

    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # 3️⃣ Vérification du code
    if json_data.get('code_verified', False):
        # Mettre à jour la session avec l'heure actuelle
        request.session[f'{username}_last_verified'] = timezone.now().isoformat()
        return True

    # 4️⃣ Expiré ou non vérifié → forcer code_verified à False
    json_data['code_verified'] = False
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    return False