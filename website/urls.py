from django.urls import path
from . import views

from django.views.decorators.cache import never_cache
urlpatterns = [
    path('', views.home,  name='home'),
    path('home/', never_cache(views.home), name='home'),
    # path('login/', views.login_user, name='login'),
    path('logout/', never_cache(views.logout_user), name='logout'),
    path('register/', never_cache(views.register_user), name='register'),
    path('record/<int:pk>', never_cache(views.customer_record), name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('add_record/', views.add_record, name='add_record'),
    path('update_record/<int:pk>', never_cache(views.update_record), name='update_record'),
    # Exemple d'URL pour l'importation CSV
    path('export_csv/', views.export_csv, name='export_csv'),
    # Exemple d'URL pour l'importation Excel (si nécessaire)
    path('export_excel/', views.export_excel, name='export_excel'),
    path('qrcode/<str:username>/', views.TOW_FA, name='qrcode'),
    path('verify_code/<str:username>/', views.verify_code, name='verify_code'),

]
