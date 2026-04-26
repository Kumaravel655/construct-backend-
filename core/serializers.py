from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    GRADE_TO_ACCOUNT,
    Attendance,
    AttendanceSession,
    Budget,
    Communication,
    DailyWorkItem,
    Document,
    Equipment,
    Invoice,
    MaterialRequest,
    Project,
    PurchaseOrder,
    QualityInspection,
    SafetyIncident,
    Task,
    User,
    Vendor,
)

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    authority_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserModel
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'account_type',
            'account_type_display',
            'grade',
            'grade_display',
            'authority_level',
            'phone',
            'employee_id',
            'department',
            'hire_date',
            'is_active_employee',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        grade = attrs.get('grade', getattr(self.instance, 'grade', None))
        account_type = attrs.get('account_type', getattr(self.instance, 'account_type', None))
        expected_account = GRADE_TO_ACCOUNT.get(grade)
        if expected_account and account_type and expected_account != account_type:
            raise serializers.ValidationError(
                {'grade': f"Grade '{grade}' must belong to account '{expected_account}'"}
            )
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = [
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'account_type',
            'grade',
            'phone',
            'employee_id',
            'department',
        ]

    def validate(self, attrs):
        grade = attrs.get('grade', 'tech_wk')
        account_type = attrs.get('account_type', 'technical')
        expected_account = GRADE_TO_ACCOUNT.get(grade)
        if expected_account and expected_account != account_type:
            raise serializers.ValidationError(
                {'grade': f"Grade '{grade}' must belong to account '{expected_account}'"}
            )
        return attrs

    def create(self, validated_data):
        return UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            account_type=validated_data.get('account_type', 'technical'),
            grade=validated_data.get('grade', 'tech_wk'),
            phone=validated_data.get('phone', ''),
            employee_id=validated_data.get('employee_id', ''),
            department=validated_data.get('department', ''),
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
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
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    status = serializers.ReadOnlyField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'user',
            'project',
            'date',
            'check_in_time',
            'check_out_time',
            'latitude',
            'longitude',
            'hours_worked',
            'overtime_hours',
            'notes',
            'attendance_type',
            'contractor_name',
            'work_category',
            'daily_wage',
            'is_approved',
            'approved_by',
            'user_name',
            'project_name',
            'approved_by_name',
            'status',
        ]
        read_only_fields = ['id', 'date', 'hours_worked', 'overtime_hours']

    def update(self, instance, validated_data):
        updated = super().update(instance, validated_data)
        if updated.check_out_time:
            updated.calculate_hours()
        return updated


class AttendanceSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = [
            'id',
            'user',
            'user_name',
            'project',
            'project_name',
            'session_date',
            'sequence_no',
            'location_type',
            'check_in_at',
            'check_out_at',
            'check_in_latitude',
            'check_in_longitude',
            'check_out_latitude',
            'check_out_longitude',
            'check_in_address',
            'check_out_address',
            'travel_km',
            'status',
            'late_flag',
            'early_flag',
            'duration_hours',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'session_date',
            'sequence_no',
            'status',
            'late_flag',
            'early_flag',
            'duration_hours',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        check_in_at = attrs.get('check_in_at', getattr(self.instance, 'check_in_at', None))
        check_out_at = attrs.get('check_out_at', getattr(self.instance, 'check_out_at', None))
        if check_in_at and check_out_at and check_out_at <= check_in_at:
            raise serializers.ValidationError({'check_out_at': 'check_out_at must be later than check_in_at'})
        return attrs

    def get_duration_hours(self, obj):
        return obj.duration_hours


class AttendanceSessionCheckInSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    location_type = serializers.ChoiceField(choices=AttendanceSession.LOCATION_TYPE_CHOICES)
    check_in_at = serializers.DateTimeField(required=False)
    check_in_latitude = serializers.FloatField()
    check_in_longitude = serializers.FloatField()
    check_in_address = serializers.CharField(required=False, allow_blank=True, max_length=255)
    travel_km = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.00'))
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        lat = attrs.get('check_in_latitude')
        lng = attrs.get('check_in_longitude')
        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({'check_in_latitude': 'Latitude must be between -90 and 90'})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({'check_in_longitude': 'Longitude must be between -180 and 180'})
        return attrs


class AttendanceSessionCheckOutSerializer(serializers.Serializer):
    check_out_at = serializers.DateTimeField(required=False)
    check_out_latitude = serializers.FloatField(required=False)
    check_out_longitude = serializers.FloatField(required=False)
    check_out_address = serializers.CharField(required=False, allow_blank=True, max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        has_lat = 'check_out_latitude' in attrs
        has_lng = 'check_out_longitude' in attrs
        if has_lat != has_lng:
            raise serializers.ValidationError('Both check_out_latitude and check_out_longitude are required together')

        lat = attrs.get('check_out_latitude')
        lng = attrs.get('check_out_longitude')
        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({'check_out_latitude': 'Latitude must be between -90 and 90'})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({'check_out_longitude': 'Longitude must be between -180 and 180'})
        return attrs


class DailyWorkItemSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DailyWorkItem
        fields = [
            'id',
            'user',
            'user_name',
            'project',
            'project_name',
            'work_date',
            'title',
            'description',
            'status',
            'started_at',
            'completed_at',
            'blocker_note',
            'priority',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        status_value = attrs.get('status', getattr(self.instance, 'status', 'not_started'))
        if status_value == 'blocked' and not attrs.get('blocker_note', getattr(self.instance, 'blocker_note', '')):
            raise serializers.ValidationError({'blocker_note': 'blocker_note is required when status is blocked'})
        return attrs

    def update(self, instance, validated_data):
        updated = super().update(instance, validated_data)
        if updated.status == 'in_progress' and not updated.started_at:
            updated.started_at = timezone.now()
            updated.save(update_fields=['started_at', 'updated_at'])
        if updated.status == 'done' and not updated.completed_at:
            if not updated.started_at:
                updated.started_at = timezone.now()
            updated.completed_at = timezone.now()
            updated.blocker_note = ''
            updated.save(update_fields=['started_at', 'completed_at', 'blocker_note', 'updated_at'])
        return updated


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
