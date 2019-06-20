from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from simple_tasks.models import Task
from simple_tasks.views import TaskDetail


class TaskListTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser("admin", "admin@stm.es", "adminpass01")
        self.regular_user = User.objects.create_user("user", "user@stm.es", "userpass01")
        self.task = Task.objects.create(
            status="new",
            created_by=self.admin_user,
            modified_by=self.admin_user,
            assigned_to=self.admin_user,
        )

    def test_login_required(self):
        request = self.factory.get(reverse('task_detail', kwargs={'pk': self.task.pk}))

        request.user = AnonymousUser()

        response = TaskDetail.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next=/task/{self.task.pk}')

    def test_access_to_admin(self):
        request = self.factory.get(reverse('task_detail', kwargs={'pk': self.task.pk}))

        request.user = self.admin_user

        response = TaskDetail.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_detail.html', response.template_name)
        self.assertEqual(response.context_data['object'], self.task)

    def test_access_to_user(self):
        request = self.factory.get(reverse('task_detail', kwargs={'pk': self.task.pk}))

        request.user = self.regular_user

        response = TaskDetail.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_detail.html', response.template_name)
        self.assertEqual(response.context_data['object'], self.task)
