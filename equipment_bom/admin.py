from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EquipmentType, Job, Material, BOMTemplate, EquipmentItem, 
    BOMComponent, Specification, ImportLog
)

@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_number', 'description', 'customer', 'project_manager', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date', 'project_manager']
    search_fields = ['job_number', 'description', 'customer']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job_number', 'description', 'customer', 'project_manager')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'material_type', 'description']
    list_filter = ['material_type']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'material_type', 'description')
        }),
        ('Properties', {
            'fields': ('properties',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BOMTemplate)
class BOMTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_code', 'name', 'equipment_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['equipment_type', 'is_active', 'created_at']
    search_fields = ['template_code', 'name', 'description']
    ordering = ['template_code']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('template_code', 'name', 'equipment_type', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    list_display = [
        'item_number', 'description', 'job', 'equipment_type', 'product_type', 
        'status', 'created_by'
    ]
    list_filter = [
        'equipment_type', 'product_type', 'supply_type', 'status', 
        'primary_material', 'created_at'
    ]
    search_fields = ['item_number', 'description', 'job__job_number']
    date_hierarchy = 'created_at'
    ordering = ['item_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_number', 'description', 'job', 'bom_template', 'equipment_type')
        }),
        ('Product Details', {
            'fields': ('product_type', 'supply_type')
        }),
        ('Dimensions', {
            'fields': ('diameter', 'height', 'length', 'width', 'thickness'),
            'classes': ('collapse',)
        }),
        ('Specifications', {
            'fields': (
                'gas_train_size', 'gas_train_mount', 'heater_model', 
                'flange_inlet', 'stack_diameter'
            ),
            'classes': ('collapse',)
        }),
        ('Materials', {
            'fields': ('primary_material', 'secondary_material', 'position'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'equipment_type', 'primary_material')

@admin.register(BOMComponent)
class BOMComponentAdmin(admin.ModelAdmin):
    list_display = [
        'component_number', 'description', 'equipment_item', 'product_type', 
        'supply_type', 'status'
    ]
    list_filter = [
        'product_type', 'supply_type', 'status', 'material', 'equipment_item__equipment_type'
    ]
    search_fields = ['component_number', 'description', 'equipment_item__item_number']
    ordering = ['equipment_item', 'component_number']
    
    fieldsets = (
        ('Component Information', {
            'fields': ('component_number', 'description', 'equipment_item', 'bom_template')
        }),
        ('Product Details', {
            'fields': ('product_type', 'supply_type')
        }),
        ('Dimensions', {
            'fields': ('diameter', 'height', 'length', 'width', 'thickness'),
            'classes': ('collapse',)
        }),
        ('Specifications', {
            'fields': (
                'gas_train_size', 'gas_train_mount', 'heater_model', 
                'flange_inlet', 'stack_diameter', 'tank_diameter', 'tank_height'
            ),
            'classes': ('collapse',)
        }),
        ('Materials & Position', {
            'fields': ('material', 'position'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('equipment_item', 'material')

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['spec_type', 'value', 'unit', 'equipment_item', 'component']
    list_filter = ['spec_type', 'equipment_item__equipment_type']
    search_fields = ['spec_type', 'value', 'description']
    ordering = ['spec_type']
    
    fieldsets = (
        ('Specification Details', {
            'fields': ('spec_type', 'value', 'unit', 'description')
        }),
        ('Related Items', {
            'fields': ('equipment_item', 'component'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'file_name', 'equipment_type', 'imported_by', 'import_date', 
        'records_processed', 'records_created', 'records_updated', 'status'
    ]
    list_filter = ['equipment_type', 'status', 'import_date', 'imported_by']
    search_fields = ['file_name', 'imported_by__username']
    date_hierarchy = 'import_date'
    ordering = ['-import_date']
    
    fieldsets = (
        ('Import Information', {
            'fields': ('file_name', 'equipment_type', 'imported_by', 'import_date')
        }),
        ('Results', {
            'fields': ('records_processed', 'records_created', 'records_updated', 'status')
        }),
        ('Errors', {
            'fields': ('errors',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['import_date', 'records_processed', 'records_created', 'records_updated', 'errors']
    
    def has_add_permission(self, request):
        return False  # Import logs are created automatically during imports
