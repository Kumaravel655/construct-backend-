# Construction Management API - cURL Commands

## Base URL
```
http://localhost:8000/api/auth
```

## Authentication Endpoints

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123",
    "role": "site_engineer",
    "contact_info": "123-456-7890"
  }'
```

### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

## CRUD Operations

### Users
```bash
# GET all users
curl -X GET http://localhost:8000/api/auth/users/

# POST create user
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "newpass123", 
    "role": "admin",
    "contact_info": "987-654-3210"
  }'

# GET specific user
curl -X GET http://localhost:8000/api/auth/users/1/

# PUT update user
curl -X PUT http://localhost:8000/api/auth/users/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updateduser",
    "email": "updated@example.com",
    "role": "site_engineer"
  }'

# DELETE user
curl -X DELETE http://localhost:8000/api/auth/users/1/
```

### Projects
```bash
# GET all projects
curl -X GET http://localhost:8000/api/auth/projects/

# POST create project
curl -X POST http://localhost:8000/api/auth/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Construction Project",
    "client": "ABC Corporation", 
    "location": "New York, NY",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "status": "active",
    "start_date": "2024-01-15",
    "end_date": "2024-12-31"
  }'

# GET specific project
curl -X GET http://localhost:8000/api/auth/projects/1/

# PUT update project
curl -X PUT http://localhost:8000/api/auth/projects/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "status": "completed"
  }'
```

### Tasks
```bash
# GET all tasks
curl -X GET http://localhost:8000/api/auth/tasks/

# POST create task
curl -X POST http://localhost:8000/api/auth/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "description": "Install electrical wiring",
    "assigned_to": 1,
    "status": "pending", 
    "priority": "high",
    "due_date": "2024-02-15"
  }'
```

### Attendance (Requires Authentication)
```bash
# GET all attendance (replace YOUR_TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/attendance/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# POST create attendance
curl -X POST http://localhost:8000/api/auth/attendance/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project": 1,
    "hours_worked": 8.5,
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### Vendors
```bash
# GET all vendors
curl -X GET http://localhost:8000/api/auth/vendors/

# POST create vendor
curl -X POST http://localhost:8000/api/auth/vendors/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Supplies",
    "contact": "contact@abcsupplies.com",
    "service_type": "Construction Materials"
  }'
```

### Purchase Orders
```bash
# GET all purchase orders
curl -X GET http://localhost:8000/api/auth/purchaseorders/

# POST create purchase order
curl -X POST http://localhost:8000/api/auth/purchaseorders/ \
  -H "Content-Type: application/json" \
  -d '{
    "vendor": 1,
    "project": 1, 
    "amount": 15000.00,
    "status": "pending"
  }'
```

### Budgets
```bash
# GET all budgets
curl -X GET http://localhost:8000/api/auth/budgets/

# POST create budget
curl -X POST http://localhost:8000/api/auth/budgets/ \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "amount_allocated": 500000.00,
    "amount_spent": 125000.00,
    "fiscal_year": 2024
  }'
```

### Equipment
```bash
# GET all equipment
curl -X GET http://localhost:8000/api/auth/equipment/

# POST create equipment
curl -X POST http://localhost:8000/api/auth/equipment/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Excavator CAT 320",
    "status": "available",
    "assigned_to": 1
  }'
```

### Safety Incidents
```bash
# GET all incidents
curl -X GET http://localhost:8000/api/auth/incidents/

# POST create incident
curl -X POST http://localhost:8000/api/auth/incidents/ \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "description": "Minor injury on site",
    "reported_by": 1,
    "date": "2024-01-20",
    "status": "reported"
  }'
```

### Communications
```bash
# GET all communications
curl -X GET http://localhost:8000/api/auth/communications/

# POST create communication
curl -X POST http://localhost:8000/api/auth/communications/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender": 1,
    "receiver": 2,
    "project": 1,
    "message": "Project update: Phase 1 completed"
  }'
```

## Testing Steps

1. Start your Django server: `python manage.py runserver`
2. First register a user using the signup endpoint
3. Login to get authentication token (if using token auth)
4. Use the token in Authorization header for protected endpoints
5. Test CRUD operations for each model

## Notes
- Replace `YOUR_TOKEN` with actual authentication token
- Adjust IDs (1, 2, etc.) based on your actual data
- Some endpoints require authentication (marked above)
- All POST/PUT requests need Content-Type: application/json header