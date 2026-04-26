from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DailyWorkItem, Project, User


class AttendanceSessionApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='worker1', password='workerpass123')
		self.admin_user = User.objects.create_user(
			username='admin1',
			password='adminpass123',
			account_type='admin',
			grade='admin_head',
		)
		self.project = Project.objects.create(
			name='Tower A',
			project_code='PROJ101',
			client='ACME',
			project_manager=self.user,
			location='Downtown',
		)

	def test_checkin_checkout_flow(self):
		self.client.force_authenticate(user=self.user)

		checkin_payload = {
			'project': self.project.id,
			'location_type': 'site',
			'check_in_latitude': 12.9716,
			'check_in_longitude': 77.5946,
			'travel_km': '0.00',
			'notes': 'Reached project site',
		}
		checkin_response = self.client.post('/api/auth/attendance-sessions/check-in/', checkin_payload, format='json')
		self.assertEqual(checkin_response.status_code, status.HTTP_201_CREATED)
		session_id = checkin_response.data['id']
		self.assertEqual(checkin_response.data['status'], 'open')

		checkout_payload = {
			'check_out_latitude': 12.9720,
			'check_out_longitude': 77.5950,
			'notes': 'Checked out from site',
		}
		checkout_response = self.client.patch(
			f'/api/auth/attendance-sessions/{session_id}/check-out/',
			checkout_payload,
			format='json',
		)
		self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
		self.assertEqual(checkout_response.data['status'], 'closed')

		summary_response = self.client.get(
			f"/api/auth/attendance-sessions/my-day-summary/?date={timezone.localdate().isoformat()}"
		)
		self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
		self.assertEqual(summary_response.data['total_sessions'], 1)

	def test_cannot_checkin_with_existing_open_session(self):
		self.client.force_authenticate(user=self.user)

		payload = {
			'project': self.project.id,
			'location_type': 'site',
			'check_in_latitude': 12.9716,
			'check_in_longitude': 77.5946,
			'travel_km': '0.00',
		}
		first_response = self.client.post('/api/auth/attendance-sessions/check-in/', payload, format='json')
		self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

		second_response = self.client.post('/api/auth/attendance-sessions/check-in/', payload, format='json')
		self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_admin_day_overview_requires_admin_account(self):
		self.client.force_authenticate(user=self.user)
		forbidden = self.client.get('/api/auth/attendance-sessions/admin-day-overview/')
		self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

		self.client.force_authenticate(user=self.admin_user)
		allowed = self.client.get('/api/auth/attendance-sessions/admin-day-overview/')
		self.assertEqual(allowed.status_code, status.HTTP_200_OK)


class DailyWorkItemApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='worklist_user', password='workpass123')
		self.project = Project.objects.create(
			name='Villa Site',
			project_code='PROJ202',
			client='Skyline',
			project_manager=self.user,
			location='North Zone',
		)
		self.client.force_authenticate(user=self.user)

	def test_work_item_state_transitions(self):
		create_payload = {
			'project': self.project.id,
			'title': 'Concrete slab marking',
			'description': 'Mark slab points and verify level',
			'priority': 'high',
		}
		create_response = self.client.post('/api/auth/daily-work-items/', create_payload, format='json')
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		item_id = create_response.data['id']

		start_response = self.client.patch(f'/api/auth/daily-work-items/{item_id}/start/', {}, format='json')
		self.assertEqual(start_response.status_code, status.HTTP_200_OK)
		self.assertEqual(start_response.data['status'], 'in_progress')

		complete_response = self.client.patch(f'/api/auth/daily-work-items/{item_id}/complete/', {}, format='json')
		self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
		self.assertEqual(complete_response.data['status'], 'done')

		db_item = DailyWorkItem.objects.get(id=item_id)
		self.assertIsNotNone(db_item.completed_at)


class DashboardSummaryApiTests(APITestCase):
	def setUp(self):
		self.worker = User.objects.create_user(
			username='dashboard_worker',
			password='workerpass123',
			account_type='technical',
			grade='tech_wk',
		)
		self.admin_user = User.objects.create_user(
			username='dashboard_admin',
			password='adminpass123',
			account_type='admin',
			grade='admin_head',
		)

	def test_worker_dashboard_summary_returns_common_and_technical_sections(self):
		self.client.force_authenticate(user=self.worker)
		response = self.client.get('/api/auth/dashboard/summary/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['dashboard_type'], 'technical')
		self.assertIn('common', response.data)
		self.assertIn('role_summary', response.data)
		self.assertIn('execution', response.data['role_summary'])
		self.assertIn('my_tasks', response.data['common'])

	def test_admin_dashboard_summary_returns_admin_sections(self):
		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get('/api/auth/dashboard/summary/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['dashboard_type'], 'admin')
		self.assertIn('organization', response.data['role_summary'])
		self.assertIn('operations', response.data['role_summary'])
		self.assertIn('approvals', response.data['role_summary'])
