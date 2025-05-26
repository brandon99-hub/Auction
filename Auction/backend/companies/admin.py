from django.contrib import admin
from .models import Company, CompanyAddress, CompanyDocument

class CompanyAddressInline(admin.TabularInline):
    model = CompanyAddress
    extra = 1

class CompanyDocumentInline(admin.TabularInline):
    model = CompanyDocument
    extra = 1

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'verified', 'created_at')
    list_filter = ('status', 'verified')
    search_fields = ('name', 'description', 'tax_id')
    filter_horizontal = ('managers',)
    inlines = [CompanyAddressInline, CompanyDocumentInline]

class CompanyAddressAdmin(admin.ModelAdmin):
    list_display = ('company', 'city', 'state', 'country', 'is_primary')
    list_filter = ('country', 'is_primary')
    search_fields = ('company__name', 'city', 'state')

class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ('company', 'document_type', 'is_verified', "created_at")
    list_filter = ('document_type', 'is_verified')
    search_fields = ('company__name','document_type')

admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyAddress, CompanyAddressAdmin)
admin.site.register(CompanyDocument, CompanyDocumentAdmin)
