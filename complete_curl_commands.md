# Complete Construction Management API - cURL Commands

## Base URL
```
BASE_URL=http://localhost:8000/api/auth
```

## 1. Authentication
```bash
# Register Admin
curl -X POST $BASE_URL/signup/ -H "Content-Type: application/json" -d '{"username": "admin", "email": "admin@site.com", "password": "admin123", "role": "admin", "employee_id": "ADM001"}'

# Login Admin (Save token)
curl -X POST $BASE_URL/login/ -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}'
```

## 2. Users CRUD
```bash
# Create Project Manager
curl -X POST $BASE_URL/users/ -H "Content-Type: application/json" -d '{"username": "pm1", "email": "pm@site.com", "password": "pm123", "role": "project_manager", "employee_id": "PM001"}'

# Create Site Engineer
curl -X POST $BASE_URL/users/ -H "Content-Type: application/json" -d '{"username": "eng1", "email": "eng@site.com", "password": "eng123", "role": "site_engineer", "employee_id": "ENG001"}'

# Create Worker
curl -X POST $BASE_URL/users/ -H "Content-Type: application/json" -d '{"username": "worker1", "email": "worker@site.com", "password": "work123", "role": "worker", "employee_id": "W001"}'

# Get All Users
curl -X GET $BASE_URL/users/

# Update User
curl -X PATCH $BASE_URL/users/2/ -H "Content-Type: application/json" -d '{"phone": "+1234567890", "department": "Engineering"}'
```

## 3. Projects CRUD
```bash
# Create Commercial Project
curl -X POST $BASE_URL/projects/ -H "Content-Type: application/json" -d '{"name": "Office Complex", "project_code": "OC2024", "client": "ABC Corp", "project_manager": 2, "project_type": "commercial", "location": "Downtown", "latitude": 40.7128, "longitude": -74.0060, "start_date": "2024-03-01", "end_date": "2024-12-31", "total_budget": 5000000.00}'

# Create Residential Project
curl -X POST $BASE_URL/projects/ -H "Content-Type: application/json" -d '{"name": "Apartments", "project_code": "APT2024", "client": "XYZ Dev", "project_manager": 2, "project_type": "residential", "location": "Suburb", "start_date": "2024-04-01", "end_date": "2024-11-30", "total_budget": 2500000.00}'

# Get All Projects
curl -X GET $BASE_URL/projects/

# Update Project Status
curl -X PATCH $BASE_URL/projects/1/ -H "Content-Type: application/json" -d '{"status": "active", "actual_start_date": "2024-03-01"}'
```

## 4. Tasks CRUD
```bash
# Create Foundation Task
curl -X POST $BASE_URL/tasks/ -H "Content-Type: application/json" -d '{"project": 1, "task_code": "T001", "title": "Foundation Work", "description": "Excavate and pour foundation", "assigned_to": 3, "created_by": 2, "priority": "high", "start_date": "2024-03-15", "due_date": "2024-03-30", "estimated_hours": 120.00}'

# Create Steel Work Task
curl -X POST $BASE_URL/tasks/ -H "Content-Type: application/json" -d '{"project": 1, "task_code": "T002", "title": "Steel Frame", "description": "Install steel frame", "assigned_to": 3, "created_by": 2, "priority": "medium", "start_date": "2024-04-01", "due_date": "2024-04-30", "estimated_hours": 200.00}'

# Get All Tasks
curl -X GET $BASE_URL/tasks/

# Update Task Progress
curl -X PATCH $BASE_URL/tasks/1/ -H "Content-Type: application/json" -d '{"status": "in_progress", "progress_percentage": 50, "actual_hours": 60.00}'
```

## 5. Vendors CRUD
```bash
# Create Steel Supplier
curl -X POST $BASE_URL/vendors/ -H "Content-Type: application/json" -d '{"name": "Steel Co", "vendor_code": "SC001", "vendor_type": "supplier", "contact_person": "John Steel", "email": "john@steel.com", "phone": "+1987654321", "address": "123 Steel St", "rating": 4.5, "is_approved": true}'

# Create Concrete Supplier
curl -X POST $BASE_URL/vendors/ -H "Content-Type: application/json" -d '{"name": "Concrete Inc", "vendor_code": "CI001", "vendor_type": "supplier", "contact_person": "Jane Concrete", "email": "jane@concrete.com", "phone": "+1555777888", "address": "456 Concrete Ave", "rating": 4.8, "is_approved": true}'

# Get All Vendors
curl -X GET $BASE_URL/vendors/
```

