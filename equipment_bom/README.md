# Equipment BOM Management App

This Django application manages Bill of Materials (BOM) for industrial equipment, allowing users to import Excel data, manage equipment items, jobs, and materials.

## Features

- **Excel Import/Export**: Import equipment data from Excel files with multiple sheets
- **Equipment Management**: Track equipment items with specifications and dimensions
- **Job Management**: Organize equipment by projects and jobs
- **Material Tracking**: Manage material specifications and properties
- **BOM Templates**: Create reusable Bill of Materials templates
- **Import Logging**: Track all import activities with detailed logs

## Supported Equipment Types

- Import Heater
- Import Tank
- Pump
- Stack Economizer

## Excel Import Format

The app expects Excel files with specific sheet names matching the equipment types:

### Import Heater Sheet
- Item Number (e.g., 35284-01)
- Description (e.g., HEATER, FAB, 42X12, RM, 316)
- BOM (e.g., 35284-01-000)
- Product Type (e.g., FG FAB, Sub Assy)
- Dimensions (various columns for diameter, height, length, width)

### Import Tank Sheet
- Similar structure to Import Heater
- Tank-specific specifications

### Pump Sheet
- Pump-specific specifications and dimensions

### Stack Economizer Sheet
- Economizer-specific specifications

## Usage

### 1. Access the App
Navigate to the Apps menu in the navbar and select "Equipment BOM"

### 2. Import Excel Data
1. Go to the Import Excel page
2. Select your Excel file (.xlsx or .xls)
3. Choose the equipment type
4. Click "Start Import"

### 3. View and Manage Data
- **Dashboard**: Overview of all equipment, jobs, and recent imports
- **Equipment List**: Browse all equipment items with search and filters
- **Job Management**: View and manage projects
- **Materials**: Browse available materials
- **BOM Templates**: Manage reusable templates
- **Import Logs**: Track all import activities

## Models

### EquipmentType
- Defines the type of equipment (Heater, Tank, Pump, etc.)

### Job
- Represents a project or job number
- Links to equipment items

### Material
- Material specifications with properties
- Supports various material types (316, 304, RM, GP, etc.)

### EquipmentItem
- Main equipment item with specifications
- Links to job, equipment type, and BOM template

### BOMTemplate
- Reusable Bill of Materials templates
- Links to equipment types

### ImportLog
- Tracks all Excel import activities
- Records success/failure and record counts

## Management Commands

### Setup Initial Data
```bash
python manage.py setup_equipment_bom
```
Creates initial equipment types and sample materials.

## URL Structure

- `/equipment/` - Main dashboard
- `/equipment/import/` - Excel import page
- `/equipment/equipment/` - Equipment list
- `/equipment/jobs/` - Job management
- `/equipment/materials/` - Materials list
- `/equipment/templates/` - BOM templates
- `/equipment/logs/` - Import logs

## Excel Import Process

1. **File Validation**: Checks file format and size
2. **Sheet Detection**: Automatically detects relevant sheets
3. **Data Processing**: Parses Excel data and validates structure
4. **Database Creation**: Creates/updates equipment, jobs, and materials
5. **Logging**: Records import results and statistics

## Data Relationships

- Equipment Items belong to Jobs
- Equipment Items have Equipment Types
- Equipment Items can use BOM Templates
- Materials are referenced by Equipment Items
- Import Logs track all import activities

## Admin Interface

All models are available in the Django admin interface for manual management and data review.

## Styling

The app uses DaisyUI components with Tailwind CSS for a modern, responsive interface that matches the main project theme.
