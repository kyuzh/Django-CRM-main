from django.contrib import admin
from .models import Record
from .models import company_information

admin.site.register(Record)
admin.site.register(company_information)

