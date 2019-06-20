from django.apps import apps
from django.test import TestCase
from simple_tasks.apps import TasksConfig


class TasksConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(TasksConfig.name, 'simple_tasks')
        self.assertEqual(apps.get_app_config('simple_tasks').name, 'simple_tasks')