from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'employee_id', 'department', 'hire_date', 'is_active_employee']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone', 'employee_id', 'department']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'worker'),
            phone=validated_data.get('phone', ''),
            employee_id=validated_data.get('employee_id', ''),
            department=validated_data.get('department', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }

class ProjectSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    project_manager_name = serializers.CharField(source='project_manager.username', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.ReadOnlyField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'project', 'date', 'check_in_time', 'check_out_time', 'latitude', 'longitude', 
                 'hours_worked', 'overtime_hours', 'notes', 'user_name', 'project_name', 'status']
        read_only_fields = ['id', 'date', 'hours_worked', 'overtime_hours']

    def create(self, validated_data):
        attendance = Attendance(**validated_data)
        attendance.save()
        return attendance
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if instance.check_out_time:
            instance.calculate_hours()
        return instance

class InvoiceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    current_project_name = serializers.CharField(source='current_project.name', read_only=True)
    
    class Meta:
        model = Equipment
        fields = '__all__'

class SafetyIncidentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    
    class Meta:
        model = SafetyIncident
        fields = '__all__'

class CommunicationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Communication
        fields = '__all__'

class MaterialRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = MaterialRequest
        fields = '__all__'

class QualityInspectionSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = QualityInspection
        fields = '__all__'