## 6. Material Requests CRUD
```bash
# Create Steel Request
curl -X POST $BASE_URL/material-requests/ -H "Content-Type: application/json" -d '{"request_id": "MR001", "project": 1, "task": 2, "requested_by": 3, "material_description": "Steel beams", "quantity": 50.00, "unit": "pieces", "estimated_cost": 25000.00, "urgency": "high", "required_date": "2024-04-01"}'

# Create Concrete Request
curl -X POST $BASE_URL/material-requests/ -H "Content-Type: application/json" -d '{"request_id": "MR002", "project": 1, "task": 1, "requested_by": 3, "material_description": "Concrete mix", "quantity": 100.00, "unit": "cubic yards", "estimated_cost": 15000.00, "urgency": "high", "required_date": "2024-03-20"}'

# Get All Material Requests
curl -X GET $BASE_URL/material-requests/

# Approve Material Request
curl -X PATCH $BASE_URL/material-requests/1/ -H "Content-Type: application/json" -d '{"status": "approved", "approved_by": 2}'
```

## 7. Purchase Orders CRUD
```bash
# Create Steel PO
curl -X POST $BASE_URL/purchaseorders/ -H "Content-Type: application/json" -d '{"po_number": "PO001", "vendor": 1, "project": 1, "requested_by": 2, "description": "Steel beams", "total_amount": 25000.00, "tax_amount": 2500.00, "order_date": "2024-03-01", "expected_delivery_date": "2024-03-20"}'

# Create Concrete PO
curl -X POST $BASE_URL/purchaseorders/ -H "Content-Type: application/json" -d '{"po_number": "PO002", "vendor": 2, "project": 1, "requested_by": 2, "description": "Concrete mix", "total_amount": 15000.00, "tax_amount": 1500.00, "order_date": "2024-03-05", "expected_delivery_date": "2024-03-18"}'

# Get All Purchase Orders
curl -X GET $BASE_URL/purchaseorders/

# Approve PO
curl -X PATCH $BASE_URL/purchaseorders/1/ -H "Content-Type: application/json" -d '{"status": "approved", "approved_by": 2}'
```

## 8. Budgets CRUD
```bash
# Create Materials Budget
curl -X POST $BASE_URL/budgets/ -H "Content-Type: application/json" -d '{"project": 1, "category": "materials", "description": "Materials budget", "allocated_amount": 2000000.00, "spent_amount": 500000.00, "committed_amount": 800000.00, "fiscal_year": 2024, "created_by": 2}'

# Create Labor Budget
curl -X POST $BASE_URL/budgets/ -H "Content-Type: application/json" -d '{"project": 1, "category": "labor", "description": "Labor budget", "allocated_amount": 2500000.00, "spent_amount": 600000.00, "committed_amount": 1000000.00, "fiscal_year": 2024, "created_by": 2}'

# Get All Budgets
curl -X GET $BASE_URL/budgets/
```

## 9. Equipment CRUD
```bash
# Create Excavator
curl -X POST $BASE_URL/equipment/ -H "Content-Type: application/json" -d '{"equipment_id": "EQ001", "name": "Excavator CAT 320", "category": "Heavy Machinery", "model": "CAT 320", "serial_number": "CAT001", "purchase_cost": 250000.00, "status": "available"}'

# Create Crane
curl -X POST $BASE_URL/equipment/ -H "Content-Type: application/json" -d '{"equipment_id": "EQ002", "name": "Tower Crane", "category": "Lifting", "model": "TC-200", "serial_number": "TC001", "purchase_cost": 500000.00, "status": "available"}'

# Get All Equipment
curl -X GET $BASE_URL/equipment/

# Assign Equipment
curl -X PATCH $BASE_URL/equipment/1/ -H "Content-Type: application/json" -d '{"status": "in_use", "current_project": 1, "assigned_to": 3}'
```

## 10. Safety Incidents CRUD
```bash
# Report Minor Incident
curl -X POST $BASE_URL/incidents/ -H "Content-Type: application/json" -d '{"incident_id": "INC001", "project": 1, "title": "Minor Cut", "description": "Small cut on hand", "severity": "minor", "location_details": "Foundation area", "injured_person": "Worker1", "reported_by": 3}'

# Report Major Incident
curl -X POST $BASE_URL/incidents/ -H "Content-Type: application/json" -d '{"incident_id": "INC002", "project": 1, "title": "Equipment Failure", "description": "Crane malfunction", "severity": "major", "location_details": "Crane area", "reported_by": 3}'

# Get All Incidents
curl -X GET $BASE_URL/incidents/
```

