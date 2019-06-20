from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from simple_tasks.models import Task


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
        object = super(TaskUpdate, self).get_object(queryset)
        if object and not object.can_be_updated():
            raise PermissionDenied
        return object

    def get_form(self):
        form = super(TaskUpdate, self).get_form(self.form_class)
        form.fields['status'].choices = Task.STATUS_ACTIVE_CHOICES
        return form

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class TaskArchive(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

    def test_func(self):
        return self.request.user.is_staff
