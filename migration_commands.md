# Database Migration Commands

## Important: Run these commands to update your database with the enhanced models

### 1. Create migrations for the model changes
```bash
python manage.py makemigrations core
```

### 2. Apply the migrations
```bash
python manage.py migrate
```

### 3. Create a superuser (if not already created)
```bash
python manage.py createsuperuser
```

### 4. Start the development server
```bash
python manage.py runserver
```

## Model Changes Summary

### Enhanced User Model
- Added: `phone`, `employee_id`, `department`, `hire_date`, `is_active_employee`
- Expanded roles: project_manager, foreman, worker, safety_officer, quality_inspector

### Enhanced Project Model
- Added: `project_code`, `project_manager`, `project_type`, `description`, `actual_start_date`, `actual_end_date`, `total_budget`, `created_at`, `updated_at`
- Added progress calculation method

### Enhanced Task Model
- Added: `task_code`, `title`, `created_by`, `start_date`, `actual_start_date`, `actual_completion_date`, `estimated_hours`, `actual_hours`, `progress_percentage`, `dependencies`
- Better status and priority choices

### Enhanced Attendance Model
- Added: `check_in_time`, `check_out_time`, `overtime_hours`, `notes`, `approved_by`
- Added unique constraint for user/project/date

### Enhanced Document Model
- Added: `task`, `document_type`, `title`, `file_path`, `description`, `is_active`
- Better document type categorization

### Enhanced Vendor Model
- Added: `vendor_code`, `vendor_type`, `contact_person`, `email`, `phone`, `address`, `tax_id`, `rating`, `is_approved`, `created_at`

### Enhanced Purchase Order Model
- Added: `po_number`, `requested_by`, `approved_by`, `description`, `tax_amount`, `order_date`, `expected_delivery_date`, `actual_delivery_date`, `created_at`

### Enhanced Budget Model
- Added: `category`, `description`, `spent_amount`, `committed_amount`, `created_by`, `created_at`
- Added remaining_amount property

### Enhanced Invoice Model
- Added: `invoice_number`, `vendor`, `purchase_order`, `description`, `subtotal`, `tax_amount`, `invoice_date`, `paid_date`, `approved_by`, `created_at`

### Enhanced Equipment Model
- Added: `equipment_id`, `category`, `model`, `serial_number`, `purchase_date`, `purchase_cost`, `current_project`, `last_maintenance_date`, `next_maintenance_date`, `location`

### Enhanced Safety Incident Model
- Added: `incident_id`, `title`, `severity`, `location_details`, `injured_person`, `investigated_by`, `incident_date`, `reported_date`, `corrective_actions`

### Enhanced Communication Model
- Changed: `receiver` to `receivers` (ManyToMany), added `task`, `message_type`, `subject`, `is_read`

### New Models Added
- **MaterialRequest**: For managing material requests and approvals
- **QualityInspection**: For quality control and inspections

## Troubleshooting

### If you get migration conflicts:
```bash
# Reset migrations (WARNING: This will lose data)
python manage.py migrate core zero
rm core/migrations/0*.py
python manage.py makemigrations core
python manage.py migrate
```

### If you need to preserve existing data:
1. Backup your database first
2. Run migrations step by step
3. Manually update existing records through Django admin or shell

### Check migration status:
```bash
python manage.py showmigrations
```

### Run Django shell to test models:
```bash
python manage.py shell
```

Then in the shell:
```python
from core.models import *
# Test creating objects
user = User.objects.create_user(username='test', password='test123', role='project_manager')
project = Project.objects.create(name='Test Project', project_code='TP001', client='Test Client', start_date='2024-01-01', end_date='2024-12-31')
```