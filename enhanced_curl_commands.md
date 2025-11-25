# Enhanced Construction Management API - cURL Commands

## Base URL
```
http://localhost:8000/api/auth
```

## Authentication Endpoints

### Register User (Enhanced)
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@construction.com",
    "password": "secure123",
    "role": "site_engineer",
    "phone": "+1234567890",
    "employee_id": "EMP001",
    "department": "Engineering"
  }'
```

### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123"
  }'
```

## Enhanced Project Management

### Create Project (Enhanced)
```bash
curl -X POST http://localhost:8000/api/auth/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Office Complex",
    "project_code": "DOC2024",
    "client": "ABC Corporation",
    "project_manager": 1,
    "project_type": "commercial",
    "description": "50-story office building with underground parking",
    "location": "Downtown, New York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "status": "planning",
    "start_date": "2024-03-01",
    "end_date": "2025-12-31",
    "total_budget": 50000000.00
  }'
```

### Get Project Progress
```bash
curl -X GET http://localhost:8000/api/auth/projects/1/
```

## Enhanced Task Management

### Create Task (Enhanced)
```bash
curl -X POST http://localhost:8000/api/auth/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "task_code": "T001",
    "title": "Foundation Excavation",
    "description": "Excavate foundation area according to blueprints",
    "assigned_to": 2,
    "created_by": 1,
    "status": "not_started",
    "priority": "high",
    "start_date": "2024-03-15",
    "due_date": "2024-03-30",
    "estimated_hours": 120.00
  }'
```

### Update Task Progress
```bash
curl -X PATCH http://localhost:8000/api/auth/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "progress_percentage": 25,
    "actual_start_date": "2024-03-15",
    "actual_hours": 30.00
  }'
```

## Vendor Management (Enhanced)

### Create Vendor
```bash
curl -X POST http://localhost:8000/api/auth/vendors/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Steel Supply Co.",
    "vendor_code": "SSC001",
    "vendor_type": "supplier",
    "contact_person": "Mike Johnson",
    "email": "mike@steelsupply.com",
    "phone": "+1987654321",
    "address": "123 Industrial Ave, Steel City",
    "tax_id": "TAX123456",
    "rating": 4.5,
    "is_approved": true
  }'
```

## Purchase Order Management (Enhanced)

### Create Purchase Order
```bash
curl -X POST http://localhost:8000/api/auth/purchaseorders/ \
  -H "Content-Type: application/json" \
  -d '{
    "po_number": "PO2024001",
    "vendor": 1,
    "project": 1,
    "requested_by": 1,
    "description": "Steel beams for foundation",
    "total_amount": 25000.00,
    "tax_amount": 2500.00,
    "status": "draft",
    "order_date": "2024-03-01",
    "expected_delivery_date": "2024-03-20"
  }'
```

### Approve Purchase Order
```bash
curl -X PATCH http://localhost:8000/api/auth/purchaseorders/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_by": 1
  }'
```

## Budget Management (Enhanced)

### Create Budget by Category
```bash
curl -X POST http://localhost:8000/api/auth/budgets/ \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "category": "materials",
    "description": "Construction materials budget",
    "allocated_amount": 15000000.00,
    "spent_amount": 2500000.00,
    "committed_amount": 5000000.00,
    "fiscal_year": 2024,
    "created_by": 1
  }'
```

## Equipment Management (Enhanced)

### Create Equipment
```bash
curl -X POST http://localhost:8000/api/auth/equipment/ \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ001",
    "name": "Caterpillar 320 Excavator",
    "category": "Heavy Machinery",
    "model": "CAT 320",
    "serial_number": "CAT320-2024-001",
    "purchase_date": "2024-01-15",
    "purchase_cost": 250000.00,
    "status": "available",
    "location": "Equipment Yard A"
  }'
```

### Assign Equipment to Project
```bash
curl -X PATCH http://localhost:8000/api/auth/equipment/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_use",
    "current_project": 1,
    "assigned_to": 2
  }'
```

## Safety Incident Management (Enhanced)

### Report Safety Incident
```bash
curl -X POST http://localhost:8000/api/auth/incidents/ \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC2024001",
    "project": 1,
    "title": "Minor Cut on Hand",
    "description": "Worker sustained minor cut while handling steel beam",
    "severity": "minor",
    "location_details": "Foundation area, Grid A-3",
    "injured_person": "John Smith",
    "reported_by": 1,
    "incident_date": "2024-03-15T14:30:00Z",
    "status": "reported"
  }'
```

### Update Incident Investigation
```bash
curl -X PATCH http://localhost:8000/api/auth/incidents/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "investigating",
    "investigated_by": 3,
    "corrective_actions": "Provide additional safety gloves and training"
  }'
```

## Material Request Management (New)

