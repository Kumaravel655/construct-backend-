# 🏗️ BEEMJI ENTERPRISE — Full Implementation Plan
### Civil Construction & Government Projects | Construction Management System

> **Purpose:** This document bridges the existing backend (construct-backend) with the full organizational structure of Beemji Enterprise as defined in the Corporate Organization Chart. It covers every new API module, frontend page, role-based access, and architectural decision needed to make the system production-ready.

---

## 📌 TABLE OF CONTENTS

1. [Gap Analysis — Existing vs Required](#1-gap-analysis)
2. [System Architecture Overview](#2-system-architecture)
3. [Role & Permission Matrix](#3-role--permission-matrix)
4. [Backend — New & Extended API Modules](#4-backend--new--extended-api-modules)
5. [Frontend Pages — Complete Plan](#5-frontend-pages--complete-plan)
6. [Database Schema Extensions](#6-database-schema-extensions)
7. [Running the Application](#7-running-the-application)
8. [Folder Structure (Full)](#8-folder-structure-full)
9. [Deployment & Production Hardening](#9-deployment--production-hardening)

---

## 1. GAP ANALYSIS

### ✅ Already Implemented (from existing backend)

| Module | Status |
|---|---|
| JWT Auth / User CRUD | ✅ Done |
| Project Management (lifecycle, budget, GPS) | ✅ Done |
| Task Management (dependencies, progress) | ✅ Done |
| Attendance + GPS check-in/check-out | ✅ Done |
| Document Management | ✅ Done |
| Vendor & Procurement (PO, material request) | ✅ Done |
| Budget & Invoice Management | ✅ Done |
| Equipment Management | ✅ Done |
| Safety Incidents | ✅ Done |
| Quality Inspections | ✅ Done |
| Communications | ✅ Done |

### ❌ Missing Modules (from Org Chart)

| Required by Org Chart | Module to Build |
|---|---|
| MD — Government Relations (PWD/DRDA/Highways) | `government_relations` app |
| MD — Fund Allotment & Fund Organising | `fund_management` app |
| MD — Investor Relationship | `investor_relations` app |
| Transport & Machinery Manager | `transport` app (extend equipment) |
| Drivers/Operators — Trip Sheet & Daily Report | `trip_sheet` model |
| Fuel Monitoring & Control | `fuel_log` model |
| Quantity Surveyor — BOQ, Measurement Book | `quantity_survey` app |
| Civil Draftsman — Drawing Management | `drawing_management` app |
| Estimation Engineer — Rate Analysis, Tender Estimation | `estimation` app |
| Work Status Classification (3-state) | Extend `Task` model |
| Meeting & Review System (Daily/Weekly/Monthly) | `meetings` app |
| Reporting Flow (Engineer → PM → OM → MD) | `reports` app |
| Role-specific Dashboards | Frontend only |
| Assistant A1 — Work Status Excel Export | API export endpoint |
| Assistant A2 — Contractor Follow-up, Labour Attendance | Extend existing models |

---

## 2. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     BEEMJI ENTERPRISE SYSTEM                    │
├────────────────────┬────────────────────┬───────────────────────┤
│   FRONTEND (React) │   BACKEND (Django)  │   INFRA               │
│                    │                     │                       │
│  - Role Dashboards │  - Django REST FW   │  - PostgreSQL (prod)  │
│  - MD Portal       │  - JWT Auth         │  - Redis (cache/queue)│
│  - PM Portal       │  - 14 Existing APIs │  - Celery (tasks)     │
│  - Admin Portal    │  - 8 New API Apps   │  - S3/Cloudinary      │
│  - Site Eng App    │  - WebSocket (msg)  │    (file storage)     │
│  - Transport App   │  - Celery (reports) │  - Nginx              │
│  - Driver App      │  - Export (Excel)   │  - Gunicorn           │
└────────────────────┴────────────────────┴───────────────────────┘
```

### Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2 + Django REST Framework |
| Auth | djangorestframework-simplejwt |
| Database (Dev) | SQLite |
| Database (Prod) | PostgreSQL |
| Task Queue | Celery + Redis |
| Real-time | Django Channels (WebSocket) |
| File Storage | Local / AWS S3 |
| Cache | Redis |
| Frontend | React 18 + Vite + TailwindCSS |
| State Management | Zustand or Redux Toolkit |
| HTTP Client | Axios |
| Charts | Recharts / Chart.js |
| PDF Export | jsPDF + html2canvas |
| Excel Export | SheetJS (xlsx) |

---

## 3. ROLE & PERMISSION MATRIX

The user model uses a **two-field hierarchy**: `account_type` (which team) + `grade` (level within that team). This replaces the old single flat `role` field.

---

### 3.1 Account → Grade Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BEEMJI ENTERPRISE                            │
│                                                                     │
│  ● MANAGING DIRECTOR (MD)                                           │
│    account_type = "md"   |   grade = "md_head"                     │
│    ─ Standalone. No team. Full system access.                       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  🟩 ADMIN ACCOUNT  (account_type = "admin")                         │
│                                                                     │
│    Grade: admin_head  →  Office Manager                            │
│           ├─ Grade: admin_a1  →  Assistant A1 (Documentation)      │
│           └─ Grade: admin_a2  →  Assistant A2 (Coordination)       │
│                                                                     │
│    Responsibilities: Office operations, billing, tender docs,       │
│    work status reports, contractor coordination, labour records.    │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  🟦 TECHNICAL ACCOUNT  (account_type = "technical")                 │
│                                                                     │
│    Grade: tech_head   →  Project Manager (Technical Head)          │
│           ├─ Grade: tech_se   →  Site Engineer / Supervisor         │
│           │         (3 nos. — Site Engineer 1, 2, 3)               │
│           ├─ Grade: tech_qs   →  Quantity Surveyor  [as required]  │
│           ├─ Grade: tech_cd   →  Civil Draftsman    [as required]  │
│           ├─ Grade: tech_ee   →  Estimation Engineer [as required] │
│           ├─ Grade: tech_so   →  Safety Officer                    │
│           ├─ Grade: tech_qi   →  Quality Inspector                 │
│           ├─ Grade: tech_fm   →  Foreman                           │
│           ├─ Grade: tech_sc   →  Subcontractor                     │
│           └─ Grade: tech_wk   →  Worker                            │
│                                                                     │
│    Responsibilities: Site operations, progress, safety, quality,   │
│    drawings, BOQ, estimation, task management.                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  🟠 TRANSPORT ACCOUNT  (account_type = "transport")                 │
│                                                                     │
│    Grade: tr_head     →  Transport & Machinery Manager              │
│           └─ Grade: tr_do  →  Driver / Operator  (6 nos.)          │
│                                                                     │
│    Responsibilities: Fleet management, fuel, trip sheets,           │
│    vehicle maintenance, site material transportation.               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Grade Reference Table (All 15 Staff)

| Account | Grade Code | Title | Org Chart Name | Count |
|---|---|---|---|---|
| `md` | `md_head` | Managing Director | Managing Director (MD) | 1 |
| `admin` | `admin_head` | Office Manager | Office Manager | 1 |
| `admin` | `admin_a1` | Assistant A1 | Assistant A1 — Documentation | 1 |
| `admin` | `admin_a2` | Assistant A2 | Assistant A2 — Coordination | 1 |
| `technical` | `tech_head` | Project Manager | Project Manager | 1 |
| `technical` | `tech_se` | Site Engineer | Site Engineers / Supervisors | 3 |
| `technical` | `tech_qs` | Quantity Surveyor | Technical Support (As Required) | — |
| `technical` | `tech_cd` | Civil Draftsman | Technical Support (As Required) | — |
| `technical` | `tech_ee` | Estimation Engineer | Technical Support (As Required) | — |
| `technical` | `tech_so` | Safety Officer | — | — |
| `technical` | `tech_qi` | Quality Inspector | — | — |
| `technical` | `tech_fm` | Foreman | — | — |
| `technical` | `tech_sc` | Subcontractor | — | — |
| `technical` | `tech_wk` | Worker | — | — |
| `transport` | `tr_head` | Transport Manager | Transport & Machinery Manager | 1 |
| `transport` | `tr_do` | Driver / Operator | Drivers / Operators | 6 |

> **Core Staff = 15.** Technical Support (QS, CD, EE) and field roles (SO, QI, Foreman, SC, Worker) are created on-demand.

---

### 3.3 Grade Hierarchy & Reporting Chain

```
md_head
  │
  ├──► admin_head  ──► admin_a1
  │                └──► admin_a2
  │
  ├──► tech_head   ──► tech_se  ──► tech_fm ──► tech_wk
  │                ├──► tech_qs         └──► tech_sc
  │                ├──► tech_cd
  │                ├──► tech_ee
  │                ├──► tech_so
  │                └──► tech_qi
  │
  └──► tr_head     ──► tr_do
```

**Reporting Flow (as per org chart):**
```
tech_se  →  [Daily Work Report]  →  tech_head
tech_head → [Site Progress Review] → admin_head
admin_head → [Work Status Consolidation] → md_head
```

---

### 3.4 Access Permission Matrix

| Resource / Module | md_head | admin_head | admin_a1 | admin_a2 | tech_head | tech_se | tr_head | tr_do |
|---|---|---|---|---|---|---|---|---|
| **All Projects** | ✅ Full | ✅ Read | Read | Read | Own | Own | Read | ❌ |
| **Fund Management** | ✅ Full | View | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Government Relations** | ✅ Full | View | File only | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Investor Relations** | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Tender Docs** | ✅ Full | View | ✅ Upload | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Daily Report** | Review | Consolidate | Export | ❌ | Review | ✅ Submit | ❌ | ❌ |
| **Attendance** | ✅ Full | Approve | Export Excel | Bulk Entry | Own team | Own | Own team | Own |
| **Trip Sheets** | ✅ Full | View | ❌ | ✅ Logistics | View | ❌ | ✅ Full | Own |
| **Fuel Logs** | ✅ Full | View | ❌ | ❌ | View | ❌ | ✅ Full | Own |
| **BOQ / Qty Survey** | ✅ Full | View | ❌ | ❌ | Approve | View | ❌ | ❌ |
| **Drawings** | ✅ Full | ❌ | ❌ | ❌ | Approve | View | ❌ | ❌ |
| **Estimation** | ✅ Full | View | File only | ❌ | View | ❌ | ❌ | ❌ |
| **Meetings** | ✅ Full | ✅ Full | View | View | ✅ Full | Daily only | View | ❌ |
| **Safety Incidents** | View | View | ❌ | ❌ | Manage | ✅ Report | ❌ | ❌ |
| **Quality Inspect.** | View | View | ❌ | ❌ | Manage | ✅ Report | ❌ | ❌ |
| **Billing / Invoices** | View | ✅ Full | View | ❌ | View | ❌ | ❌ | ❌ |
| **Communications** | ✅ Full | ✅ Full | View | View | ✅ Full | ✅ Own | View | View |
| **Excel Exports** | ✅ All | ✅ All | ✅ All | Labour only | Own projects | ❌ | Fleet only | ❌ |

---

## 4. BACKEND — NEW & EXTENDED API MODULES

> Base URL remains: `/api/auth/`  
> All new apps will register under the same DRF router.

---

### 4.1 EXTEND: User Model — Account + Grade System

Replace the single flat `role` field with two fields: `account_type` (which team) and `grade` (level within that team).

**File:** `core/models.py`

```python
# ── Account Types ──────────────────────────────────────────────────
ACCOUNT_TYPE_CHOICES = [
    ('md',        'Managing Director'),
    ('admin',     'Admin Team'),
    ('technical', 'Technical Team'),
    ('transport', 'Transport & Machinery Team'),
]

# ── Grades per Account ─────────────────────────────────────────────
#    account_type → available grades
GRADE_CHOICES = [
    # MD Account
    ('md_head',    'Managing Director'),

    # Admin Account
    ('admin_head', 'Office Manager'),        # Admin Head
    ('admin_a1',   'Assistant A1'),          # Documentation
    ('admin_a2',   'Assistant A2'),          # Coordination

    # Technical Account
    ('tech_head',  'Project Manager'),       # Technical Head
    ('tech_se',    'Site Engineer'),         # 3 nos.
    ('tech_qs',    'Quantity Surveyor'),     # As Required
    ('tech_cd',    'Civil Draftsman'),       # As Required
    ('tech_ee',    'Estimation Engineer'),   # As Required
    ('tech_so',    'Safety Officer'),
    ('tech_qi',    'Quality Inspector'),
    ('tech_fm',    'Foreman'),
    ('tech_sc',    'Subcontractor'),
    ('tech_wk',    'Worker'),

    # Transport Account
    ('tr_head',    'Transport & Machinery Manager'),  # Operations Head
    ('tr_do',      'Driver / Operator'),              # 6 nos.
]

# ── Grade → Account mapping for validation ────────────────────────
GRADE_TO_ACCOUNT = {
    'md_head':    'md',
    'admin_head': 'admin',
    'admin_a1':   'admin',
    'admin_a2':   'admin',
    'tech_head':  'technical',
    'tech_se':    'technical',
    'tech_qs':    'technical',
    'tech_cd':    'technical',
    'tech_ee':    'technical',
    'tech_so':    'technical',
    'tech_qi':    'technical',
    'tech_fm':    'technical',
    'tech_sc':    'technical',
    'tech_wk':    'technical',
    'tr_head':    'transport',
    'tr_do':      'transport',
}

# ── Grade authority levels (higher = more access) ─────────────────
GRADE_LEVEL = {
    'md_head':    100,
    'admin_head':  60,
    'tech_head':   60,
    'tr_head':     60,
    'admin_a1':    40,
    'admin_a2':    40,
    'tech_se':     40,
    'tech_qs':     35,
    'tech_cd':     35,
    'tech_ee':     35,
    'tech_so':     35,
    'tech_qi':     35,
    'tr_do':       30,
    'tech_fm':     20,
    'tech_sc':     15,
    'tech_wk':     10,
}


class User(AbstractUser):
    # Remove old single 'role' field — replace with:
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='technical',
        help_text='Which team this user belongs to'
    )
    grade = models.CharField(
        max_length=20,
        choices=GRADE_CHOICES,
        default='tech_wk',
        help_text='Grade/level within the account team'
    )

    # Keep existing fields:
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active_employee = models.BooleanField(default=True)

    def clean(self):
        # Validate grade belongs to account_type
        expected_account = GRADE_TO_ACCOUNT.get(self.grade)
        if expected_account and expected_account != self.account_type:
            raise ValidationError(
                f"Grade '{self.grade}' does not belong to account '{self.account_type}'. "
                f"Expected account: '{expected_account}'."
            )

    @property
    def authority_level(self):
        return GRADE_LEVEL.get(self.grade, 0)

    @property
    def is_md(self):
        return self.account_type == 'md'

    @property
    def is_admin_team(self):
        return self.account_type == 'admin'

    @property
    def is_technical_team(self):
        return self.account_type == 'technical'

    @property
    def is_transport_team(self):
        return self.account_type == 'transport'

    @property
    def is_head_of_team(self):
        return self.grade in ('md_head', 'admin_head', 'tech_head', 'tr_head')

    def __str__(self):
        return f"{self.get_full_name()} [{self.get_grade_display()} / {self.get_account_type_display()}]"
```

#### Permission Helper (core/permissions.py)

```python
from rest_framework.permissions import BasePermission
from .models import GRADE_LEVEL

class MinimumGradePermission(BasePermission):
    """
    Usage:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, MinimumGrade('tech_se')]
    """
    def __init__(self, minimum_grade):
        self.minimum_level = GRADE_LEVEL.get(minimum_grade, 0)

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.authority_level >= self.minimum_level
        )

def MinimumGrade(grade):
    """Factory so it can be used inline in permission_classes."""
    perm = MinimumGradePermission.__new__(MinimumGradePermission)
    perm.minimum_level = GRADE_LEVEL.get(grade, 0)
    return perm


class AccountTypePermission(BasePermission):
    """
    Restrict access to specific account types.
    Usage: AccountOnly('admin', 'md')
    """
    def __init__(self, *allowed_accounts):
        self.allowed = set(allowed_accounts)

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.account_type in self.allowed
        )

def AccountOnly(*accounts):
    perm = AccountTypePermission.__new__(AccountTypePermission)
    perm.allowed = set(accounts)
    return perm
```

#### Serializer Update (core/serializers.py)

```python
class UserSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(
        source='get_account_type_display', read_only=True
    )
    grade_display = serializers.CharField(
        source='get_grade_display', read_only=True
    )
    authority_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'account_type', 'account_type_display',
            'grade', 'grade_display',
            'authority_level',
            'phone', 'employee_id', 'department', 'hire_date',
            'is_active_employee',
        ]

    def validate(self, data):
        # Cross-validate account_type vs grade
        from .models import GRADE_TO_ACCOUNT
        grade = data.get('grade', self.instance.grade if self.instance else None)
        account = data.get('account_type', self.instance.account_type if self.instance else None)
        expected = GRADE_TO_ACCOUNT.get(grade)
        if expected and expected != account:
            raise serializers.ValidationError(
                {'grade': f"Grade '{grade}' must belong to account '{expected}', not '{account}'."}
            )
        return data
```

#### New API Endpoints for User Filtering

```
GET /users/?account_type=admin              ← all admin team members
GET /users/?account_type=technical          ← all technical team
GET /users/?account_type=transport          ← all transport team
GET /users/?grade=tech_se                   ← all site engineers
GET /users/?grade=tr_do                     ← all drivers
GET /users/team-summary/                    ← count per account + grade
```

#### Migration Note

Since the old model had a single `role` field, create a data migration to map old roles to new account + grade:

```python
# core/migrations/XXXX_migrate_roles_to_account_grade.py

ROLE_MAP = {
    'admin':             ('md',        'md_head'),
    'project_manager':   ('technical', 'tech_head'),
    'site_engineer':     ('technical', 'tech_se'),
    'foreman':           ('technical', 'tech_fm'),
    'subcontractor':     ('technical', 'tech_sc'),
    'worker':            ('technical', 'tech_wk'),
    'safety_officer':    ('technical', 'tech_so'),
    'quality_inspector': ('technical', 'tech_qi'),
}

def migrate_roles(apps, schema_editor):
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        account, grade = ROLE_MAP.get(user.role, ('technical', 'tech_wk'))
        user.account_type = account
        user.grade = grade
        user.save()
```

---

### 4.2 NEW APP: `government_relations`

Manages PWD/DRDA/Highways coordination, tender tracking, client & government officer relationships.

#### Models

```python
class GovernmentDepartment(models.Model):
    name = models.CharField(max_length=200)           # PWD, DRDA, Highways, etc.
    department_type = models.CharField(...)
    contact_officer = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True)
    district = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

class TenderApplication(models.Model):
    STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    tender_number = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(GovernmentDepartment, on_delete=models.PROTECT)
    project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True)
    tender_value = models.DecimalField(max_digits=15, decimal_places=2)
    submission_date = models.DateField()
    decision_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    documents = models.FileField(upload_to='tenders/', blank=True)
    notes = models.TextField(blank=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GovernmentContact(models.Model):
    department = models.ForeignKey(GovernmentDepartment, on_delete=models.CASCADE)
    officer_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    relationship_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    last_meeting_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
```

#### API Endpoints

```
GET/POST   /government-departments/
GET/PUT/PATCH/DELETE /government-departments/<id>/

GET/POST   /tenders/
GET/PUT/PATCH/DELETE /tenders/<id>/
POST       /tenders/<id>/approve/
POST       /tenders/<id>/submit/

GET/POST   /government-contacts/
```

---

### 4.3 NEW APP: `fund_management`

Handles fund allotment by project, fund sourcing (bank loans, NBFC, working capital), and release tracking.

#### Models

```python
class FundSource(models.Model):
    SOURCE_TYPES = [
        ('bank_loan', 'Bank Loan'),
        ('working_capital', 'Working Capital'),
        ('equipment_finance', 'Equipment Finance'),
        ('nbfc', 'NBFC'),
        ('partner', 'Partner Funding'),
        ('own_funds', 'Own Funds'),
    ]
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPES)
    institution_name = models.CharField(max_length=200)
    sanctioned_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    disbursed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    repaid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

class FundAllotment(models.Model):
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE, related_name='fund_allotments')
    fund_source = models.ForeignKey(FundSource, on_delete=models.PROTECT)
    allotment_type = models.CharField(max_length=50)   # machinery, labour, material, advance
    allotted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    released_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    allotment_date = models.DateField()
    release_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    @property
    def pending_release(self):
        return self.allotted_amount - self.released_amount

class FundTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('disbursement', 'Disbursement'),
        ('repayment', 'Repayment'),
        ('advance', 'Site Advance'),
        ('release', 'Fund Release'),
    ]
    allotment = models.ForeignKey(FundAllotment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
```

#### API Endpoints

```
GET/POST   /fund-sources/
GET/PUT/PATCH/DELETE /fund-sources/<id>/

GET/POST   /fund-allotments/
GET/PUT/PATCH/DELETE /fund-allotments/<id>/
POST       /fund-allotments/<id>/release/   ← releases funds to site
GET        /fund-allotments/?project=<id>

GET/POST   /fund-transactions/
GET        /fund-summary/                   ← MD dashboard summary
```

---

### 4.4 NEW APP: `investor_relations`

Investor communication log, profit/loss reports, progress updates, investment planning.

#### Models

```python
class Investor(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    investment_date = models.DateField(null=True, blank=True)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

class InvestorReport(models.Model):
    REPORT_TYPES = [
        ('profit_loss', 'Profit & Loss'),
        ('progress_update', 'Project Progress'),
        ('financial_summary', 'Financial Summary'),
        ('future_investment', 'Future Investment Plan'),
    ]
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    period_from = models.DateField()
    period_to = models.DateField()
    content = models.TextField()
    attachment = models.FileField(upload_to='investor_reports/', blank=True)
    sent_date = models.DateField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### API Endpoints

```
GET/POST   /investors/
GET/PUT/PATCH/DELETE /investors/<id>/

GET/POST   /investor-reports/
GET/PUT/PATCH/DELETE /investor-reports/<id>/
POST       /investor-reports/<id>/send/    ← mark as sent
```

---

### 4.5 NEW APP: `transport`

Vehicle & machinery management, fuel logs, trip sheets, driver assignments.

#### Models

```python
class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('tipper_truck', 'Tipper Truck'),
        ('excavator', 'Excavator'),
        ('jcb', 'JCB'),
        ('concrete_mixer', 'Concrete Mixer'),
        ('crane', 'Crane'),
        ('roller', 'Road Roller'),
        ('other', 'Other'),
    ]
    STATUS = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('breakdown', 'Breakdown'),
        ('inactive', 'Inactive'),
    ]
    vehicle_id = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=30, unique=True)
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPES)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    current_project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='available')
    last_service_date = models.DateField(null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)

class TripSheet(models.Model):
    STATUS = [
        ('open', 'Open'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
    ]
    trip_id = models.CharField(max_length=50, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='trips')
    project = models.ForeignKey('core.Project', on_delete=models.PROTECT)
    trip_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    start_odometer = models.DecimalField(max_digits=10, decimal_places=1)
    end_odometer = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    from_location = models.CharField(max_length=200)
    to_location = models.CharField(max_length=200)
    purpose = models.TextField()         # material transport, site visit, etc.
    material_carried = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_trips')
    notes = models.TextField(blank=True)

    @property
    def distance_km(self):
        if self.end_odometer:
            return self.end_odometer - self.start_odometer
        return None

class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    project = models.ForeignKey('core.Project', on_delete=models.PROTECT)
    fill_date = models.DateField()
    fuel_type = models.CharField(max_length=20, choices=[('diesel', 'Diesel'), ('petrol', 'Petrol')])
    quantity_litres = models.DecimalField(max_digits=8, decimal_places=2)
    rate_per_litre = models.DecimalField(max_digits=6, decimal_places=2)
    odometer_reading = models.DecimalField(max_digits=10, decimal_places=1)
    fuel_station = models.CharField(max_length=200)
    bill_number = models.CharField(max_length=100, blank=True)
    bill_attachment = models.FileField(upload_to='fuel_bills/', blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_fuel')

    @property
    def total_cost(self):
        return self.quantity_litres * self.rate_per_litre
```

#### API Endpoints

```
GET/POST   /vehicles/
GET/PUT/PATCH/DELETE /vehicles/<id>/
POST       /vehicles/<id>/assign/          ← assign to project + driver
POST       /vehicles/<id>/maintenance/     ← set maintenance status
GET        /vehicles/due-maintenance/      ← vehicles needing service

GET/POST   /trip-sheets/
GET/PUT/PATCH/DELETE /trip-sheets/<id>/
PATCH      /trip-sheets/<id>/complete/     ← driver closes trip
PATCH      /trip-sheets/<id>/verify/       ← manager verifies
GET        /trip-sheets/?vehicle=<id>
GET        /trip-sheets/?driver=<id>
GET        /trip-sheets/?project=<id>
GET        /trip-sheets/?date=<YYYY-MM-DD>

GET/POST   /fuel-logs/
GET/PUT/PATCH/DELETE /fuel-logs/<id>/
GET        /fuel-logs/?vehicle=<id>
GET        /fuel-summary/?project=<id>     ← fuel cost summary
```

---

### 4.6 NEW APP: `quantity_survey`

BOQ (Bill of Quantities), quantity calculations, measurement books, cost control.

#### Models

```python
class BOQ(models.Model):
    boq_id = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    version = models.CharField(max_length=10, default='1.0')
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_boqs')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

class BOQItem(models.Model):
    boq = models.ForeignKey(BOQ, on_delete=models.CASCADE, related_name='items')
    item_code = models.CharField(max_length=30)
    description = models.TextField()
    unit = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2)
    task = models.ForeignKey('core.Task', on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def amount(self):
        return self.quantity * self.unit_rate

class MeasurementBook(models.Model):
    mb_number = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
    boq = models.ForeignKey(BOQ, on_delete=models.PROTECT)
    measurement_date = models.DateField()
    work_description = models.TextField()
    measured_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_mbs')
    is_verified = models.BooleanField(default=False)

class MeasurementEntry(models.Model):
    measurement_book = models.ForeignKey(MeasurementBook, on_delete=models.CASCADE, related_name='entries')
    boq_item = models.ForeignKey(BOQItem, on_delete=models.PROTECT)
    length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    breadth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    depth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    nos = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    measured_quantity = models.DecimalField(max_digits=12, decimal_places=3)
    remarks = models.CharField(max_length=200, blank=True)
```

#### API Endpoints

```
GET/POST   /boqs/
GET/PUT/PATCH/DELETE /boqs/<id>/
POST       /boqs/<id>/approve/
GET        /boqs/<id>/items/
POST       /boqs/<id>/export-excel/        ← export BOQ as Excel

GET/POST   /boq-items/
GET/PUT/PATCH/DELETE /boq-items/<id>/

GET/POST   /measurement-books/
GET/PUT/PATCH/DELETE /measurement-books/<id>/
POST       /measurement-books/<id>/verify/
GET        /measurement-books/<id>/entries/
POST       /measurement-books/<id>/export-pdf/
```

---

### 4.7 NEW APP: `drawings`

Civil drawing management — plan drawings, as-built drawings, section drawings, AutoCAD file management.

#### Models

```python
class Drawing(models.Model):
    DRAWING_TYPES = [
        ('plan', 'Plan Drawing'),
        ('section', 'Section Drawing'),
        ('elevation', 'Elevation'),
        ('as_built', 'As-Built Drawing'),
        ('structural', 'Structural Drawing'),
        ('electrical', 'Electrical Drawing'),
        ('plumbing', 'Plumbing Drawing'),
        ('landscape', 'Landscape Drawing'),
    ]
    STATUS = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
        ('as_built', 'As-Built'),
    ]
    drawing_number = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
    task = models.ForeignKey('core.Task', on_delete=models.SET_NULL, null=True, blank=True)
    drawing_type = models.CharField(max_length=20, choices=DRAWING_TYPES)
    title = models.CharField(max_length=200)
    scale = models.CharField(max_length=50, blank=True)    # e.g., 1:100
    revision = models.CharField(max_length=10, default='A')
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    file = models.FileField(upload_to='drawings/')         # DWG, PDF
    thumbnail = models.ImageField(upload_to='drawing_thumbs/', blank=True)
    drawn_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='drawn')
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_drawings')
    drawing_date = models.DateField()
    approval_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    superseded_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### API Endpoints

```
GET/POST   /drawings/
GET/PUT/PATCH/DELETE /drawings/<id>/
POST       /drawings/<id>/approve/
POST       /drawings/<id>/supersede/
GET        /drawings/?project=<id>
GET        /drawings/?type=<drawing_type>
GET        /drawings/latest/               ← latest revision per drawing number
```

---

### 4.8 NEW APP: `estimation`

Rate analysis, cost estimation, tender estimation, comparative statements.

#### Models

```python
class RateAnalysis(models.Model):
    item_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    unit = models.CharField(max_length=20)
    materials_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labour_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    machinery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overhead_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    reference_schedule = models.CharField(max_length=100, blank=True)  # SSR year, etc.
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    @property
    def base_rate(self):
        return self.materials_cost + self.labour_cost + self.machinery_cost

    @property
    def total_rate(self):
        base = self.base_rate
        overhead = base * (self.overhead_percentage / 100)
        profit = (base + overhead) * (self.profit_percentage / 100)
        return base + overhead + profit

class TenderEstimate(models.Model):
    tender = models.ForeignKey('government_relations.TenderApplication', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    total_estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
    contingency_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    prepared_date = models.DateField()

class ComparativeStatement(models.Model):
    tender = models.ForeignKey('government_relations.TenderApplication', on_delete=models.CASCADE)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comparison_date = models.DateField()
    lowest_bidder = models.CharField(max_length=200, blank=True)
    recommendation = models.TextField(blank=True)
    attachment = models.FileField(upload_to='comparative_statements/', blank=True)
```

#### API Endpoints

```
GET/POST   /rate-analysis/
GET/PUT/PATCH/DELETE /rate-analysis/<id>/
GET        /rate-analysis/schedule/        ← grouped by schedule/year

GET/POST   /tender-estimates/
GET/PUT/PATCH/DELETE /tender-estimates/<id>/
POST       /tender-estimates/<id>/export-pdf/

GET/POST   /comparative-statements/
GET/PUT/PATCH/DELETE /comparative-statements/<id>/
```

---

### 4.9 NEW APP: `meetings`

Daily, Weekly (Saturday), Monthly meeting records, minutes, action items.

#### Models

```python
class Meeting(models.Model):
    MEETING_TYPES = [
        ('daily', 'Daily Site Work Review'),
        ('weekly', 'Weekly Project Progress Review'),
        ('monthly', 'Monthly MD Review'),
    ]
    STATUS = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    meeting_id = models.CharField(max_length=50, unique=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    actual_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS, default='scheduled')
    agenda = models.TextField()
    minutes = models.TextField(blank=True)
    organized_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_meetings')
    created_at = models.DateTimeField(auto_now_add=True)

class MeetingAttendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)

class ActionItem(models.Model):
    PRIORITY = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    STATUS = [('open', 'Open'), ('in_progress', 'In Progress'), ('done', 'Done'), ('overdue', 'Overdue')]
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    description = models.TextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    completion_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
```

#### API Endpoints

```
GET/POST   /meetings/
GET/PUT/PATCH/DELETE /meetings/<id>/
POST       /meetings/<id>/start/
POST       /meetings/<id>/complete/
GET        /meetings/?type=daily|weekly|monthly
GET        /meetings/today/

GET/POST   /meeting-attendees/
PATCH      /meeting-attendees/<id>/mark-present/

GET/POST   /action-items/
PATCH      /action-items/<id>/complete/
GET        /action-items/?assignee=<user_id>
GET        /action-items/overdue/
```

---

### 4.10 NEW APP: `reports`

Implements the Reporting Flow: Site Engineer → Project Manager → Office Manager → MD.

#### Models

```python
class DailyWorkReport(models.Model):
    STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted to PM'),
        ('pm_reviewed', 'PM Reviewed'),
        ('om_consolidated', 'OM Consolidated'),
        ('md_reviewed', 'MD Reviewed'),
    ]
    report_id = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
    report_date = models.DateField()
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='daily_reports')
    status = models.CharField(max_length=20, choices=STATUS, default='draft')

    # Work Progress
    work_completed_today = models.TextField()
    work_planned_tomorrow = models.TextField()
    issues_faced = models.TextField(blank=True)

    # Labour
    total_workers_present = models.IntegerField(default=0)
    total_workers_absent = models.IntegerField(default=0)
    subcontractor_workers = models.IntegerField(default=0)

    # Materials Used
    materials_used = models.JSONField(default=list)  # [{name, qty, unit}]

    # Equipment
    equipment_used = models.JSONField(default=list)

    # Weather
    weather_condition = models.CharField(max_length=50, blank=True)
    rainfall_mm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # Progress
    overall_progress_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    # Review chain
    pm_remarks = models.TextField(blank=True)
    pm_reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pm_reviewed_reports')
    pm_reviewed_at = models.DateTimeField(null=True, blank=True)

    om_remarks = models.TextField(blank=True)
    om_reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='om_reviewed_reports')
    om_reviewed_at = models.DateTimeField(null=True, blank=True)

    md_remarks = models.TextField(blank=True)
    md_reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='md_reviewed_reports')
    md_reviewed_at = models.DateTimeField(null=True, blank=True)

    photo_attachments = models.ManyToManyField('core.Document', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### API Endpoints

```
GET/POST   /daily-reports/
GET/PUT/PATCH/DELETE /daily-reports/<id>/
POST       /daily-reports/<id>/submit/          ← SE submits to PM
POST       /daily-reports/<id>/pm-review/       ← PM reviews
POST       /daily-reports/<id>/om-consolidate/  ← OM consolidates
POST       /daily-reports/<id>/md-review/       ← MD reviews
GET        /daily-reports/?project=<id>&date=<date>
GET        /daily-reports/pending-review/       ← reports waiting review at each level
POST       /daily-reports/<id>/export-pdf/
GET        /work-status-summary/?project=<id>   ← ongoing/completed/not-started counts
```

---

### 4.11 EXTEND: Task Work Status Classification

Update `Task` model in `core/models.py`:

```python
WORK_STATUS = [
    ('ongoing', 'Ongoing — Work in Progress as per plan and target'),
    ('completed', 'Completed — Work completed and handed over'),
    ('not_started', 'Not Started — Yet to be started (planning/approval pending)'),
]

# Add to Task model:
work_status = models.CharField(max_length=15, choices=WORK_STATUS, default='not_started')
```

This maps to the 3-state Work Status Classification shown in the org chart.

---

### 4.12 EXTEND: Attendance — Labour Management

Add to `Attendance` model for better labour tracking (needed by Assistant A2):

```python
# Add fields to existing Attendance model:
attendance_type = models.CharField(max_length=20, choices=[
    ('employee', 'Company Employee'),
    ('contractor', 'Contractor Worker'),
    ('subcontractor', 'Subcontractor'),
], default='employee')
contractor_name = models.CharField(max_length=200, blank=True)
work_category = models.CharField(max_length=100, blank=True)  # masonry, carpentry, etc.
daily_wage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
is_approved = models.BooleanField(default=False)
approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendance')
```

#### New Endpoint

```
POST   /attendance/bulk-checkin/              ← A2 bulk records contractor attendance
GET    /attendance/export-excel/?project=<id>&date=<date>  ← A1 exports to Excel
GET    /attendance/labour-summary/?project=<id>
```

---

### 4.13 EXTEND: Export API (Assistant A1 — Excel)

All major modules should support Excel export:

```
GET /projects/export-excel/
GET /attendance/export-excel/?project=<id>&from=<date>&to=<date>
GET /daily-reports/export-excel/?project=<id>&month=<YYYY-MM>
GET /boqs/<id>/export-excel/
GET /trip-sheets/export-excel/?vehicle=<id>&month=<YYYY-MM>
GET /fuel-logs/export-excel/?project=<id>
GET /invoices/export-excel/?project=<id>
GET /budgets/export-excel/?project=<id>
```

**Implementation:** Use `openpyxl` library for all Excel exports.

```bash
pip install openpyxl
```

---

## 5. FRONTEND PAGES — COMPLETE PLAN

### Tech Stack

```bash
# Setup
npm create vite@latest beemji-frontend -- --template react
cd beemji-frontend
npm install axios zustand react-router-dom tailwindcss recharts @headlessui/react
npm install jspdf html2canvas xlsx react-hot-toast date-fns lucide-react
```

### Page Structure by Role

---

#### 🟦 COMMON PAGES (All Roles)

| Page | Route | Description |
|---|---|---|
| Login | `/login` | JWT login — detects `account_type` + `grade`, redirects to correct dashboard |
| Dashboard | `/dashboard` | Role-based dashboard redirect |
| Profile | `/profile` | User profile, change password |
| Notifications | `/notifications` | Action items, alerts, messages |

---

#### 🔴 MD DASHBOARD (managing_director)

| Page | Route | Key Widgets |
|---|---|---|
| MD Home | `/md` | Projects overview, fund summary, pending tenders, investor updates |
| Company Vision | `/md/vision` | Strategic goals, expansion planning |
| Government Relations | `/md/government` | Departments list, tender pipeline, approval status |
| Tender Details | `/md/tenders/:id` | Tender application detail, documents |
| Fund Overview | `/md/funds` | Fund sources, allotments, cash flow chart |
| Investor Portal | `/md/investors` | Investor list, reports sent, profit/loss |
| All Projects (MD View) | `/md/projects` | All projects with status, progress, fund health |
| Monthly Review | `/md/monthly-review` | Monthly meeting records, MD review queue |
| Reports Inbox | `/md/reports` | Daily/weekly reports pending MD review |

---

#### 🟩 OFFICE MANAGER / ADMIN TEAM

| Page | Route | Key Features |
|---|---|---|
| Admin Dashboard | `/admin-office` | Work status board, billing pending, tender docs |
| Work Status Board | `/admin-office/work-status` | Projects with 3-state: Ongoing / Completed / Not Started |
| Tender Documents | `/admin-office/tenders` | Document filing, upload, track submissions |
| Billing & Payments | `/admin-office/billing` | Invoice list, payment follow-up, overdue alerts |
| Weekly Report View | `/admin-office/weekly` | Weekly reports consolidation view |
| Staff Directory | `/admin-office/staff` | All 15 staff, roles, contact |

---

#### 📄 ASSISTANT A1 — DOCUMENTATION

| Page | Route | Key Features |
|---|---|---|
| A1 Dashboard | `/a1` | Tasks today, pending Excel exports, document queue |
| Work Status Excel | `/a1/work-status-excel` | Generate & download work status Excel per project |
| Progress Reports | `/a1/progress-reports` | View/generate project progress report PDFs |
| Tender Documents | `/a1/tender-docs` | Upload, organize, submit tender documents |
| Bill Copies | `/a1/bills` | Bill filing, scan upload, categorize |
| Government Docs | `/a1/government-docs` | Government office document submission log |

---

#### 🔧 ASSISTANT A2 — COORDINATION

| Page | Route | Key Features |
|---|---|---|
| A2 Dashboard | `/a2` | Contractor status, material deliveries, vehicle log |
| Contractor Follow-up | `/a2/contractors` | Contractor list, follow-up dates, status |
| Material Delivery | `/a2/material-delivery` | Material requests status, delivery tracking |
| Site Updates | `/a2/site-updates` | Site update log from engineers |
| Labour Attendance | `/a2/labour-attendance` | Bulk contractor attendance entry, export |
| Vehicle & Logistics | `/a2/logistics` | Vehicle assignment, trip status today |

---

#### 🏗️ PROJECT MANAGER PORTAL (Technical Head)

| Page | Route | Key Features |
|---|---|---|
| PM Dashboard | `/pm` | All site projects, progress bars, pending reviews |
| Project Detail | `/pm/projects/:id` | Tasks, budget, team, site engineers, documents |
| Task Board | `/pm/projects/:id/tasks` | Kanban with 3-state work status |
| Site Progress Review | `/pm/reports` | Daily reports from site engineers, PM review |
| Weekly Report Submit | `/pm/weekly-report` | Weekly progress report to Office Manager |
| Material Requests | `/pm/materials` | Approve/reject material requests |
| Quality Control | `/pm/quality` | Inspection schedule, findings |
| Safety Overview | `/pm/safety` | Incidents, open investigations |
| Schedule | `/pm/schedule` | Gantt chart of project tasks |
| BOQ Manager | `/pm/boq/:project_id` | Review and approve BOQ |

---

#### 👷 SITE ENGINEER PORTAL

| Page | Route | Key Features |
|---|---|---|
| Site Dashboard | `/site` | Today's tasks, worker count, weather, pending report |
| Daily Report Entry | `/site/daily-report` | Submit daily work report (form) |
| Attendance Entry | `/site/attendance` | Record worker attendance, check-in/out |
| Task Update | `/site/tasks` | Update task progress, work status |
| Engineer Inspection | `/site/inspections` | Inspection checklist, photo upload |
| Material Request | `/site/material-request` | Raise material request |
| Safety Report | `/site/safety` | Report safety incident |
| Drawing Viewer | `/site/drawings` | View approved drawings for their project |
| Daily Progress Report | `/site/progress-photos` | Upload site photos with descriptions |

---

#### 🚛 TRANSPORT & MACHINERY MANAGER

| Page | Route | Key Features |
|---|---|---|
| Transport Dashboard | `/transport` | Fleet status map, vehicles in use, due maintenance |
| Vehicle List | `/transport/vehicles` | All vehicles, status, current project, driver |
| Vehicle Detail | `/transport/vehicles/:id` | Trip history, fuel history, maintenance log |
| Trip Sheets | `/transport/trip-sheets` | All trips, verify, filter by date/project/driver |
| Fuel Logs | `/transport/fuel` | Fuel consumption per vehicle, cost chart |
| Maintenance Planner | `/transport/maintenance` | Service due alerts, maintenance history |
| Assign Vehicle | `/transport/assign` | Assign vehicle + driver to project |
| Daily Vehicle Report | `/transport/daily-report` | End-of-day fleet summary |

---

#### 🚗 DRIVER / OPERATOR APP

| Page | Route | Key Features |
|---|---|---|
| Driver Home | `/driver` | Today's assignment, vehicle details |
| Start Trip | `/driver/trip/start` | Start trip — enter odometer, from/to |
| End Trip | `/driver/trip/:id/end` | Close trip — end odometer, notes |
| Trip History | `/driver/trips` | My past trips |
| Fuel Entry | `/driver/fuel` | Record fuel fill-up with bill photo |
| Daily Check | `/driver/vehicle-check` | Pre-trip vehicle inspection checklist |

---

#### 📐 QUANTITY SURVEYOR

| Page | Route | Key Features |
|---|---|---|
| QS Dashboard | `/qs` | BOQs pending approval, measurement books due |
| BOQ List | `/qs/boqs` | All BOQs, version history |
| BOQ Editor | `/qs/boqs/:id/edit` | Line-by-line BOQ entry, linked to tasks |
| Measurement Book | `/qs/measurement-books` | Record measurements per site visit |
| MB Detail | `/qs/measurement-books/:id` | Entries, L×B×D calculations |
| Cost Control | `/qs/cost-control` | Budget vs actual vs committed |
| Excel Export | `/qs/export` | Export BOQ, MB to Excel |

---

#### ✏️ CIVIL DRAFTSMAN

| Page | Route | Key Features |
|---|---|---|
| Drawing Dashboard | `/draftsman` | Drawing queue, revision requests |
| Drawing List | `/draftsman/drawings` | All drawings by project, type, status |
| Upload Drawing | `/draftsman/upload` | Upload DWG/PDF, set metadata |
| Drawing Viewer | `/draftsman/drawings/:id` | PDF viewer, revision history |
| As-Built Upload | `/draftsman/as-built` | Upload as-built drawings |
| Drawing Register | `/draftsman/register` | Drawing register export |

---

#### 📊 ESTIMATION ENGINEER

| Page | Route | Key Features |
|---|---|---|
| Estimation Dashboard | `/estimation` | Active tender estimates, rate analysis library |
| Rate Analysis | `/estimation/rates` | SSR rate library, custom rate entries |
| Rate Detail | `/estimation/rates/:id` | Material + Labour + Machinery cost breakdown |
| Tender Estimate | `/estimation/tender-estimate` | Build estimate for a tender |
| Comparative Statement | `/estimation/comparative` | Multi-bid comparison table |
| Export PDF | `/estimation/export` | Generate estimate PDF |

---

### Shared Components Plan

```
components/
├── layout/
│   ├── Sidebar.jsx            ← Account+Grade-aware sidebar (different nav per account_type)
│   ├── TopBar.jsx             ← Shows user name, grade_display, account_type badge
│   └── PageWrapper.jsx
├── charts/
│   ├── ProjectProgressBar.jsx
│   ├── BudgetDonut.jsx
│   ├── FundFlowChart.jsx
│   ├── AttendanceTrend.jsx
│   └── WorkStatusPie.jsx
├── tables/
│   ├── DataTable.jsx          ← Sortable, filterable
│   └── ExportButton.jsx
├── forms/
│   ├── AttendanceForm.jsx
│   ├── DailyReportForm.jsx
│   └── TripSheetForm.jsx
├── status/
│   ├── WorkStatusBadge.jsx    ← 🟢 Ongoing 🔵 Completed 🔴 Not Started
│   ├── TenderStatusBadge.jsx
│   └── ProjectStatusBadge.jsx
└── modals/
    ├── ReviewModal.jsx
    └── ConfirmModal.jsx
```

---

## 6. DATABASE SCHEMA EXTENSIONS

### Summary of New Tables

| App | New Tables |
|---|---|
| government_relations | GovernmentDepartment, TenderApplication, GovernmentContact |
| fund_management | FundSource, FundAllotment, FundTransaction |
| investor_relations | Investor, InvestorReport |
| transport | Vehicle, TripSheet, FuelLog |
| quantity_survey | BOQ, BOQItem, MeasurementBook, MeasurementEntry |
| drawings | Drawing |
| estimation | RateAnalysis, TenderEstimate, ComparativeStatement |
| meetings | Meeting, MeetingAttendee, ActionItem |
| reports | DailyWorkReport |
| core (extend) | Task.work_status, Attendance.attendance_type, etc. |

### Django Settings — Register New Apps

```python
# construction_mgmt/settings.py

INSTALLED_APPS = [
    # existing...
    'core',
    # new apps:
    'government_relations',
    'fund_management',
    'investor_relations',
    'transport',
    'quantity_survey',
    'drawings',
    'estimation',
    'meetings',
    'reports',
]
```

### URL Registration

```python
# construction_mgmt/urls.py

from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('core.urls')),
    path('api/gov/', include('government_relations.urls')),
    path('api/funds/', include('fund_management.urls')),
    path('api/investors/', include('investor_relations.urls')),
    path('api/transport/', include('transport.urls')),
    path('api/qs/', include('quantity_survey.urls')),
    path('api/drawings/', include('drawings.urls')),
    path('api/estimation/', include('estimation.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/reports/', include('reports.urls')),
]
```

---

## 7. RUNNING THE APPLICATION

### Backend Setup

```bash
# 1. Clone and create virtualenv
git clone <repo-url>
cd construct-backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add new dependencies
pip install openpyxl pillow celery redis django-channels

# 4. Run migrations (after creating all new apps)
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (MD account)
python manage.py createsuperuser

# 6. Create initial roles (via management command — create this)
python manage.py seed_roles

# 7. Run backend
python manage.py runserver
```

### Frontend Setup

```bash
# 1. Create frontend project
npm create vite@latest beemji-frontend -- --template react
cd beemji-frontend

# 2. Install dependencies
npm install axios zustand react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install recharts @headlessui/react lucide-react
npm install jspdf html2canvas xlsx react-hot-toast date-fns

# 3. Configure API base URL
# Create .env file:
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# 4. Run frontend
npm run dev
# → http://localhost:5173
```

### Environment Variables

```env
# backend/.env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost:5432/beemji
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.com
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=beemji-files

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Beemji Enterprise
```

---

## 8. FOLDER STRUCTURE (FULL)

```
beemji-enterprise/
├── construct-backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── construction_mgmt/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py          ← NEW
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── core/                  ← EXISTING (extend)
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── exports.py         ← NEW: Excel export helpers
│   │   └── migrations/
│   ├── government_relations/  ← NEW
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── fund_management/       ← NEW
│   ├── investor_relations/    ← NEW
│   ├── transport/             ← NEW
│   ├── quantity_survey/       ← NEW
│   ├── drawings/              ← NEW
│   ├── estimation/            ← NEW
│   ├── meetings/              ← NEW
│   └── reports/               ← NEW
│
└── beemji-frontend/
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── api/
    │   │   ├── axios.js        ← Configured axios instance
    │   │   ├── auth.js
    │   │   ├── projects.js
    │   │   ├── transport.js
    │   │   └── reports.js
    │   ├── store/
    │   │   ├── authStore.js    ← Zustand auth state
    │   │   └── uiStore.js
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── md/             ← MD pages
    │   │   ├── admin-office/   ← Office Manager, A1, A2 pages
    │   │   ├── pm/             ← Project Manager pages
    │   │   ├── site/           ← Site Engineer pages
    │   │   ├── transport/      ← Transport Manager pages
    │   │   ├── driver/         ← Driver/Operator pages
    │   │   ├── qs/             ← Quantity Surveyor pages
    │   │   ├── draftsman/      ← Civil Draftsman pages
    │   │   └── estimation/     ← Estimation Engineer pages
    │   ├── components/
    │   │   ├── layout/
    │   │   ├── charts/
    │   │   ├── tables/
    │   │   ├── forms/
    │   │   ├── status/
    │   │   └── modals/
    │   └── utils/
    │       ├── permissions.js   ← account_type + grade access helpers (checkGrade, checkAccount)
    │       ├── exportExcel.js
    │       └── exportPdf.js
```

### Frontend: Account + Grade Routing Logic

After login, the JWT payload contains `account_type` and `grade`. Use these to redirect to the correct dashboard:

```javascript
// src/utils/permissions.js

export const GRADE_LEVEL = {
  md_head: 100, admin_head: 60, tech_head: 60, tr_head: 60,
  admin_a1: 40, admin_a2: 40, tech_se: 40,
  tech_qs: 35, tech_cd: 35, tech_ee: 35, tech_so: 35, tech_qi: 35,
  tr_do: 30, tech_fm: 20, tech_sc: 15, tech_wk: 10,
};

export const DASHBOARD_ROUTE = {
  // MD Account
  md_head:    '/md',
  // Admin Account
  admin_head: '/admin-office',
  admin_a1:   '/a1',
  admin_a2:   '/a2',
  // Technical Account
  tech_head:  '/pm',
  tech_se:    '/site',
  tech_qs:    '/qs',
  tech_cd:    '/draftsman',
  tech_ee:    '/estimation',
  tech_so:    '/site',
  tech_qi:    '/site',
  tech_fm:    '/site',
  tech_sc:    '/site',
  tech_wk:    '/site',
  // Transport Account
  tr_head:    '/transport',
  tr_do:      '/driver',
};

export function getDashboardRoute(grade) {
  return DASHBOARD_ROUTE[grade] || '/dashboard';
}

export function hasMinimumGrade(userGrade, requiredGrade) {
  return (GRADE_LEVEL[userGrade] || 0) >= (GRADE_LEVEL[requiredGrade] || 0);
}

export function isAccountType(user, ...accounts) {
  return accounts.includes(user.account_type);
}

// React guard component
export function RequireGrade({ minGrade, children, fallback = null }) {
  const { user } = useAuthStore();
  if (!hasMinimumGrade(user?.grade, minGrade)) return fallback;
  return children;
}

export function RequireAccount({ accounts, children, fallback = null }) {
  const { user } = useAuthStore();
  if (!isAccountType(user, ...accounts)) return fallback;
  return children;
}
```

```javascript
// src/App.jsx — Route guards by account_type + grade
<Routes>
  {/* MD Account */}
  <Route path="/md/*" element={
    <RequireAccount accounts={['md']}><MDLayout /></RequireAccount>
  } />

  {/* Admin Account */}
  <Route path="/admin-office/*" element={
    <RequireAccount accounts={['admin']}><AdminLayout /></RequireAccount>
  } />
  <Route path="/a1/*" element={
    <RequireGrade minGrade="admin_a1"><A1Layout /></RequireGrade>
  } />
  <Route path="/a2/*" element={
    <RequireGrade minGrade="admin_a2"><A2Layout /></RequireGrade>
  } />

  {/* Technical Account */}
  <Route path="/pm/*" element={
    <RequireGrade minGrade="tech_head"><PMLayout /></RequireGrade>
  } />
  <Route path="/site/*" element={
    <RequireAccount accounts={['technical']}><SiteLayout /></RequireAccount>
  } />

  {/* Transport Account */}
  <Route path="/transport/*" element={
    <RequireGrade minGrade="tr_head"><TransportLayout /></RequireGrade>
  } />
  <Route path="/driver/*" element={
    <RequireAccount accounts={['transport']}><DriverLayout /></RequireAccount>
  } />
</Routes>
```

---

## 9. DEPLOYMENT & PRODUCTION HARDENING

### Critical Fixes Before Production

```python
# settings.py — REQUIRED changes:

# 1. Switch to PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': '5432',
    }
}

# 2. Disable DEBUG
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 3. Set ALLOWED_HOSTS properly
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# 4. Restrict CORS
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# 5. Secure SECRET_KEY
SECRET_KEY = os.environ['SECRET_KEY']

# 6. Replace API key permission with proper JWT everywhere
# Remove APIKeyPermission from AttendanceViewSet
# Use IsAuthenticated consistently
```

### Production Server

```bash
# Install production server
pip install gunicorn psycopg2-binary

# Run with Gunicorn
gunicorn construction_mgmt.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Nginx config: proxy to Gunicorn, serve React static files
```

### Missing Tests — Priority

```
tests/
├── test_auth.py              ← JWT login, signup, roles
├── test_daily_report_flow.py ← SE submit → PM → OM → MD chain
├── test_attendance.py        ← check-in, check-out, hours calculation
├── test_trip_sheets.py       ← driver start/end trip
├── test_fund_allotment.py    ← allotment + release
├── test_tender_workflow.py   ← draft → submit → approved
└── test_exports.py           ← Excel/PDF generation
```

---

## 📋 IMPLEMENTATION PRIORITY ORDER

| Phase | Items | Timeline Estimate |
|---|---|---|
| **Phase 1** | Extend roles + permissions, Work Status on Tasks, Attendance improvements, Daily Report flow, Export APIs | Week 1–2 |
| **Phase 2** | Transport app (Vehicles, Trip Sheets, Fuel Logs), Meeting app, Reports app | Week 3–4 |
| **Phase 3** | Government Relations, Fund Management, Investor Relations | Week 5–6 |
| **Phase 4** | Quantity Survey, Drawings, Estimation apps | Week 7–8 |
| **Phase 5** | Frontend — Role dashboards (MD, PM, Site, Driver, Transport) | Week 9–11 |
| **Phase 6** | Frontend — Admin/Office pages, QS, Draftsman, Estimation pages | Week 12–13 |
| **Phase 7** | Testing, Production hardening, Deployment | Week 14 |

---

## 📞 TOTAL STAFF MAPPING (15 Users — Account → Grade)

```
ACCOUNT: md  (Managing Director)
└── md_head   →  Managing Director                          × 1

ACCOUNT: admin  (Admin Team — Office Operations)
├── admin_head →  Office Manager                            × 1
├── admin_a1   →  Assistant A1 (Documentation)              × 1
│               Duties: Work status Excel, tender docs,
│               progress reports, bill filing, govt docs
└── admin_a2   →  Assistant A2 (Coordination)               × 1
                Duties: Contractor follow-up, material
                delivery, site updates, labour attendance,
                vehicle & logistics coordination

ACCOUNT: technical  (Technical Team — Site Operations)
├── tech_head  →  Project Manager (Technical Head)          × 1
│               Duties: Project planning, site engineer
│               supervision, progress monitoring,
│               quality control & safety, weekly report
├── tech_se    →  Site Engineer / Supervisor                 × 3
│               (Site Engineer 1, Site Engineer 2, Site Engineer 3)
│               Duties: Daily site supervision, labour
│               management, work measurement, engineer
│               inspection coordination, daily progress report
├── tech_qs    →  Quantity Surveyor         [As Required]
├── tech_cd    →  Civil Draftsman           [As Required]
├── tech_ee    →  Estimation Engineer       [As Required]
├── tech_so    →  Safety Officer
├── tech_qi    →  Quality Inspector
├── tech_fm    →  Foreman
├── tech_sc    →  Subcontractor
└── tech_wk    →  Worker

ACCOUNT: transport  (Transport & Machinery — Logistics)
├── tr_head    →  Transport & Machinery Manager             × 1
│               Duties: Vehicle & machinery management,
│               drivers supervision, fuel monitoring,
│               maintenance planning, vehicle allocation
└── tr_do      →  Driver / Operator                         × 6
                Duties: Tipper trucks, excavator/JCB,
                concrete mixer, site material transport,
                vehicle daily check, trip sheet & daily report
```

### Core Staff Count

| Account | Grade | Role Title | Count |
|---|---|---|---|
| `md` | `md_head` | Managing Director | **1** |
| `admin` | `admin_head` | Office Manager | **1** |
| `admin` | `admin_a1` | Assistant A1 | **1** |
| `admin` | `admin_a2` | Assistant A2 | **1** |
| `technical` | `tech_head` | Project Manager | **1** |
| `technical` | `tech_se` | Site Engineer | **3** |
| `transport` | `tr_head` | Transport Manager | **1** |
| `transport` | `tr_do` | Driver / Operator | **6** |
| | | **TOTAL CORE STAFF** | **15** |

> Technical Support (`tech_qs`, `tech_cd`, `tech_ee`) and field roles (`tech_so`, `tech_qi`, `tech_fm`, `tech_sc`, `tech_wk`) are created as on-demand accounts under the **technical** account type.

---

*This plan fully covers the Beemji Enterprise org chart requirements and maps every role, workflow, reporting chain, and module to concrete backend APIs and frontend pages. Implement in the phased order above for fastest path to a working system.*

---
**Beemji Enterprise Construction Management System**  
*Quality Construction • Timely Completion • Transparency • Growth*  
*Building a Better Tomorrow — Developing Tamil Nadu*
