from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.urls import reverse

from simple_tasks.models import Task
from simple_tasks.views import TaskUpdate


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
        request = self.factory.get(reverse('task_update', kwargs={'pk': self.task.pk}))

        request.user = AnonymousUser()

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next=/update/{self.task.pk}')

    def test_access_to_admin(self):
        request = self.factory.get(reverse('task_update', kwargs={'pk': self.task.pk}))

        request.user = self.admin_user

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_form.html', response.template_name)
        self.assertEqual(response.context_data['object'], self.task)
        self.assertEqual(self.task, response.context_data['form'].instance)
        self.assertIn('form', response.context_data)

    def test_access_to_user(self):
        request = self.factory.get(reverse('task_update', kwargs={'pk': self.task.pk}))

        request.user = self.regular_user

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_form.html', response.template_name)
        self.assertEqual(response.context_data['object'], self.task)
        self.assertEqual(self.task, response.context_data['form'].instance)
        self.assertIn('form', response.context_data)

    def test_admin_can_update(self):
        data = {'assigned_to': self.regular_user.pk, 'status': Task.COMPLETED_STATUS}
        request = self.factory.post(reverse('task_update', kwargs={'pk': self.task.pk}), data)

        request.user = self.admin_user

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=self.task.pk).assigned_to, self.regular_user)
        self.assertEqual(Task.objects.get(pk=self.task.pk).status, Task.COMPLETED_STATUS)
        self.assertEqual(response.url, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_user_can_update(self):
        data = {'assigned_to': self.regular_user.pk, 'status': Task.IN_PROGRESS_STATUS}
        request = self.factory.post(reverse('task_update', kwargs={'pk': self.task.pk}), data)

        request.user = self.regular_user

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=self.task.pk).assigned_to, self.regular_user)
        self.assertEqual(Task.objects.get(pk=self.task.pk).status, Task.IN_PROGRESS_STATUS)
        self.assertEqual(response.url, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_cant_archive(self):
        data = {'assigned_to': self.regular_user.pk, 'status': Task.ARCHIVED_STATUS}
        request = self.factory.post(reverse('task_update', kwargs={'pk': self.task.pk}), data)

        request.user = self.admin_user

        response = TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('simple_tasks/task_form.html', response.template_name)
        self.assertIn('form', response.context_data)
        self.assertIn('status', response.context_data['form'].errors)
        self.assertEqual(self.task, response.context_data['form'].instance)
        self.assertEqual(Task.objects.get(pk=self.task.pk).assigned_to, self.admin_user)
        self.assertEqual(Task.objects.get(pk=self.task.pk).status, Task.NEW_STATUS)

    def test_cant_access_archived(self):
        self.task.status = Task.ARCHIVED_STATUS
        self.task.save()
        request = self.factory.get(reverse('task_update', kwargs={'pk': self.task.pk}))

        request.user = self.admin_user

        with self.assertRaises(PermissionDenied):
            TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(Task.objects.get(pk=self.task.pk).assigned_to, self.admin_user)
        self.assertEqual(Task.objects.get(pk=self.task.pk).status, Task.ARCHIVED_STATUS)

    def test_cant_update_archived(self):
        self.task.status = Task.ARCHIVED_STATUS
        self.task.save()
        data = {'assigned_to': self.regular_user.pk, 'status': Task.IN_PROGRESS_STATUS}
        request = self.factory.post(reverse('task_update', kwargs={'pk': self.task.pk}), data)

        request.user = self.admin_user

        with self.assertRaises(PermissionDenied):
            TaskUpdate.as_view()(request, pk=self.task.pk)

        self.assertEqual(Task.objects.get(pk=self.task.pk).assigned_to, self.admin_user)
        self.assertEqual(Task.objects.get(pk=self.task.pk).status, Task.ARCHIVED_STATUS)
