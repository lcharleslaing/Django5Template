import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import (
    EquipmentType, Job, Material, BOMTemplate, EquipmentItem, 
    BOMComponent, Specification, ImportLog
)
import logging

logger = logging.getLogger(__name__)

class ExcelBOMImporter:
    """Excel importer for BOM data with multiple tabs"""
    
    def __init__(self, file_path, user, equipment_type_name):
        self.file_path = file_path
        self.user = user
        self.equipment_type_name = equipment_type_name
        self.import_log = None
        self.errors = []
        self.records_processed = 0
        self.records_created = 0
        self.records_updated = 0
        
    def import_excel(self):
        """Main import method"""
        try:
            # Create import log
            equipment_type, _ = EquipmentType.objects.get_or_create(
                name=self.equipment_type_name,
                defaults={'code': self.equipment_type_name[:3].upper()}
            )
            
            self.import_log = ImportLog.objects.create(
                file_name=self.file_path.split('/')[-1],
                imported_by=self.user,
                equipment_type=equipment_type,
                status='in_progress'
            )
            
            # Read Excel file
            excel_file = pd.ExcelFile(self.file_path)
            
            # Process each sheet based on equipment type
            if self.equipment_type_name == 'Import Heater':
                self._process_heater_sheet(excel_file)
            elif self.equipment_type_name == 'Import Tank':
                self._process_tank_sheet(excel_file)
            elif self.equipment_type_name == 'Pump':
                self._process_pump_sheet(excel_file)
            elif self.equipment_type_name == 'Stack Economizer':
                self._process_economizer_sheet(excel_file)
            else:
                raise ValueError(f"Unknown equipment type: {self.equipment_type_name}")
            
            # Update import log
            self.import_log.records_processed = self.records_processed
            self.import_log.records_created = self.records_created
            self.import_log.records_updated = self.records_updated
            self.import_log.errors = self.errors
            self.import_log.status = 'completed' if not self.errors else 'partial'
            self.import_log.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            if self.import_log:
                self.import_log.status = 'failed'
                self.import_log.errors.append(str(e))
                self.import_log.save()
            return False
    
    def _process_heater_sheet(self, excel_file):
        """Process Import Heater sheet"""
        df = pd.read_excel(excel_file, sheet_name='Import Heater')
        
        # Clean up the dataframe
        df = self._clean_dataframe(df)
        
        # Extract job information
        job_number = self._extract_job_number(df)
        job, _ = Job.objects.get_or_create(
            job_number=job_number,
            defaults={
                'description': f'Heater Project {job_number}',
                'created_by': self.user
            }
        )
        
        # Get or create equipment type
        equipment_type, _ = EquipmentType.objects.get_or_create(
            name='Import Heater',
            defaults={'code': 'HEA', 'description': 'Import Heater Equipment'}
        )
        
        # Process each row
        for index, row in df.iterrows():
            if pd.isna(row.get('Item Number')) or pd.isna(row.get('Description')):
                continue
                
            self.records_processed += 1
            
            try:
                with transaction.atomic():
                    # Create or update equipment item
                    equipment_item, created = self._create_heater_item(row, job, equipment_type)
                    
                    if created:
                        self.records_created += 1
                    else:
                        self.records_updated += 1
                    
                    # Create specifications
                    self._create_heater_specifications(row, equipment_item)
                    
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _process_tank_sheet(self, excel_file):
        """Process Import Tank sheet"""
        df = pd.read_excel(excel_file, sheet_name='Import Tank')
        df = self._clean_dataframe(df)
        
        job_number = self._extract_job_number(df)
        job, _ = Job.objects.get_or_create(
            job_number=job_number,
            defaults={
                'description': f'Tank Project {job_number}',
                'created_by': self.user
            }
        )
        
        equipment_type, _ = EquipmentType.objects.get_or_create(
            name='Import Tank',
            defaults={'code': 'TNK', 'description': 'Import Tank Equipment'}
        )
        
        for index, row in df.iterrows():
            if pd.isna(row.get('Item Number')) or pd.isna(row.get('Description')):
                continue
                
            self.records_processed += 1
            
            try:
                with transaction.atomic():
                    equipment_item, created = self._create_tank_item(row, job, equipment_type)
                    
                    if created:
                        self.records_created += 1
                    else:
                        self.records_updated += 1
                        
                    self._create_tank_specifications(row, equipment_item)
                    
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _process_pump_sheet(self, excel_file):
        """Process Pump sheet"""
        df = pd.read_excel(excel_file, sheet_name='Pump')
        df = self._clean_dataframe(df)
        
        job_number = self._extract_job_number(df)
        job, _ = Job.objects.get_or_create(
            job_number=job_number,
            defaults={
                'description': f'Pump Project {job_number}',
                'created_by': self.user
            }
        )
        
        equipment_type, _ = EquipmentType.objects.get_or_create(
            name='Pump',
            defaults={'code': 'PMP', 'description': 'Pump Equipment'}
        )
        
        for index, row in df.iterrows():
            if pd.isna(row.get('Item Number')) or pd.isna(row.get('Description')):
                continue
                
            self.records_processed += 1
            
            try:
                with transaction.atomic():
                    equipment_item, created = self._create_pump_item(row, job, equipment_type)
                    
                    if created:
                        self.records_created += 1
                    else:
                        self.records_updated += 1
                        
                    self._create_pump_specifications(row, equipment_item)
                    
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _process_economizer_sheet(self, excel_file):
        """Process Stack Economizer sheet"""
        df = pd.read_excel(excel_file, sheet_name='Stack Economizer')
        df = self._clean_dataframe(df)
        
        job_number = self._extract_job_number(df)
        job, _ = Job.objects.get_or_create(
            job_number=job_number,
            defaults={
                'description': f'Economizer Project {job_number}',
                'created_by': self.user
            }
        )
        
        equipment_type, _ = EquipmentType.objects.get_or_create(
            name='Stack Economizer',
            defaults={'code': 'ECO', 'description': 'Stack Economizer Equipment'}
        )
        
        for index, row in df.iterrows():
            if pd.isna(row.get('Item Number')) or pd.isna(row.get('Description')):
                continue
                
            self.records_processed += 1
            
            try:
                with transaction.atomic():
                    equipment_item, created = self._create_economizer_item(row, job, equipment_type)
                    
                    if created:
                        self.records_created += 1
                    else:
                        self.records_updated += 1
                        
                    self._create_economizer_specifications(row, equipment_item)
                    
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _clean_dataframe(self, df):
        """Clean and standardize dataframe"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Forward fill some columns for better data structure
        df = df.fillna(method='ffill', limit=1)
        
        return df
    
    def _extract_job_number(self, df):
        """Extract job number from dataframe"""
        # Look for job number in various columns
        for col in df.columns:
            if 'Job #' in str(col):
                values = df[col].dropna()
                if not values.empty:
                    return str(values.iloc[0])
        
        # Fallback: look for pattern like 35284
        for col in df.columns:
            values = df[col].dropna()
            for value in values:
                if isinstance(value, (int, float)) and 10000 <= value <= 99999:
                    return str(int(value))
        
        return "UNKNOWN"
    
    def _create_heater_item(self, row, job, equipment_type):
        """Create heater equipment item from row data"""
        item_number = str(row.get('Item Number', ''))
        description = str(row.get('Description', ''))
        
        # Determine product type
        product_type = 'Item'
        if 'Sub Assy' in str(row.get('Product Type', '')):
            product_type = 'Sub Assy'
        elif 'FG FAB' in str(row.get('Product Type', '')):
            product_type = 'FG FAB'
        
        # Determine supply type
        supply_type = 'Item'
        if 'Pegged Supply' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Pegged Supply'
        elif 'Phantom' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Phantom'
        
        # Extract dimensions
        diameter = self._safe_float(row.get(304))
        height = self._safe_float(row.get(30))
        length = self._safe_float(row.get(12))
        width = self._safe_float(row.get(9.5))
        thickness = self._safe_float(row.get(7))
        
        # Extract position
        position = 'CENTER'
        if 'LEFT' in str(row.get('LEFT', '')):
            position = 'LEFT'
        elif 'RIGHT' in str(row.get('RIGHT', '')):
            position = 'RIGHT'
        
        # Get or create material
        material_code = str(row.get('GP', ''))
        if material_code and material_code != 'nan':
            material, _ = Material.objects.get_or_create(
                code=material_code,
                defaults={
                    'name': f'{material_code} Material',
                    'material_type': material_code
                }
            )
        else:
            material = None
        
        # Create or update equipment item
        equipment_item, created = EquipmentItem.objects.update_or_create(
            item_number=item_number,
            defaults={
                'description': description,
                'job': job,
                'equipment_type': equipment_type,
                'product_type': product_type,
                'supply_type': supply_type,
                'diameter': diameter,
                'height': height,
                'length': length,
                'width': width,
                'thickness': thickness,
                'position': position,
                'primary_material': material,
                'created_by': self.user,
            }
        )
        
        return equipment_item, created
    
    def _create_tank_item(self, row, job, equipment_type):
        """Create tank equipment item from row data"""
        item_number = str(row.get('Item Number', ''))
        description = str(row.get('Description', ''))
        
        product_type = 'Item'
        if 'Sub Assy' in str(row.get('Product Type', '')):
            product_type = 'Sub Assy'
        
        supply_type = 'Item'
        if 'Phantom' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Phantom'
        
        # Extract dimensions
        diameter = self._safe_float(row.get(304))
        height = self._safe_float(row.get(48))
        length = self._safe_float(row.get(3))
        width = self._safe_float(row.get(36.25))
        
        # Get material
        material_code = str(row.get('HW', ''))
        if material_code and material_code != 'nan':
            material, _ = Material.objects.get_or_create(
                code=material_code,
                defaults={
                    'name': f'{material_code} Material',
                    'material_type': material_code
                }
            )
        else:
            material = None
        
        equipment_item, created = EquipmentItem.objects.update_or_create(
            item_number=item_number,
            defaults={
                'description': description,
                'job': job,
                'equipment_type': equipment_type,
                'product_type': product_type,
                'supply_type': supply_type,
                'diameter': diameter,
                'height': height,
                'length': length,
                'width': width,
                'primary_material': material,
                'created_by': self.user,
            }
        )
        
        return equipment_item, created
    
    def _create_pump_item(self, row, job, equipment_type):
        """Create pump equipment item from row data"""
        item_number = str(row.get('Item Number', ''))
        description = str(row.get('Description', ''))
        
        product_type = 'Item'
        if 'Sub Assy' in str(row.get('Product Type', '')):
            product_type = 'Sub Assy'
        
        supply_type = 'Item'
        if 'Phantom' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Phantom'
        
        # Extract dimensions
        diameter = self._safe_float(row.get(304))
        height = self._safe_float(row.get(30))
        length = self._safe_float(row.get(12))
        width = self._safe_float(row.get(9.5))
        thickness = self._safe_float(row.get(7))
        
        # Get material
        material_code = str(row.get('GP', ''))
        if material_code and material_code != 'nan':
            material, _ = Material.objects.get_or_create(
                code=material_code,
                defaults={
                    'name': f'{material_code} Material',
                    'material_type': material_code
                }
            )
        else:
            material = None
        
        equipment_item, created = EquipmentItem.objects.update_or_create(
            item_number=item_number,
            defaults={
                'description': description,
                'job': job,
                'equipment_type': equipment_type,
                'product_type': product_type,
                'supply_type': supply_type,
                'diameter': diameter,
                'height': height,
                'length': length,
                'width': width,
                'thickness': thickness,
                'primary_material': material,
                'created_by': self.user,
            }
        )
        
        return equipment_item, created
    
    def _create_economizer_item(self, row, job, equipment_type):
        """Create economizer equipment item from row data"""
        item_number = str(row.get('Item Number', ''))
        description = str(row.get('Description', ''))
        
        product_type = 'Item'
        if 'Sub Assy' in str(row.get('Product Type', '')):
            product_type = 'Sub Assy'
        elif 'FG FAB' in str(row.get('Product Type', '')):
            product_type = 'FG FAB'
        
        supply_type = 'Item'
        if 'Pegged Supply' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Pegged Supply'
        elif 'Phantom' in str(row.get('Unnamed: 6', '')):
            supply_type = 'Phantom'
        
        # Extract dimensions
        diameter = self._safe_float(row.get(304))
        height = self._safe_float(row.get(30))
        length = self._safe_float(row.get(12))
        width = self._safe_float(row.get(9.5))
        thickness = self._safe_float(row.get(7))
        
        # Extract position
        position = 'CENTER'
        if 'LEFT' in str(row.get('LEFT', '')):
            position = 'LEFT'
        elif 'RIGHT' in str(row.get('RIGHT', '')):
            position = 'RIGHT'
        
        # Get material
        material_code = str(row.get('GP', ''))
        if material_code and material_code != 'nan':
            material, _ = Material.objects.get_or_create(
                code=material_code,
                defaults={
                    'name': f'{material_code} Material',
                    'material_type': material_code
                }
            )
        else:
            material = None
        
        equipment_item, created = EquipmentItem.objects.update_or_create(
            item_number=item_number,
            defaults={
                'description': description,
                'job': job,
                'equipment_type': equipment_type,
                'product_type': product_type,
                'supply_type': supply_type,
                'diameter': diameter,
                'height': height,
                'length': length,
                'width': width,
                'thickness': thickness,
                'position': position,
                'primary_material': material,
                'created_by': self.user,
            }
        )
        
        return equipment_item, created
    
    def _create_heater_specifications(self, row, equipment_item):
        """Create heater specifications from row data"""
        # Extract various specifications
        specs = [
            ('Heater Diameter', str(row.get(42, '')),
             'Heater Diameter specification'),
            ('Heater Height', str(row.get(12, '')),
             'Heater Height specification'),
            ('Stack Diameter', str(row.get(18, '')),
             'Stack Diameter specification'),
            ('Gas Train Size', str(row.get(2, '')),
             'Gas Train Size specification'),
            ('Gas Train Mount', str(row.get('FM', '')),
             'Gas Train Mount specification'),
            ('Heater Model', str(row.get('RM', '')),
             'Heater Model specification'),
            ('Flange Inlet', str(row.get(2, '')),
             'Flange Inlet specification'),
        ]
        
        for spec_type, value, description in specs:
            if value and value != 'nan':
                Specification.objects.get_or_create(
                    equipment_item=equipment_item,
                    spec_type=spec_type,
                    defaults={
                        'value': value,
                        'description': description
                    }
                )
    
    def _create_tank_specifications(self, row, equipment_item):
        """Create tank specifications from row data"""
        specs = [
            ('Tank Diameter', str(row.get(72, '')),
             'Tank Diameter specification'),
            ('Tank Height', str(row.get(12, '')),
             'Tank Height specification'),
            ('Type', str(row.get('HW', '')),
             'Tank Type specification'),
        ]
        
        for spec_type, value, description in specs:
            if value and value != 'nan':
                Specification.objects.get_or_create(
                    equipment_item=equipment_item,
                    spec_type=spec_type,
                    defaults={
                        'value': value,
                        'description': description
                    }
                )
    
    def _create_pump_specifications(self, row, equipment_item):
        """Create pump specifications from row data"""
        specs = [
            ('HP', str(row.get(2, '')),
             'Pump Horsepower specification'),
            ('Type', str(row.get('HW', '')),
             'Pump Type specification'),
        ]
        
        for spec_type, value, description in specs:
            if value and value != 'nan':
                Specification.objects.get_or_create(
                    equipment_item=equipment_item,
                    spec_type=spec_type,
                    defaults={
                        'value': value,
                        'description': description
                    }
                )
    
    def _create_economizer_specifications(self, row, equipment_item):
        """Create economizer specifications from row data"""
        specs = [
            ('Stack Diameter', str(row.get(18, '')),
             'Stack Diameter specification'),
            ('Gas Train Size', str(row.get(2, '')),
             'Gas Train Size specification'),
            ('Gas Train Mount', str(row.get('FM', '')),
             'Gas Train Mount specification'),
        ]
        
        for spec_type, value, description in specs:
            if value and value != 'nan':
                Specification.objects.get_or_create(
                    equipment_item=equipment_item,
                    spec_type=spec_type,
                    defaults={
                        'value': value,
                        'description': description
                    }
                )
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
