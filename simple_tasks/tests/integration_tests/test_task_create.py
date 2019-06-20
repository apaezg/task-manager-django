from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from simple_tasks.models import Task
from simple_tasks.views import TaskCreate


class TaskListTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser("admin", "admin@stm.es", "adminpass01")
        self.regular_user = User.objects.create_user("user", "user@stm.es", "userpass01")

    def test_login_required(self):
        request = self.factory.get(reverse('task_create'))

        request.user = AnonymousUser()

        response = TaskCreate.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/create')

    def test_access_to_admin(self):
        request = self.factory.get(reverse('task_create'))

        request.user = self.admin_user

        response = TaskCreate.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_form.html', response.template_name)
        self.assertIn('form', response.context_data)

    def test_access_to_user(self):
        request = self.factory.get(reverse('task_create'))

        request.user = self.regular_user

        response = TaskCreate.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_form.html', response.template_name)
        self.assertIn('form', response.context_data)

    def test_admin_can_create(self):
        request = self.factory.post(reverse('task_create'), {'assigned_to': self.regular_user.pk})

        request.user = self.admin_user

        response = TaskCreate.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.last().assigned_to, self.regular_user)
        self.assertEqual(Task.objects.last().status, Task.NEW_STATUS)
        self.assertEqual(response.url, reverse('task_detail', kwargs={'pk': Task.objects.last().pk}))

    def test_user_can_create(self):
        request = self.factory.post(reverse('task_create'), {'assigned_to': self.regular_user.pk})

        request.user = self.regular_user

        response = TaskCreate.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.last().assigned_to, self.regular_user)
        self.assertEqual(Task.objects.last().status, Task.NEW_STATUS)
        self.assertEqual(response.url, reverse('task_detail', kwargs={'pk': Task.objects.last().pk}))