## 11. Quality Inspections CRUD
```bash
# Schedule Foundation Inspection
curl -X POST $BASE_URL/quality-inspections/ -H "Content-Type: application/json" -d '{"inspection_id": "QI001", "project": 1, "task": 1, "inspector": 3, "inspection_type": "Foundation Check", "scheduled_date": "2024-03-25", "checklist_items": "Check concrete strength\nVerify dimensions"}'

# Complete Inspection
curl -X PATCH $BASE_URL/quality-inspections/1/ -H "Content-Type: application/json" -d '{"status": "passed", "actual_date": "2024-03-25", "observations": "All good", "score": 95}'

# Get All Inspections
curl -X GET $BASE_URL/quality-inspections/
```

## 12. Communications CRUD
```bash
# Send Progress Update
curl -X POST $BASE_URL/communications/ -H "Content-Type: application/json" -d '{"sender": 2, "receivers": [1, 3], "project": 1, "task": 1, "message_type": "progress_update", "subject": "Foundation Progress", "message": "Foundation work 50% complete"}'

# Send Safety Alert
curl -X POST $BASE_URL/communications/ -H "Content-Type: application/json" -d '{"sender": 1, "receivers": [2, 3], "project": 1, "message_type": "safety_alert", "subject": "PPE Required", "message": "All workers must wear hard hats"}'

# Get All Communications
curl -X GET $BASE_URL/communications/
```

## 13. Attendance CRUD (Requires Token)
```bash
# Clock In
curl -X POST $BASE_URL/attendance/ -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"project": 1, "check_in_time": "08:00:00", "latitude": 40.7128, "longitude": -74.0060, "notes": "Starting work"}'

# Clock Out
curl -X PATCH $BASE_URL/attendance/1/ -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"check_out_time": "17:00:00"}'

# Get All Attendance
curl -X GET $BASE_URL/attendance/ -H "Authorization: Bearer YOUR_TOKEN"
```

## 14. Invoices CRUD
```bash
# Create Steel Invoice
curl -X POST $BASE_URL/invoices/ -H "Content-Type: application/json" -d '{"invoice_number": "INV001", "vendor": 1, "purchase_order": 1, "project": 1, "description": "Steel delivery", "subtotal": 25000.00, "tax_amount": 2500.00, "total_amount": 27500.00, "invoice_date": "2024-03-20", "due_date": "2024-04-20"}'

# Approve Invoice
curl -X PATCH $BASE_URL/invoices/1/ -H "Content-Type: application/json" -d '{"status": "approved", "approved_by": 2}'

# Get All Invoices
curl -X GET $BASE_URL/invoices/
```

## 15. Documents CRUD
```bash
# Upload Blueprint
curl -X POST $BASE_URL/documents/ -H "Content-Type: application/json" -d '{"project": 1, "task": 1, "document_type": "blueprint", "title": "Foundation Blueprint", "version": "1.0", "description": "Foundation design", "uploaded_by": 2}'

# Get All Documents
curl -X GET $BASE_URL/documents/
```

## Complete Workflow Test
```bash
# 1. Setup users and project
curl -X POST $BASE_URL/signup/ -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123", "role": "admin"}'
curl -X POST $BASE_URL/login/ -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}'
curl -X POST $BASE_URL/projects/ -H "Content-Type: application/json" -d '{"name": "Test Project", "project_code": "TP001", "client": "Test Client", "total_budget": 1000000.00}'

# 2. Create tasks and materials
curl -X POST $BASE_URL/tasks/ -H "Content-Type: application/json" -d '{"project": 1, "task_code": "T001", "title": "Foundation", "estimated_hours": 100}'
curl -X POST $BASE_URL/material-requests/ -H "Content-Type: application/json" -d '{"request_id": "MR001", "project": 1, "material_description": "Concrete", "quantity": 50}'

# 3. Create vendors and purchase orders
curl -X POST $BASE_URL/vendors/ -H "Content-Type: application/json" -d '{"name": "Supplier Co", "vendor_code": "SUP001", "email": "sup@test.com", "phone": "123456789", "address": "Test Address"}'
curl -X POST $BASE_URL/purchaseorders/ -H "Content-Type: application/json" -d '{"po_number": "PO001", "vendor": 1, "project": 1, "total_amount": 10000.00}'

# 4. Test attendance and safety
curl -X POST $BASE_URL/attendance/ -H "Authorization: Bearer TOKEN" -d '{"project": 1, "check_in_time": "08:00:00", "latitude": 40.7128, "longitude": -74.0060}'
curl -X POST $BASE_URL/incidents/ -H "Content-Type: application/json" -d '{"incident_id": "INC001", "project": 1, "title": "Test Incident", "severity": "minor"}'
```