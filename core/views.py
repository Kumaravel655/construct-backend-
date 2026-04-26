from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import Max, Q
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .exports import export_rows_to_excel
from .models import (
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
from .serializers import (
    AttendanceSerializer,
    AttendanceSessionCheckInSerializer,
    AttendanceSessionCheckOutSerializer,
    AttendanceSessionSerializer,
    BudgetSerializer,
    CommunicationSerializer,
    DailyWorkItemSerializer,
    DocumentSerializer,
    EquipmentSerializer,
    InvoiceSerializer,
    LoginSerializer,
    MaterialRequestSerializer,
    ProjectSerializer,
    PurchaseOrderSerializer,
    QualityInspectionSerializer,
    RegisterSerializer,
    SafetyIncidentSerializer,
    TaskSerializer,
    UserSerializer,
    VendorSerializer,
)


ADMIN_ACCOUNTS = {'md', 'admin'}


def is_admin_account(user):
    return user.is_authenticated and user.account_type in ADMIN_ACCOUNTS


def grace_minutes():
    return int(getattr(settings, 'ATTENDANCE_GRACE_MINUTES', 20))


def checkin_target_hour():
    return int(getattr(settings, 'ATTENDANCE_CHECKIN_TARGET_HOUR', 9))


def checkout_target_hour():
    return int(getattr(settings, 'ATTENDANCE_CHECKOUT_TARGET_HOUR', 18))


def is_late_checkin(check_in_dt):
    local_dt = timezone.localtime(check_in_dt)
    threshold = datetime.combine(local_dt.date(), datetime.min.time()).replace(hour=checkin_target_hour()) + timedelta(
        minutes=grace_minutes()
    )
    threshold = timezone.make_aware(threshold, timezone.get_current_timezone())
    return local_dt > threshold


def is_early_checkout(check_out_dt):
    local_dt = timezone.localtime(check_out_dt)
    threshold = datetime.combine(local_dt.date(), datetime.min.time()).replace(hour=checkout_target_hour()) - timedelta(
        minutes=grace_minutes()
    )
    threshold = timezone.make_aware(threshold, timezone.get_current_timezone())
    return local_dt < threshold


def build_day_summary(sessions):
    total_distance_km = sessions.aggregate(total=Sum('travel_km')).get('total') or Decimal('0.00')
    total_seconds = 0
    for session in sessions:
        if session.check_out_at:
            total_seconds += max((session.check_out_at - session.check_in_at).total_seconds(), 0)

    total_duration_hours = round(total_seconds / 3600, 2)
    first_session = sessions.order_by('check_in_at').first()
    last_closed = sessions.filter(check_out_at__isnull=False).order_by('-check_out_at').first()

    return {
        'total_sessions': sessions.count(),
        'open_sessions': sessions.filter(status='open').count(),
        'total_distance_km': total_distance_km,
        'total_duration_hours': total_duration_hours,
        'late_flag': bool(first_session.late_flag) if first_session else False,
        'early_flag': is_early_checkout(last_closed.check_out_at) if last_closed else False,
    }


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class DashboardSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def _common_summary(self, user):
        today = timezone.localdate().isoformat()

        my_tasks = Task.objects.filter(assigned_to=user)
        my_work_items_today = DailyWorkItem.objects.filter(user=user, work_date=today)
        my_sessions_today = AttendanceSession.objects.filter(user=user, session_date=today).order_by('check_in_at')
        unread_messages = Communication.objects.filter(receivers=user, is_read=False).distinct().count()
        open_session = AttendanceSession.objects.filter(user=user, status='open').order_by('-check_in_at').first()

        return {
            'date': today,
            'user': {
                'id': user.id,
                'username': user.username,
                'account_type': user.account_type,
                'grade': user.grade,
                'authority_level': user.authority_level,
            },
            'my_tasks': {
                'total': my_tasks.count(),
                'not_started': my_tasks.filter(status='not_started').count(),
                'in_progress': my_tasks.filter(status='in_progress').count(),
                'completed': my_tasks.filter(status='completed').count(),
                'critical': my_tasks.filter(priority='critical').count(),
            },
            'my_daily_work_items': {
                'total': my_work_items_today.count(),
                'not_started': my_work_items_today.filter(status='not_started').count(),
                'in_progress': my_work_items_today.filter(status='in_progress').count(),
                'done': my_work_items_today.filter(status='done').count(),
                'blocked': my_work_items_today.filter(status='blocked').count(),
            },
            'my_attendance': {
                'has_open_session': bool(open_session),
                'open_session_id': open_session.id if open_session else None,
                'day_summary': build_day_summary(my_sessions_today),
            },
            'unread_messages': unread_messages,
        }

    def _admin_summary(self, today):
        return {
            'organization': {
                'total_users': User.objects.count(),
                'head_count_by_account': list(
                    User.objects.values('account_type').annotate(count=Count('id')).order_by('account_type')
                ),
                'head_count_by_grade': list(User.objects.values('grade').annotate(count=Count('id')).order_by('grade')),
            },
            'operations': {
                'active_projects': Project.objects.filter(status='active').count(),
                'open_attendance_sessions': AttendanceSession.objects.filter(status='open').count(),
                'today_attendance_sessions': AttendanceSession.objects.filter(session_date=today).count(),
                'blocked_work_items_today': DailyWorkItem.objects.filter(work_date=today, status='blocked').count(),
            },
            'approvals': {
                'invoices_submitted': Invoice.objects.filter(status='submitted').count(),
                'purchase_orders_pending_approval': PurchaseOrder.objects.filter(status='pending_approval').count(),
                'material_requests_pending': MaterialRequest.objects.filter(status='pending').count(),
            },
            'risk': {
                'open_incidents': SafetyIncident.objects.filter(status__in=['reported', 'investigating']).count(),
                'quality_rework_required': QualityInspection.objects.filter(status='rework_required').count(),
            },
        }

    def _technical_summary(self, user, today):
        team_scope = Q(assigned_to__account_type='technical')
        return {
            'execution': {
                'my_projects_active': Project.objects.filter(project_manager=user, status='active').count(),
                'team_tasks_in_progress': Task.objects.filter(team_scope, status='in_progress').count(),
                'critical_tasks_open': Task.objects.filter(team_scope, priority='critical').exclude(status='completed').count(),
                'today_blocked_work_items': DailyWorkItem.objects.filter(
                    user__account_type='technical', work_date=today, status='blocked'
                ).count(),
            },
            'quality_and_safety': {
                'incidents_open': SafetyIncident.objects.filter(status__in=['reported', 'investigating']).count(),
                'inspections_pending': QualityInspection.objects.filter(status__in=['scheduled', 'in_progress']).count(),
                'inspections_failed_or_rework': QualityInspection.objects.filter(
                    status__in=['failed', 'rework_required']
                ).count(),
            },
            'attendance': {
                'team_open_sessions': AttendanceSession.objects.filter(user__account_type='technical', status='open').count(),
                'team_today_sessions': AttendanceSession.objects.filter(user__account_type='technical', session_date=today).count(),
            },
        }

    def _transport_summary(self, user, today):
        return {
            'fleet': {
                'total_equipment': Equipment.objects.count(),
                'available': Equipment.objects.filter(status='available').count(),
                'in_use': Equipment.objects.filter(status='in_use').count(),
                'maintenance_or_repair': Equipment.objects.filter(status__in=['maintenance', 'repair']).count(),
                'assigned_to_me': Equipment.objects.filter(assigned_to=user).count(),
            },
            'operations': {
                'transport_team_open_sessions': AttendanceSession.objects.filter(
                    user__account_type='transport', status='open'
                ).count(),
                'transport_team_today_sessions': AttendanceSession.objects.filter(
                    user__account_type='transport', session_date=today
                ).count(),
                'my_work_items_today': DailyWorkItem.objects.filter(user=user, work_date=today).count(),
            },
        }

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate().isoformat()

        payload = {
            'dashboard_type': user.account_type,
            'common': self._common_summary(user),
        }

        if user.account_type in ADMIN_ACCOUNTS:
            payload['role_summary'] = self._admin_summary(today)
        elif user.account_type == 'technical':
            payload['role_summary'] = self._technical_summary(user, today)
        elif user.account_type == 'transport':
            payload['role_summary'] = self._transport_summary(user, today)
        else:
            payload['role_summary'] = {}

        return Response(payload, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        account_type = self.request.query_params.get('account_type')
        grade = self.request.query_params.get('grade')

        if account_type:
            queryset = queryset.filter(account_type=account_type)
        if grade:
            queryset = queryset.filter(grade=grade)
        return queryset

    @action(detail=False, methods=['get'])
    def team_summary(self, request):
        by_account = User.objects.values('account_type').annotate(count=Count('id')).order_by('account_type')
        by_grade = User.objects.values('grade').annotate(count=Count('id')).order_by('grade')
        return Response(
            {
                'total_users': User.objects.count(),
                'by_account_type': list(by_account),
                'by_grade': list(by_grade),
            }
        )


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        queryset = self.get_queryset().select_related('project_manager')
        headers = [
            'ID',
            'Project Code',
            'Name',
            'Client',
            'Project Manager',
            'Type',
            'Status',
            'Start Date',
            'End Date',
            'Total Budget',
            'Progress %',
        ]
        rows = [
            [
                obj.id,
                obj.project_code,
                obj.name,
                obj.client,
                obj.project_manager.username if obj.project_manager else '',
                obj.project_type,
                obj.status,
                obj.start_date,
                obj.end_date,
                obj.total_budget,
                obj.progress_percentage,
            ]
            for obj in queryset
        ]
        return export_rows_to_excel('projects.xlsx', headers, rows)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-upload_date')
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by('-created_at')
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all().order_by('-created_at')
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        queryset = self.get_queryset().select_related('project')
        project_id = request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        headers = [
            'ID',
            'Project',
            'Category',
            'Description',
            'Allocated',
            'Spent',
            'Committed',
            'Remaining',
            'Fiscal Year',
        ]
        rows = [
            [
                obj.id,
                obj.project.name,
                obj.category,
                obj.description,
                obj.allocated_amount,
                obj.spent_amount,
                obj.committed_amount,
                obj.remaining_amount,
                obj.fiscal_year,
            ]
            for obj in queryset
        ]
        return export_rows_to_excel('budgets.xlsx', headers, rows)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        queryset = self.get_queryset().select_related('project', 'vendor')
        headers = [
            'ID',
            'Invoice Number',
            'Project',
            'Vendor',
            'Status',
            'Subtotal',
            'Tax',
            'Total',
            'Invoice Date',
            'Due Date',
        ]
        rows = [
            [
                obj.id,
                obj.invoice_number,
                obj.project.name,
                obj.vendor.name,
                obj.status,
                obj.subtotal,
                obj.tax_amount,
                obj.total_amount,
                obj.invoice_date,
                obj.due_date,
            ]
            for obj in queryset
        ]
        return export_rows_to_excel('invoices.xlsx', headers, rows)


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('equipment_id')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]


class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all().order_by('-reported_date')
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsAuthenticated]


