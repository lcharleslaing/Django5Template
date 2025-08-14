from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from equipment_bom.models import EquipmentType, Material


class Command(BaseCommand):
    help = 'Set up initial equipment types and materials for Equipment BOM app'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Equipment BOM initial data...')
        
        # Create equipment types
        equipment_types = [
            'Import Heater',
            'Import Tank', 
            'Pump',
            'Stack Economizer'
        ]
        
        for type_name in equipment_types:
            # Generate a code from the name
            code = type_name.replace(' ', '').upper()[:10]
            equipment_type, created = EquipmentType.objects.get_or_create(
                name=type_name,
                defaults={
                    'description': f'{type_name} equipment type',
                    'code': code
                }
            )
            if created:
                self.stdout.write(f'Created equipment type: {type_name}')
            else:
                self.stdout.write(f'Equipment type already exists: {type_name}')
        
        # Create some sample materials
        materials = [
            ('316', '316 Stainless Steel', '316', 'High-grade stainless steel for corrosive environments'),
            ('304', '304 Stainless Steel', '304', 'Standard stainless steel for general use'),
            ('RM', 'RM Material', 'RM', 'Standard RM material for general use'),
            ('GP', 'GP Material', 'GP', 'Standard GP material for general use'),
        ]
        
        for code, name, material_type, description in materials:
            material, created = Material.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'material_type': material_type,
                    'description': description,
                    'properties': {}
                }
            )
            if created:
                self.stdout.write(f'Created material: {code} - {name}')
            else:
                self.stdout.write(f'Material already exists: {code} - {name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up Equipment BOM initial data!')
        )
