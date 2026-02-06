from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Record, company_information

# Resource for company_information
class CompanyInformationResource(resources.ModelResource):
    class Meta:
        model = company_information
        import_id_fields = ('id',)  # Use a unique field like 'id'
        skip_unchanged = True        # optional: skip unchanged rows

# Admin with import/export
class CompanyInformationAdmin(ImportExportModelAdmin):
    resource_class = CompanyInformationResource

# Resource for Record
class RecordResource(resources.ModelResource):
    class Meta:
        model = Record
        import_id_fields = ('id',)
        skip_unchanged = True

class RecordAdmin(ImportExportModelAdmin):
    resource_class = RecordResource

# Register models with Import/Export enabled
admin.site.register(company_information, CompanyInformationAdmin)
admin.site.register(Record, RecordAdmin)
