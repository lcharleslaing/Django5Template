import os
import pandas as pd
from django.conf import settings
from .models import EquipmentType

class ExcelTemplateDiscovery:
    """Utility class for discovering and managing Excel templates"""
    
    def __init__(self):
        self.template_dir = os.path.join(settings.BASE_DIR, 'equipment_bom', 'excel_templates')
        self.supported_types = [
            'Import Heater',
            'Import Tank', 
            'Pump',
            'Stack Economizer'
        ]
    
    def get_available_templates(self):
        """Get list of available Excel templates"""
        templates = []
        
        if not os.path.exists(self.template_dir):
            return templates
            
        for filename in os.listdir(self.template_dir):
            if filename.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(self.template_dir, filename)
                template_info = self._analyze_template(file_path)
                if template_info:
                    templates.append(template_info)
        
        return templates
    
    def _analyze_template(self, file_path):
        """Analyze an Excel file to determine its type and contents"""
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            # Find matching equipment type
            equipment_type = None
            for sheet_name in sheet_names:
                if sheet_name in self.supported_types:
                    equipment_type = sheet_name
                    break
            
            if not equipment_type:
                return None
            
            # Get basic file info
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            return {
                'filename': os.path.basename(file_path),
                'file_path': file_path,
                'equipment_type': equipment_type,
                'sheet_names': sheet_names,
                'file_size_mb': file_size_mb,
                'last_modified': os.path.getmtime(file_path)
            }
            
        except Exception as e:
            print(f"Error analyzing template {file_path}: {e}")
            return None
    
    def validate_template(self, file_path, equipment_type):
        """Validate that an Excel template has the required structure"""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            if equipment_type not in excel_file.sheet_names:
                return False, f"Missing required sheet: {equipment_type}"
            
            # Read the sheet and check for required columns
            df = pd.read_excel(excel_file, sheet_name=equipment_type)
            required_columns = ['Item Number', 'Description']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Missing required columns: {missing_columns}"
            
            return True, "Template is valid"
            
        except Exception as e:
            return False, f"Error validating template: {e}"
    
    def get_template_preview(self, file_path, equipment_type, rows=5):
        """Get a preview of the template data"""
        try:
            excel_file = pd.ExcelFile(file_path)
            df = pd.read_excel(excel_file, sheet_name=equipment_type)
            
            # Clean up the dataframe
            df = df.dropna(how='all')  # Remove completely empty rows
            df = df.fillna(method='ffill', limit=1)  # Forward fill some columns
            
            return {
                'columns': list(df.columns),
                'preview_data': df.head(rows).to_dict('records'),
                'total_rows': len(df)
            }
            
        except Exception as e:
            return None