class CommunicationViewSet(viewsets.ModelViewSet):
    queryset = Communication.objects.all().order_by('-timestamp')
    serializer_class = CommunicationSerializer
    permission_classes = [IsAuthenticated]


class MaterialRequestViewSet(viewsets.ModelViewSet):
    queryset = MaterialRequest.objects.all().order_by('-created_at')
    serializer_class = MaterialRequestSerializer
    permission_classes = [IsAuthenticated]


class QualityInspectionViewSet(viewsets.ModelViewSet):
    queryset = QualityInspection.objects.all().order_by('-created_at')
    serializer_class = QualityInspectionSerializer
    permission_classes = [IsAuthenticated]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-created_at')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        return queryset

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def check_out(self, request, pk=None):
        attendance = self.get_object()
        if attendance.check_out_time:
            return Response({'error': 'Already checked out'}, status=status.HTTP_400_BAD_REQUEST)

        check_out_time = request.data.get('check_out_time')
        if check_out_time:
            attendance.check_out_time = datetime.strptime(check_out_time, '%H:%M:%S').time()
        else:
            attendance.check_out_time = timezone.localtime().time().replace(microsecond=0)

        attendance.calculate_hours()
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-checkin')
    def bulk_checkin(self, request):
        entries = request.data.get('entries', [])
        if not isinstance(entries, list) or not entries:
            return Response({'error': 'entries must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []

        for index, entry in enumerate(entries):
            payload = dict(entry)
            payload.setdefault('user', request.user.id)
            serializer = self.get_serializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                created_items.append(serializer.data)
            else:
                errors.append({'index': index, 'errors': serializer.errors})

        if errors:
            return Response(
                {'created_count': len(created_items), 'errors': errors, 'created': created_items},
                status=status.HTTP_207_MULTI_STATUS,
            )
        return Response({'created_count': len(created_items), 'created': created_items}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='labour-summary')
    def labour_summary(self, request):
        queryset = self.get_queryset()
        attendance_type_summary = list(
            queryset.values('attendance_type')
            .annotate(total=Count('id'), wage_total=Sum('daily_wage'))
            .order_by('attendance_type')
        )
        return Response(
            {
                'total_records': queryset.count(),
                'approved_records': queryset.filter(is_approved=True).count(),
                'attendance_type_summary': attendance_type_summary,
            }
        )

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        queryset = self.get_queryset().select_related('user', 'project', 'approved_by')
        headers = [
            'ID',
            'Date',
            'User',
            'Project',
            'Attendance Type',
            'Contractor',
            'Work Category',
            'Check In',
            'Check Out',
            'Hours',
            'Overtime',
            'Daily Wage',
            'Approved',
            'Approved By',
        ]
        rows = [
            [
                obj.id,
                obj.date,
                obj.user.username,
                obj.project.name,
                obj.attendance_type,
                obj.contractor_name,
                obj.work_category,
                obj.check_in_time,
                obj.check_out_time,
                obj.hours_worked,
                obj.overtime_hours,
                obj.daily_wage,
                obj.is_approved,
                obj.approved_by.username if obj.approved_by else '',
            ]
            for obj in queryset
        ]
        return export_rows_to_excel('attendance.xlsx', headers, rows)


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.select_related('user', 'project').all().order_by('-check_in_at')
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        date_value = self.request.query_params.get('date')
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        location_type = self.request.query_params.get('location_type')
        status_value = self.request.query_params.get('status')

        if not is_admin_account(user):
            queryset = queryset.filter(user=user)
        elif user_id:
            queryset = queryset.filter(user_id=user_id)

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if date_value:
            queryset = queryset.filter(session_date=date_value)
        if from_date:
            queryset = queryset.filter(session_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(session_date__lte=to_date)
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def get_object(self):
        obj = super().get_object()
        if not is_admin_account(self.request.user) and obj.user_id != self.request.user.id:
            raise PermissionDenied('You can only access your own attendance sessions.')
        return obj

    def create(self, request, *args, **kwargs):
        return self.check_in(request)

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        serializer = AttendanceSessionCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if AttendanceSession.objects.filter(user=request.user, status='open').exists():
            return Response(
                {'error': 'You already have an open attendance session. Please check out first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        check_in_at = serializer.validated_data.get('check_in_at', timezone.now())
        local_check_in = timezone.localtime(check_in_at)
        session_date = local_check_in.date()
        max_sequence = (
            AttendanceSession.objects.filter(user=request.user, session_date=session_date)
            .aggregate(max_sequence=Max('sequence_no'))
            .get('max_sequence')
            or 0
        )
        sequence_no = max_sequence + 1

        session = AttendanceSession.objects.create(
            user=request.user,
            project=serializer.validated_data.get('project'),
            session_date=session_date,
            sequence_no=sequence_no,
            location_type=serializer.validated_data['location_type'],
            check_in_at=check_in_at,
            check_in_latitude=serializer.validated_data['check_in_latitude'],
            check_in_longitude=serializer.validated_data['check_in_longitude'],
            check_in_address=serializer.validated_data.get('check_in_address', ''),
            travel_km=serializer.validated_data['travel_km'],
            notes=serializer.validated_data.get('notes', ''),
            late_flag=is_late_checkin(check_in_at) if sequence_no == 1 else False,
        )

        return Response(self.get_serializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='check-out')
    def check_out(self, request, pk=None):
        session = self.get_object()
        if session.check_out_at:
            return Response({'error': 'This session is already checked out.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AttendanceSessionCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        check_out_at = serializer.validated_data.get('check_out_at', timezone.now())
        if check_out_at <= session.check_in_at:
            return Response(
                {'error': 'check_out_at must be after check_in_at.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.check_out_at = check_out_at
        session.check_out_latitude = serializer.validated_data.get('check_out_latitude')
        session.check_out_longitude = serializer.validated_data.get('check_out_longitude')
        session.check_out_address = serializer.validated_data.get('check_out_address', session.check_out_address)

        notes = serializer.validated_data.get('notes')
        if notes is not None:
            session.notes = notes

        session.early_flag = is_early_checkout(check_out_at)
        session.status = 'closed'
        session.save()

        return Response(self.get_serializer(session).data)

    @action(detail=False, methods=['get'], url_path='my-open-session')
    def my_open_session(self, request):
        session = AttendanceSession.objects.filter(user=request.user, status='open').order_by('-check_in_at').first()
        if not session:
            return Response({'detail': 'No open attendance session found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(session).data)

    @action(detail=False, methods=['get'], url_path='my-day-sessions')
    def my_day_sessions(self, request):
        date_value = request.query_params.get('date', timezone.localdate().isoformat())
        sessions = AttendanceSession.objects.filter(user=request.user, session_date=date_value).order_by('sequence_no')
        serialized = self.get_serializer(sessions, many=True)
        return Response({'date': date_value, 'count': len(serialized.data), 'sessions': serialized.data})

    @action(detail=False, methods=['get'], url_path='my-day-summary')
    def my_day_summary(self, request):
        date_value = request.query_params.get('date', timezone.localdate().isoformat())
        sessions = AttendanceSession.objects.filter(user=request.user, session_date=date_value).order_by('check_in_at')
        summary = build_day_summary(sessions)
        summary.update({'date': date_value, 'user_id': request.user.id, 'username': request.user.username})
        return Response(summary)

    @action(detail=False, methods=['get'], url_path='admin-user-day-route')
    def admin_user_day_route(self, request):
        if not is_admin_account(request.user):
            raise PermissionDenied('Admin or MD account is required.')

        user_id = request.query_params.get('user')
        date_value = request.query_params.get('date', timezone.localdate().isoformat())
        if not user_id:
            return Response({'error': 'user query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            return Response({'error': 'user must be a valid integer id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_user = User.objects.get(id=user_id_int)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        sessions = AttendanceSession.objects.filter(user_id=user_id_int, session_date=date_value).order_by('sequence_no')
        summary = build_day_summary(sessions)

        route_points = []
        for session in sessions:
            route_points.append(
                {
                    'session_id': session.id,
                    'event': 'check_in',
                    'location_type': session.location_type,
                    'timestamp': session.check_in_at,
                    'latitude': session.check_in_latitude,
                    'longitude': session.check_in_longitude,
                }
            )
            if session.check_out_at and session.check_out_latitude is not None and session.check_out_longitude is not None:
                route_points.append(
                    {
                        'session_id': session.id,
                        'event': 'check_out',
                        'location_type': session.location_type,
                        'timestamp': session.check_out_at,
                        'latitude': session.check_out_latitude,
                        'longitude': session.check_out_longitude,
                    }
                )

        return Response(
            {
                'date': date_value,
                'user': {'id': selected_user.id, 'username': selected_user.username},
                'summary': summary,
                'route_points': route_points,
                'sessions': self.get_serializer(sessions, many=True).data,
            }
        )

    @action(detail=False, methods=['get'], url_path='admin-day-overview')
    def admin_day_overview(self, request):
        if not is_admin_account(request.user):
            raise PermissionDenied('Admin or MD account is required.')

        date_value = request.query_params.get('date', timezone.localdate().isoformat())
        rows = (
            AttendanceSession.objects.filter(session_date=date_value)
            .values('user_id', 'user__username')
            .annotate(
                total_sessions=Count('id'),
                open_sessions=Count('id', filter=Q(status='open')),
                total_distance_km=Sum('travel_km'),
                late_sessions=Count('id', filter=Q(late_flag=True)),
            )
            .order_by('user__username')
        )
        return Response({'date': date_value, 'users': list(rows)})

    @action(detail=False, methods=['get'], url_path='admin-user-distance-trend')
    def admin_user_distance_trend(self, request):
        if not is_admin_account(request.user):
            raise PermissionDenied('Admin or MD account is required.')

        user_id = request.query_params.get('user')
        if not user_id:
            return Response({'error': 'user query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            return Response({'error': 'user must be a valid integer id.'}, status=status.HTTP_400_BAD_REQUEST)

        end_date = request.query_params.get('end', timezone.localdate().isoformat())
        start_date = request.query_params.get(
            'start',
            (timezone.localdate() - timedelta(days=6)).isoformat(),
        )

        trend = (
            AttendanceSession.objects.filter(user_id=user_id_int, session_date__gte=start_date, session_date__lte=end_date)
            .values('session_date')
            .annotate(total_distance_km=Sum('travel_km'), total_sessions=Count('id'))
            .order_by('session_date')
        )
        return Response({'user_id': user_id_int, 'start': start_date, 'end': end_date, 'days': list(trend)})


class DailyWorkItemViewSet(viewsets.ModelViewSet):
    queryset = DailyWorkItem.objects.select_related('user', 'project', 'created_by').all().order_by('-work_date', '-created_at')
    serializer_class = DailyWorkItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        work_date = self.request.query_params.get('work_date')
        status_value = self.request.query_params.get('status')

        if not is_admin_account(user):
            queryset = queryset.filter(user=user)
        elif user_id:
            queryset = queryset.filter(user_id=user_id)

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if work_date:
            queryset = queryset.filter(work_date=work_date)
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def get_object(self):
        obj = super().get_object()
        if not is_admin_account(self.request.user) and obj.user_id != self.request.user.id:
            raise PermissionDenied('You can only access your own daily worklist entries.')
        return obj

    def perform_create(self, serializer):
        requested_user_id = self.request.data.get('user')
        target_user = self.request.user

        if requested_user_id and is_admin_account(self.request.user):
            try:
                target_user = User.objects.get(id=requested_user_id)
            except User.DoesNotExist as exc:
                raise PermissionDenied('Requested user was not found.') from exc
        elif requested_user_id and str(requested_user_id) != str(self.request.user.id):
            raise PermissionDenied('You can only create entries for yourself.')

        serializer.save(user=target_user, created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-day')
    def my_day(self, request):
        date_value = request.query_params.get('date', timezone.localdate().isoformat())
        queryset = DailyWorkItem.objects.filter(user=request.user, work_date=date_value).order_by('created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response({'date': date_value, 'count': len(serializer.data), 'items': serializer.data})

    @action(detail=True, methods=['patch'], url_path='start')
    def start(self, request, pk=None):
        item = self.get_object()
        if item.status == 'done':
            return Response(
                {'error': 'Completed entries can only be reopened by admin.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.status = 'in_progress'
        if not item.started_at:
            item.started_at = timezone.now()
        item.blocker_note = ''
        item.save()
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['patch'], url_path='complete')
    def complete(self, request, pk=None):
        item = self.get_object()
        item.status = 'done'
        if not item.started_at:
            item.started_at = timezone.now()
        item.completed_at = timezone.now()
        item.blocker_note = ''
        item.save()
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['patch'], url_path='block')
    def block(self, request, pk=None):
        item = self.get_object()
        blocker_note = str(request.data.get('blocker_note', '')).strip()
        if not blocker_note:
            return Response(
                {'error': 'blocker_note is required to mark an item as blocked.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.status = 'blocked'
        if not item.started_at:
            item.started_at = timezone.now()
        item.blocker_note = blocker_note
        item.completed_at = None
        item.save()
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['patch'], url_path='reopen')
    def reopen(self, request, pk=None):
        if not is_admin_account(request.user):
            raise PermissionDenied('Admin or MD account is required.')

        item = self.get_object()
        item.status = 'in_progress'
        if not item.started_at:
            item.started_at = timezone.now()
        item.completed_at = None
        item.blocker_note = ''
        item.save()
        return Response(self.get_serializer(item).data)

    @action(detail=False, methods=['get'], url_path='admin-team-worklist')
    def admin_team_worklist(self, request):
        if not is_admin_account(request.user):
            raise PermissionDenied('Admin or MD account is required.')

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': len(serializer.data), 'items': serializer.data})
