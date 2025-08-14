from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid

class EquipmentType(models.Model):
    """Equipment types: Heater, Tank, Pump, Stack Economizer"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=20, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Job(models.Model):
    """Job/Project information"""
    job_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    customer = models.CharField(max_length=200, blank=True)
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ], default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.job_number}: {self.description}"

class Material(models.Model):
    """Material specifications"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=100, choices=[
        ('316', '316 Stainless Steel'),
        ('304', '304 Stainless Steel'),
        ('AL6XN', 'AL6XN Alloy'),
        ('RM', 'RM Material'),
        ('GP', 'GP Material'),
        ('BM', 'BM Material'),
        ('TE', 'TE Material'),
        ('FM', 'FM Material'),
        ('HW', 'Hot Water'),
        ('TW', 'Tepid Water'),
        ('CW', 'Cold Water'),
        ('CMF', 'CMF Material'),
        ('RO', 'RO Material'),
        ('WW', 'WW Material'),
    ])
    properties = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class BOMTemplate(models.Model):
    """Bill of Materials Template"""
    template_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_code']
    
    def __str__(self):
        return f"{self.template_code}: {self.name}"

class EquipmentItem(models.Model):
    """Main equipment item (e.g., Heater, Tank, Pump)"""
    item_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='equipment_items')
    bom_template = models.ForeignKey(BOMTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=100, choices=[
        ('Item', 'Item'),
        ('Sub Assy', 'Sub Assembly'),
        ('FG FAB', 'Finished Goods Fabrication'),
    ])
    supply_type = models.CharField(max_length=100, choices=[
        ('Pegged Supply', 'Pegged Supply'),
        ('Phantom', 'Phantom'),
        ('Item', 'Item'),
    ], blank=True)
    
    # Dimensions and specifications
    diameter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional specifications
    gas_train_size = models.CharField(max_length=50, blank=True)
    gas_train_mount = models.CharField(max_length=50, blank=True)
    heater_model = models.CharField(max_length=50, blank=True)
    flange_inlet = models.CharField(max_length=50, blank=True)
    stack_diameter = models.CharField(max_length=50, blank=True)
    
    # Heater-specific fields
    heater_type = models.CharField(max_length=50, blank=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pressure_rating = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Tank-specific fields
    tank_type = models.CharField(max_length=50, blank=True)
    working_pressure = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pump-specific fields
    pump_type = models.CharField(max_length=50, blank=True)
    flow_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    head = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    power = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Stack Economizer-specific fields
    economizer_type = models.CharField(max_length=50, blank=True)
    efficiency = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inlet_temp = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    outlet_temp = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Material and finish
    primary_material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_equipment')
    secondary_material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_equipment')
    
    # Position and orientation
    position = models.CharField(max_length=50, choices=[
        ('LEFT', 'Left'),
        ('RIGHT', 'Right'),
        ('CENTER', 'Center'),
    ], blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=50, choices=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
        ('shipped', 'Shipped'),
    ], default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['item_number']
    
    def __str__(self):
        return f"{self.item_number}: {self.description}"

class BOMComponent(models.Model):
    """Individual components within a BOM"""
    equipment_item = models.ForeignKey(EquipmentItem, on_delete=models.CASCADE, related_name='components')
    component_number = models.CharField(max_length=50)
    description = models.TextField()
    bom_template = models.ForeignKey(BOMTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=100, choices=[
        ('Item', 'Item'),
        ('Sub Assy', 'Sub Assembly'),
        ('Phantom', 'Phantom'),
    ])
    supply_type = models.CharField(max_length=100, choices=[
        ('Pegged Supply', 'Pegged Supply'),
        ('Phantom', 'Phantom'),
        ('Item', 'Item'),
    ], blank=True)
    
    # Dimensions and specifications
    diameter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Material specifications
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Position and orientation
    position = models.CharField(max_length=50, choices=[
        ('LEFT', 'Left'),
        ('RIGHT', 'Right'),
        ('CENTER', 'Center'),
    ], blank=True)
    
    # Additional specifications
    gas_train_size = models.CharField(max_length=50, blank=True)
    gas_train_mount = models.CharField(max_length=50, blank=True)
    heater_model = models.CharField(max_length=50, blank=True)
    flange_inlet = models.CharField(max_length=50, blank=True)
    stack_diameter = models.CharField(max_length=50, blank=True)
    tank_diameter = models.CharField(max_length=50, blank=True)
    tank_height = models.CharField(max_length=50, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=50, choices=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
    ], default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['component_number']
        unique_together = ['equipment_item', 'component_number']
    
    def __str__(self):
        return f"{self.component_number}: {self.description}"

class Specification(models.Model):
    """Additional specifications for equipment or components"""
    equipment_item = models.ForeignKey(EquipmentItem, on_delete=models.CASCADE, related_name='specifications', null=True, blank=True)
    component = models.ForeignKey(BOMComponent, on_delete=models.CASCADE, related_name='specifications', null=True, blank=True)
    spec_type = models.CharField(max_length=100, choices=[
        ('Heater Diameter', 'Heater Diameter'),
        ('Heater Height', 'Heater Height'),
        ('Stack Diameter', 'Stack Diameter'),
        ('Flange Inlet', 'Flange Inlet'),
        ('Gas Train Size', 'Gas Train Size'),
        ('Gas Train Mount', 'Gas Train Mount'),
        ('Heater Model', 'Heater Model'),
        ('Tank Diameter', 'Tank Diameter'),
        ('Tank Height', 'Tank Height'),
        ('Material', 'Material'),
        ('Type', 'Type'),
        ('HP', 'Horsepower'),
    ])
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['spec_type']
    
    def __str__(self):
        return f"{self.spec_type}: {self.value}"

class ImportLog(models.Model):
    """Log of Excel imports for tracking"""
    file_name = models.CharField(max_length=255)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ], default='in_progress')
    
    class Meta:
        ordering = ['-import_date']
    
    def __str__(self):
        return f"Import {self.file_name} - {self.import_date.strftime('%Y-%m-%d %H:%M')}"
