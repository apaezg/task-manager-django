from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from simple_tasks.models import Task
from simple_tasks.views import TaskList


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
        request = self.factory.get(reverse('task_list'))

        request.user = AnonymousUser()

        response = TaskList.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

    def test_access_to_admin(self):
        request = self.factory.get(reverse('task_list'))

        request.user = self.admin_user

        response = TaskList.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_list.html', response.template_name)
        self.assertEqual(list(response.context_data['object_list']), [self.task])

    def test_access_to_user(self):
        request = self.factory.get(reverse('task_list'))

        request.user = self.regular_user

        response = TaskList.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_list.html', response.template_name)
        self.assertEqual(list(response.context_data['object_list']), [self.task])
