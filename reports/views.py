from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exports import export_rows_to_excel
from core.models import Task

from .models import DailyWorkReport
from .serializers import DailyWorkReportSerializer


class DailyWorkReportViewSet(viewsets.ModelViewSet):
	queryset = DailyWorkReport.objects.all().order_by('-report_date', '-created_at')
	serializer_class = DailyWorkReportSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		project_id = self.request.query_params.get('project')
		report_date = self.request.query_params.get('date')
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		if report_date:
			queryset = queryset.filter(report_date=report_date)
		return queryset

	@action(detail=True, methods=['post'])
	def submit(self, request, pk=None):
		report = self.get_object()
		report.status = 'submitted'
		report.submitted_by = request.user
		report.save(update_fields=['status', 'submitted_by'])
		return Response(self.get_serializer(report).data)

	@action(detail=True, methods=['post'], url_path='pm-review')
	def pm_review(self, request, pk=None):
		report = self.get_object()
		report.status = 'pm_reviewed'
		report.pm_remarks = request.data.get('remarks', '')
		report.pm_reviewed_by = request.user
		report.pm_reviewed_at = timezone.now()
		report.save(update_fields=['status', 'pm_remarks', 'pm_reviewed_by', 'pm_reviewed_at'])
		return Response(self.get_serializer(report).data)

	@action(detail=True, methods=['post'], url_path='om-consolidate')
	def om_consolidate(self, request, pk=None):
		report = self.get_object()
		report.status = 'om_consolidated'
		report.om_remarks = request.data.get('remarks', '')
		report.om_reviewed_by = request.user
		report.om_reviewed_at = timezone.now()
		report.save(update_fields=['status', 'om_remarks', 'om_reviewed_by', 'om_reviewed_at'])
		return Response(self.get_serializer(report).data)

	@action(detail=True, methods=['post'], url_path='md-review')
	def md_review(self, request, pk=None):
		report = self.get_object()
		report.status = 'md_reviewed'
		report.md_remarks = request.data.get('remarks', '')
		report.md_reviewed_by = request.user
		report.md_reviewed_at = timezone.now()
		report.save(update_fields=['status', 'md_remarks', 'md_reviewed_by', 'md_reviewed_at'])
		return Response(self.get_serializer(report).data)

	@action(detail=False, methods=['get'], url_path='pending-review')
	def pending_review(self, request):
		data = {
			'pm_pending': self.get_queryset().filter(status='submitted').count(),
			'om_pending': self.get_queryset().filter(status='pm_reviewed').count(),
			'md_pending': self.get_queryset().filter(status='om_consolidated').count(),
		}
		return Response(data)

	@action(detail=True, methods=['post'], url_path='export-pdf')
	def export_pdf(self, request, pk=None):
		report = self.get_object()
		return Response({'message': 'PDF export endpoint is ready for integration', 'report_id': report.report_id})

	@action(detail=False, methods=['get'], url_path='export-excel')
	def export_excel(self, request):
		queryset = self.get_queryset().select_related('project', 'submitted_by')
		headers = [
			'Report ID',
			'Project',
			'Date',
			'Status',
			'Submitted By',
			'Workers Present',
			'Workers Absent',
			'Subcontractor Workers',
			'Overall Progress %',
		]
		rows = [
			[
				obj.report_id,
				obj.project.name,
				obj.report_date,
				obj.status,
				obj.submitted_by.username if obj.submitted_by else '',
				obj.total_workers_present,
				obj.total_workers_absent,
				obj.subcontractor_workers,
				obj.overall_progress_percentage,
			]
			for obj in queryset
		]
		return export_rows_to_excel('daily_reports.xlsx', headers, rows)


class WorkStatusSummaryView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		project_id = request.query_params.get('project')
		queryset = Task.objects.all()
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		summary = queryset.values('work_status').annotate(count=Count('id')).order_by('work_status')
		return Response({'summary': list(summary)})
