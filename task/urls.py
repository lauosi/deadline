from django.conf.urls import url, include
from django.contrib import admin
from . import views

app_name = 'task'
urlpatterns = [
    url(r'^home/$', views.calendar, name='calendar'),
    url(r'^calendar/([0-9]{4})/([0-9]+)/([0-9]+)/$', views.calendar, name='calendar'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^archive/$', views.ArchiveView.as_view(), name='archive'),
    url(r'^upcoming/$', views.UpcomingView.as_view(), name='upcoming'),
    url(r'^add_task/$', views.AddNewTask.as_view(), name='add_task'),
    url(r'^add_task/([0-9]{4})/([0-9]+)/([0-9]+)/$', views.AddDateTask.as_view(), name='add_task_date'),
    url(r'^(?P<pk>[0-9]+)/$', views.TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.EditTask.as_view(), name='edit'),
    url(r'^(?P<pk>[0-9]+)/postpone/$', views.task_procrastinate, name='task_procrastinate'),
    url(r'^(?P<pk>[0-9]+)/invert/$', views.task_invert, name='task_invert'),
    url(r'^(?P<pk>[0-9]+)/remove/$', views.task_remove, name='task_remove'),
]
