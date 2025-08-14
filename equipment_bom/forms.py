from django import forms
from django.contrib.auth.models import User
from .models import EquipmentItem, Job, Material, EquipmentType, BOMTemplate


class JobForm(forms.ModelForm):
    """Form for creating/editing jobs"""
    
    class Meta:
        model = Job
        fields = ['job_number', 'description', 'customer', 'project_manager', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EquipmentItemForm(forms.ModelForm):
    """Form for creating/editing equipment items"""
    
    class Meta:
        model = EquipmentItem
        fields = [
            'item_number', 'description', 'job', 'equipment_type', 'product_type',
            'diameter', 'height', 'length', 'width', 'primary_material'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'diameter': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'height': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'length': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'width': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make job field required for new equipment
        if not self.instance.pk:
            self.fields['job'].required = True


class HeaterForm(EquipmentItemForm):
    """Specialized form for Heater equipment"""
    
    class Meta(EquipmentItemForm.Meta):
        fields = EquipmentItemForm.Meta.fields + ['heater_type', 'capacity', 'pressure_rating']
        widgets = {
            **EquipmentItemForm.Meta.widgets,
            'capacity': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'pressure_rating': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set equipment type to Heater
        heater_type = EquipmentType.objects.filter(name__icontains='Heater').first()
        if heater_type:
            self.fields['equipment_type'].initial = heater_type


class TankForm(EquipmentItemForm):
    """Specialized form for Tank equipment"""
    
    class Meta(EquipmentItemForm.Meta):
        fields = EquipmentItemForm.Meta.fields + ['tank_type', 'capacity', 'working_pressure']
        widgets = {
            **EquipmentItemForm.Meta.widgets,
            'capacity': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'working_pressure': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set equipment type to Tank
        tank_type = EquipmentType.objects.filter(name__icontains='Tank').first()
        if tank_type:
            self.fields['equipment_type'].initial = tank_type


class PumpForm(EquipmentItemForm):
    """Specialized form for Pump equipment"""
    
    class Meta(EquipmentItemForm.Meta):
        fields = EquipmentItemForm.Meta.fields + ['pump_type', 'flow_rate', 'head', 'power']
        widgets = {
            **EquipmentItemForm.Meta.widgets,
            'flow_rate': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'head': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'power': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set equipment type to Pump
        pump_type = EquipmentType.objects.filter(name__icontains='Pump').first()
        if pump_type:
            self.fields['equipment_type'].initial = pump_type


class StackEconomizerForm(EquipmentItemForm):
    """Specialized form for Stack Economizer equipment"""
    
    class Meta(EquipmentItemForm.Meta):
        fields = EquipmentItemForm.Meta.fields + ['economizer_type', 'efficiency', 'inlet_temp', 'outlet_temp']
        widgets = {
            **EquipmentItemForm.Meta.widgets,
            'efficiency': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'inlet_temp': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'outlet_temp': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set equipment type to Stack Economizer
        economizer_type = EquipmentType.objects.filter(name__icontains='Economizer').first()
        if economizer_type:
            self.fields['equipment_type'].initial = economizer_type


class MaterialForm(forms.ModelForm):
    """Form for creating/editing materials"""
    
    class Meta:
        model = Material
        fields = ['code', 'name', 'description', 'material_type', 'properties']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'properties': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter material properties as JSON or plain text'}),
        }


class BOMTemplateForm(forms.ModelForm):
    """Form for creating/editing BOM templates"""
    
    class Meta:
        model = BOMTemplate
        fields = ['template_code', 'name', 'equipment_type', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
