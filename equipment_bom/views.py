from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
import os
import json

from .models import (
    EquipmentType, Job, Material, BOMTemplate, EquipmentItem, 
    BOMComponent, Specification, ImportLog
)
from .excel_importer import ExcelBOMImporter
from .forms import JobForm, EquipmentItemForm, HeaterForm, TankForm, PumpForm, StackEconomizerForm, MaterialForm, BOMTemplateForm
from .template_utils import ExcelTemplateDiscovery

@login_required
def dashboard(request):
    """Main dashboard for equipment BOM system"""
    # Get summary statistics
    total_jobs = Job.objects.count()
    total_equipment = EquipmentItem.objects.count()
    total_materials = Material.objects.count()
    
    # Recent imports
    recent_imports = ImportLog.objects.all()[:5]
    
    # Equipment by type
    equipment_by_type = EquipmentItem.objects.values('equipment_type__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent jobs
    recent_jobs = Job.objects.all()[:5]
    
    # Recent equipment
    recent_equipment = EquipmentItem.objects.select_related('job', 'equipment_type').all()[:5]
    
    context = {
        'total_jobs': total_jobs,
        'total_equipment': total_equipment,
        'total_materials': total_materials,
        'recent_imports': recent_imports,
        'equipment_by_type': equipment_by_type,
        'recent_jobs': recent_jobs,
        'recent_equipment': recent_equipment,
    }
    
    return render(request, 'equipment_bom/dashboard.html', context)

@login_required
def job_list(request):
    """List all jobs"""
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    jobs = Job.objects.all()
    
    if search_query:
        jobs = jobs.filter(
            Q(job_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(customer__icontains=search_query)
        )
    
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Job._meta.get_field('status').choices,
    }
    
    return render(request, 'equipment_bom/job_list.html', context)

@login_required
def job_detail(request, job_id):
    """Job detail view with equipment items"""
    job = get_object_or_404(Job, id=job_id)
    equipment_items = job.equipment_items.select_related('equipment_type', 'primary_material').all()
    
    # Group equipment by type
    equipment_by_type = {}
    for item in equipment_items:
        eq_type = item.equipment_type.name
        if eq_type not in equipment_by_type:
            equipment_by_type[eq_type] = []
        equipment_by_type[eq_type].append(item)
    
    context = {
        'job': job,
        'equipment_items': equipment_items,
        'equipment_by_type': equipment_by_type,
    }
    
    return render(request, 'equipment_bom/job_detail.html', context)

@login_required
def equipment_list(request):
    """List all equipment items"""
    search_query = request.GET.get('q', '')
    equipment_type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    
    equipment = EquipmentItem.objects.select_related('job', 'equipment_type', 'primary_material').all()
    
    if search_query:
        equipment = equipment.filter(
            Q(item_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(job__job_number__icontains=search_query)
        )
    
    if equipment_type_filter:
        equipment = equipment.filter(equipment_type__id=equipment_type_filter)
    
    if status_filter:
        equipment = equipment.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(equipment, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get equipment types for filter
    equipment_types = EquipmentType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'equipment_type_filter': equipment_type_filter,
        'status_filter': status_filter,
        'equipment_types': equipment_types,
        'status_choices': EquipmentItem._meta.get_field('status').choices,
    }
    
    return render(request, 'equipment_bom/equipment_list.html', context)

@login_required
def equipment_detail(request, equipment_id):
    """Equipment item detail view"""
    equipment = get_object_or_404(EquipmentItem, id=equipment_id)
    components = equipment.components.select_related('material').all()
    specifications = equipment.specifications.all()
    
    context = {
        'equipment': equipment,
        'components': components,
        'specifications': specifications,
    }
    
    return render(request, 'equipment_bom/equipment_detail.html', context)

@login_required
def material_list(request):
    """List all materials"""
    search_query = request.GET.get('q', '')
    material_type_filter = request.GET.get('type', '')
    
    materials = Material.objects.all()
    
    if search_query:
        materials = materials.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if material_type_filter:
        materials = materials.filter(material_type=material_type_filter)
    
    # Pagination
    paginator = Paginator(materials, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get material types for filter
    material_types = Material.objects.values_list('material_type', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'material_type_filter': material_type_filter,
        'material_types': material_types,
    }
    
    return render(request, 'equipment_bom/material_list.html', context)

@login_required
def import_excel(request):
    """Excel import interface"""
    if request.method == 'POST':
        try:
            # Handle file upload
            excel_file = request.FILES.get('excel_file')
            equipment_type_name = request.POST.get('equipment_type')
            
            if not excel_file or not equipment_type_name:
                messages.error(request, 'Please select both a file and equipment type.')
                return redirect('equipment_bom:import_excel')
            
            # Save file temporarily
            file_path = os.path.join(settings.MEDIA_ROOT, 'temp', excel_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)
            
            # Import the data
            importer = ExcelBOMImporter(file_path, request.user, equipment_type_name)
            success = importer.import_excel()
            
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if success:
                messages.success(
                    request, 
                    f'Import completed successfully! '
                    f'Processed: {importer.records_processed}, '
                    f'Created: {importer.records_created}, '
                    f'Updated: {importer.records_updated}'
                )
            else:
                messages.warning(
                    request, 
                    f'Import completed with errors. '
                    f'Check the import log for details.'
                )
            
            return redirect('equipment_bom:import_logs')
            
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
            return redirect('equipment_bom:import_excel')
    
    # GET request - show import form
    equipment_types = EquipmentType.objects.all()
    
    context = {
        'equipment_types': equipment_types,
    }
    
    return render(request, 'equipment_bom/import_excel.html', context)

@login_required
def import_logs(request):
    """View import logs"""
    logs = ImportLog.objects.select_related('imported_by', 'equipment_type').all()
    
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'equipment_bom/import_logs.html', context)

@login_required
def import_log_detail(request, log_id):
    """Import log detail view"""
    import_log = get_object_or_404(ImportLog, id=log_id)
    
    context = {
        'import_log': import_log,
    }
    
    return render(request, 'equipment_bom/import_log_detail.html', context)

@login_required
def bom_template_list(request):
    """List BOM templates"""
    templates = BOMTemplate.objects.select_related('equipment_type', 'created_by').all()
    
    # Pagination
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'equipment_bom/bom_template_list.html', context)

@login_required
def bom_template_detail(request, template_id):
    """BOM template detail view"""
    template = get_object_or_404(BOMTemplate, id=template_id)
    
    context = {
        'template': template,
    }
    
    return render(request, 'equipment_bom/bom_template_detail.html', context)

@login_required
def export_excel(request, equipment_type_id):
    """Export equipment data to Excel"""
    equipment_type = get_object_or_404(EquipmentType, id=equipment_type_id)
    equipment_items = EquipmentItem.objects.filter(equipment_type=equipment_type).select_related(
        'job', 'primary_material'
    ).prefetch_related('specifications')
    
    # Create Excel file using pandas
    import pandas as pd
    from io import BytesIO
    
    # Prepare data for export
    data = []
    for item in equipment_items:
        row = {
            'Item Number': item.item_number,
            'Description': item.description,
            'Job Number': item.job.job_number,
            'Product Type': item.product_type,
            'Supply Type': item.supply_type,
            'Diameter': item.diameter,
            'Height': item.height,
            'Length': item.length,
            'Width': item.width,
            'Thickness': item.thickness,
            'Position': item.position,
            'Material': item.primary_material.code if item.primary_material else '',
            'Status': item.status,
        }
        
        # Add specifications
        for spec in item.specifications.all():
            row[spec.spec_type] = spec.value
        
        data.append(row)
    
    # Create DataFrame and export
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=equipment_type.name, index=False)
    
    output.seek(0)
    
    # Create HTTP response
    filename = f"{equipment_type.name}_Export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def api_equipment_data(request):
    """API endpoint for equipment data (for charts/dashboards)"""
    equipment_type_id = request.GET.get('type')
    
    if equipment_type_id:
        equipment = EquipmentItem.objects.filter(equipment_type_id=equipment_type_id)
    else:
        equipment = EquipmentItem.objects.all()
    
    # Group by status
    status_counts = equipment.values('status').annotate(count=Count('id'))
    
    # Group by equipment type
    type_counts = equipment.values('equipment_type__name').annotate(count=Count('id'))
    
    data = {
        'status_counts': list(status_counts),
        'type_counts': list(type_counts),
    }
    
    return JsonResponse(data)


