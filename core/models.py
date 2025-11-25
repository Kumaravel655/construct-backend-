from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from math import radians, cos, sin, asin, sqrt


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('project_manager', 'Project Manager'),
        ('site_engineer', 'Site Engineer'),
        ('foreman', 'Foreman'),
        ('subcontractor', 'Subcontractor'),
        ('worker', 'Worker'),
        ('safety_officer', 'Safety Officer'),
        ('quality_inspector', 'Quality Inspector'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    phone = models.CharField(max_length=15, blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    is_active_employee = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROJECT_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
    ]
    
    name = models.CharField(max_length=255)
    project_code = models.CharField(max_length=20, unique=True, default='PROJ000')
    client = models.CharField(max_length=255)
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='commercial')
    description = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    actual_start_date = models.DateField(blank=True, null=True)
    actual_end_date = models.DateField(blank=True, null=True)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_code} - {self.name}"
    
    @property
    def progress_percentage(self):
        total_tasks = self.task_set.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.task_set.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 2)


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latitude = models.FloatField()
    longitude = models.FloatField()
    verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendance')
    
    class Meta:
        unique_together = ['user', 'project', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.date})"

    def is_within_project_radius(self, max_distance_m=100):
        if not self.project.latitude or not self.project.longitude:
            return False
        lat1, lon1, lat2, lon2 = map(radians, [self.latitude, self.longitude, self.project.latitude, self.project.longitude])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371000
        distance = c * r
        return distance <= max_distance_m


class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_code = models.CharField(max_length=20, default='T000')
    title = models.CharField(max_length=255, default='New Task')
    description = models.TextField(default='')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    actual_start_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    dependencies = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'task_code']

    def __str__(self):
        return f"{self.task_code} - {self.title}"


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('blueprint', 'Blueprint'),
        ('contract', 'Contract'),
        ('permit', 'Permit'),
        ('inspection_report', 'Inspection Report'),
        ('safety_report', 'Safety Report'),
        ('progress_report', 'Progress Report'),
        ('invoice', 'Invoice'),
        ('specification', 'Specification'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other')
    title = models.CharField(max_length=255, default='Untitled Document')
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} v{self.version}"


class Vendor(models.Model):
    VENDOR_TYPE_CHOICES = [
        ('supplier', 'Material Supplier'),
        ('subcontractor', 'Subcontractor'),
        ('equipment_rental', 'Equipment Rental'),
        ('service_provider', 'Service Provider'),
    ]
    
    name = models.CharField(max_length=255)
    vendor_code = models.CharField(max_length=20, unique=True)
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPE_CHOICES, default='supplier')
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    tax_id = models.CharField(max_length=50, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vendor_code} - {self.name}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Vendor'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=20, unique=True, default='PO000')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_pos')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    description = models.TextField(default='')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField(default=timezone.now)
    actual_delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.po_number} - {self.vendor.name}"


class Budget(models.Model):
    CATEGORY_CHOICES = [
        ('labor', 'Labor'),
        ('materials', 'Materials'),
        ('equipment', 'Equipment'),
        ('subcontractor', 'Subcontractor'),
        ('overhead', 'Overhead'),
        ('contingency', 'Contingency'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='materials')
    description = models.CharField(max_length=255, default='')
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    committed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fiscal_year = models.IntegerField(default=2024)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'category', 'fiscal_year']
    
    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount - self.committed_amount
    
    def __str__(self):
        return f"{self.project.name} - {self.category} ({self.fiscal_year})"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True, default='INV000')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(default='')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    paid_date = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.vendor.name}"


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ]
    
    equipment_id = models.CharField(max_length=20, unique=True, default='EQ000')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default='General')
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.equipment_id} - {self.name}"


class SafetyIncident(models.Model):
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    incident_id = models.CharField(max_length=20, unique=True, default='INC000')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='Safety Incident')
    description = models.TextField(default='')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='minor')
    location_details = models.TextField(default='Not specified')
    injured_person = models.CharField(max_length=255, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_incidents')
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_incidents')
    incident_date = models.DateTimeField(default=timezone.now)
    reported_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    corrective_actions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"


class Communication(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('general', 'General'),
        ('urgent', 'Urgent'),
        ('safety_alert', 'Safety Alert'),
        ('progress_update', 'Progress Update'),
        ('issue_report', 'Issue Report'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receivers = models.ManyToManyField(User, related_name='received_messages')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='general')
    subject = models.CharField(max_length=255, default='No Subject')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject} - {self.sender.username}"


class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True, default='MR000')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    material_description = models.TextField(default='')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=20, default='pcs')
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    urgency = models.CharField(max_length=20, choices=Task.PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    required_date = models.DateField(default=timezone.now)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_material_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request_id} - {self.material_description[:30]}"


class QualityInspection(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('rework_required', 'Rework Required'),
    ]
    
    inspection_id = models.CharField(max_length=20, unique=True, default='QI000')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    inspector = models.ForeignKey(User, on_delete=models.CASCADE)
    inspection_type = models.CharField(max_length=100, default='General Inspection')
    scheduled_date = models.DateField(default=timezone.now)
    actual_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    checklist_items = models.TextField(default='')
    observations = models.TextField(blank=True)
    defects_found = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    score = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.inspection_id} - {self.inspection_type}"