### Create Material Request
```bash
curl -X POST http://localhost:8000/api/auth/material-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "MR2024001",
    "project": 1,
    "task": 1,
    "requested_by": 2,
    "material_description": "Concrete mix for foundation",
    "quantity": 500.00,
    "unit": "cubic yards",
    "estimated_cost": 15000.00,
    "urgency": "high",
    "required_date": "2024-03-20"
  }'
```

### Approve Material Request
```bash
curl -X PATCH http://localhost:8000/api/auth/material-requests/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_by": 1
  }'
```

## Quality Inspection Management (New)

### Schedule Quality Inspection
```bash
curl -X POST http://localhost:8000/api/auth/quality-inspections/ \
  -H "Content-Type: application/json" \
  -d '{
    "inspection_id": "QI2024001",
    "project": 1,
    "task": 1,
    "inspector": 4,
    "inspection_type": "Foundation Quality Check",
    "scheduled_date": "2024-03-25",
    "checklist_items": "1. Check concrete strength\n2. Verify rebar placement\n3. Measure dimensions"
  }'
```

### Complete Quality Inspection
```bash
curl -X PATCH http://localhost:8000/api/auth/quality-inspections/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "passed",
    "actual_date": "2024-03-25",
    "observations": "All measurements within tolerance",
    "score": 95,
    "recommendations": "Excellent work quality"
  }'
```

## Enhanced Communication

### Send Project Communication
```bash
curl -X POST http://localhost:8000/api/auth/communications/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender": 1,
    "receivers": [2, 3, 4],
    "project": 1,
    "task": 1,
    "message_type": "progress_update",
    "subject": "Foundation Work Progress Update",
    "message": "Foundation excavation is 50% complete. On track for scheduled completion."
  }'
```

## Enhanced Attendance (Geo-verified)

### Clock In with Location
```bash
curl -X POST http://localhost:8000/api/auth/attendance/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project": 1,
    "check_in_time": "08:00:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "notes": "Starting foundation work"
  }'
```

### Clock Out
```bash
curl -X PATCH http://localhost:8000/api/auth/attendance/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "check_out_time": "17:00:00",
    "hours_worked": 8.5,
    "overtime_hours": 0.5
  }'
```

## Enhanced Invoice Management

### Create Invoice
```bash
curl -X POST http://localhost:8000/api/auth/invoices/ \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV2024001",
    "vendor": 1,
    "purchase_order": 1,
    "project": 1,
    "description": "Steel beams delivery",
    "subtotal": 25000.00,
    "tax_amount": 2500.00,
    "total_amount": 27500.00,
    "invoice_date": "2024-03-20",
    "due_date": "2024-04-20"
  }'
```

## Workflow Testing Sequence

### 1. Complete Project Setup
```bash
# Create project manager
curl -X POST http://localhost:8000/api/auth/signup/ -H "Content-Type: application/json" -d '{"username": "pm_john", "password": "secure123", "role": "project_manager", "employee_id": "PM001"}'

# Create project
curl -X POST http://localhost:8000/api/auth/projects/ -H "Content-Type: application/json" -d '{"name": "Test Project", "project_code": "TP001", "client": "Test Client", "project_manager": 1, "project_type": "commercial", "start_date": "2024-03-01", "end_date": "2024-12-31", "total_budget": 1000000.00}'

# Create tasks
curl -X POST http://localhost:8000/api/auth/tasks/ -H "Content-Type: application/json" -d '{"project": 1, "task_code": "T001", "title": "Site Preparation", "description": "Clear and prepare construction site", "assigned_to": 1, "start_date": "2024-03-01", "due_date": "2024-03-15", "estimated_hours": 80}'
```

### 2. Material and Vendor Management
```bash
# Create vendor
curl -X POST http://localhost:8000/api/auth/vendors/ -H "Content-Type: application/json" -d '{"name": "ABC Supplies", "vendor_code": "ABC001", "vendor_type": "supplier", "contact_person": "Jane Doe", "email": "jane@abc.com", "phone": "123-456-7890", "address": "123 Supply St"}'

# Create material request
curl -X POST http://localhost:8000/api/auth/material-requests/ -H "Content-Type: application/json" -d '{"request_id": "MR001", "project": 1, "requested_by": 1, "material_description": "Concrete blocks", "quantity": 100, "unit": "pieces", "estimated_cost": 5000, "required_date": "2024-03-10"}'

# Create purchase order
curl -X POST http://localhost:8000/api/auth/purchaseorders/ -H "Content-Type: application/json" -d '{"po_number": "PO001", "vendor": 1, "project": 1, "requested_by": 1, "description": "Concrete blocks", "total_amount": 5000, "order_date": "2024-03-05", "expected_delivery_date": "2024-03-10"}'
```

## Notes
- Replace `YOUR_TOKEN` with actual JWT token from login
- Adjust IDs based on your actual data
- All datetime fields use ISO format
- Geographic coordinates should be actual project location for attendance verification
- Use proper role-based access for different endpoints