# ===== CREATION VIEWS =====

@login_required
def job_create(request):
    """Create a new job"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, f'Job "{job.job_number}" created successfully!')
            return redirect('equipment_bom:job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'title': 'Create New Job',
        'submit_text': 'Create Job'
    }
    return render(request, 'equipment_bom/job_form.html', context)


@login_required
def job_edit(request, job_id):
    """Edit an existing job"""
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.job_number}" updated successfully!')
            return redirect('equipment_bom:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'title': f'Edit Job: {job.job_number}',
        'submit_text': 'Update Job'
    }
    return render(request, 'equipment_bom/job_form.html', context)


@login_required
def material_create(request):
    """Create a new material"""
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save()
            messages.success(request, f'Material "{material.code}" created successfully!')
            return redirect('equipment_bom:material_list')
    else:
        form = MaterialForm()
    
    context = {
        'form': form,
        'title': 'Create New Material',
        'submit_text': 'Create Material'
    }
    return render(request, 'equipment_bom/material_form.html', context)


@login_required
def material_edit(request, material_id):
    """Edit an existing material"""
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, f'Material "{material.code}" updated successfully!')
            return redirect('equipment_bom:material_list')
    else:
        form = MaterialForm(instance=material)
    
    context = {
        'form': form,
        'material': material,
        'title': f'Edit Material: {material.code}',
        'submit_text': 'Update Material'
    }
    return render(request, 'equipment_bom/material_form.html', context)


@login_required
def equipment_create(request):
    """Create a new equipment item with type selection"""
    equipment_type = request.GET.get('type', '')
    
    # Determine which form to use based on equipment type
    form_class = EquipmentItemForm
    if 'heater' in equipment_type.lower():
        form_class = HeaterForm
    elif 'tank' in equipment_type.lower():
        form_class = TankForm
    elif 'pump' in equipment_type.lower():
        form_class = PumpForm
    elif 'economizer' in equipment_type.lower():
        form_class = StackEconomizerForm
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.created_by = request.user
            equipment.save()
            messages.success(request, f'Equipment "{equipment.item_number}" created successfully!')
            return redirect('equipment_bom:equipment_detail', equipment_id=equipment.id)
    else:
        form = form_class()
    
    context = {
        'form': form,
        'equipment_type': equipment_type,
        'title': f'Create New {equipment_type.title() if equipment_type else "Equipment"}',
        'submit_text': 'Create Equipment'
    }
    return render(request, 'equipment_bom/equipment_form.html', context)


@login_required
def equipment_edit(request, equipment_id):
    """Edit an existing equipment item"""
    equipment = get_object_or_404(EquipmentItem, id=equipment_id)
    
    # Determine which form to use based on equipment type
    form_class = EquipmentItemForm
    if 'heater' in equipment.equipment_type.name.lower():
        form_class = HeaterForm
    elif 'tank' in equipment.equipment_type.name.lower():
        form_class = TankForm
    elif 'pump' in equipment.equipment_type.name.lower():
        form_class = PumpForm
    elif 'economizer' in equipment.equipment_type.name.lower():
        form_class = StackEconomizerForm
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Equipment "{equipment.item_number}" updated successfully!')
            return redirect('equipment_bom:equipment_detail', equipment_id=equipment.id)
    else:
        form = form_class(instance=equipment)
    
    context = {
        'form': form,
        'equipment': equipment,
        'title': f'Edit Equipment: {equipment.item_number}',
        'submit_text': 'Update Equipment'
    }
    return render(request, 'equipment_bom/equipment_form.html', context)


@login_required
def bom_template_create(request):
    """Create a new BOM template"""
    if request.method == 'POST':
        form = BOMTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'BOM Template "{template.template_code}" created successfully!')
            return redirect('equipment_bom:bom_template_detail', template_id=template.id)
    else:
        form = BOMTemplateForm()
    
    context = {
        'form': form,
        'title': 'Create New BOM Template',
        'submit_text': 'Create Template'
    }
    return render(request, 'equipment_bom/bom_template_form.html', context)


@login_required
def bom_template_edit(request, template_id):
    """Edit an existing BOM template"""
    template = get_object_or_404(BOMTemplate, id=template_id)
    if request.method == 'POST':
        form = BOMTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'BOM Template "{template.template_code}" updated successfully!')
            return redirect('equipment_bom:bom_template_detail', template_id=template.id)
    else:
        form = BOMTemplateForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
        'title': f'Edit BOM Template: {template.template_code}',
        'submit_text': 'Update Template'
    }
    return render(request, 'equipment_bom/bom_template_form.html', context)


@login_required
def excel_templates(request):
    """Display available Excel templates"""
    discovery = ExcelTemplateDiscovery()
    templates = discovery.get_available_templates()
    
    context = {
        'templates': templates,
        'supported_types': discovery.supported_types,
    }
    
    return render(request, 'equipment_bom/excel_templates.html', context)
