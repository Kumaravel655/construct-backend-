from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db import models
from django.contrib.auth.models import AbstractUser
from math import radians, cos, sin, asin, sqrt


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('site_engineer', 'Site Engineer'),
        ('subcontractor', 'Subcontractor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='site_engineer')
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Project(models.Model):
    name = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    latitude = models.FloatField()
    longitude = models.FloatField()
    verified = models.BooleanField(default=False)  # will store if geo verified

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.date})"

    def is_within_project_radius(self, max_distance_m=100):
        """
        Check if this attendance location is within allowed distance of project site.
        Uses the Haversine formula.
        """
        if not self.project.latitude or not self.project.longitude:
            return False

        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [self.latitude, self.longitude, self.project.latitude, self.project.longitude])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth radius in meters
        distance = c * r

        return distance <= max_distance_m



# ---------------- TASKS ----------------
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.project.name} - {self.description[:20]}"


# ---------------- DOCUMENTS ----------------
class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)
    version = models.CharField(max_length=10)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)


# ---------------- VENDORS ----------------
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    service_type = models.CharField(max_length=255)


# ---------------- PURCHASE ORDERS ----------------
class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    created_date = models.DateField(auto_now_add=True)


# ---------------- BUDGETS ----------------
class Budget(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount_allocated = models.DecimalField(max_digits=12, decimal_places=2)
    amount_spent = models.DecimalField(max_digits=12, decimal_places=2)
    fiscal_year = models.IntegerField()


 

# ---------------- INVOICES ----------------
class Invoice(models.Model):
    subcontractor = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    due_date = models.DateField()


# ---------------- EQUIPMENT ----------------
class Equipment(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


# ---------------- SAFETY INCIDENTS ----------------
class SafetyIncident(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    status = models.CharField(max_length=50)


# ---------------- COMMUNICATIONS ----------------
class Communication(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
