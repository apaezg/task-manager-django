import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from simple_tasks.models import Task


logger = logging.getLogger('django')


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    fields = ('id', 'status', 'assigned_to')
    ordering = ['-id']


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['assigned_to']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status', 'assigned_to']

    def get_object(self, queryset=None):
        task_object = super(TaskUpdate, self).get_object(queryset)
        if task_object and not task_object.can_be_updated():
            raise PermissionDenied
        return task_object

    def get_form(self, form_class=None):
        form = super(TaskUpdate, self).get_form(self.form_class)
        form.fields['status'].choices = Task.STATUS_ACTIVE_CHOICES
        return form

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        response = super().form_valid(form)
        self.notify_changed_task(form)
        return response

    def notify_changed_task(self, form):
        subject = f'Task {self.object.pk} has changed'
        changes = []
        for field in form.changed_data:
            changes.append(f'- {field}: {form.initial[field]} -> {form.data[field]}')
        str_changes = "\n".join(changes)
        nl = "\n"
        body = f'Task has changed following values:{nl}{str_changes}'
        send_mail(
            subject,
            body,
            'from@example.com',
            [form.instance.assigned_to.email],
            fail_silently=False,
        )


class TaskArchive(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

    def test_func(self):
        return self.request.user.is_staff
