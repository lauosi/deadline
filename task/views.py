from django.shortcuts import render
from django.utils import timezone
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404 , redirect, render_to_response
from django.utils.safestring import mark_safe

import datetime
import calendar

from .models import Task
from .forms import AddTask, AddTaskDate
from .event_calendar import TaskCalendar

class SearchView(generic.ListView):
    
    template_name = 'task/search.html'

    def get_queryset(self):
        return Task.objects.all().order_by('-date')

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)

        errors = []
        if 'q' in self.request.GET:
            q = self.request.GET['q']
            if not q:
                errors.append('Please enter a search term.')
                context['errors'] = errors
            elif len(q) > 30:
                errors.append('Please enter at most 30 characters.')
                context['errors'] = errors
            else:
                if 'f' in self.request.GET:
                    f = self.request.GET['f']
                    if f == "display_upcoming":
                        tasks = Task.objects.filter(short_command__icontains=q).extra(where=["date > %s"], params=[timezone.now()])
                else:
                    tasks = Task.objects.filter(short_command__icontains=q)
                context['tasks'] = tasks
                context['query'] = q
        else:
            context['tasks'] = []
        return context
    
class ArchiveView(generic.ListView):
    
    template_name = 'task/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.all().filter(date__lt=timezone.now()).order_by('-date')[:20]

    def get_context_data(self, *args, **kwargs):
        context = super(ArchiveView, self).get_context_data(*args, **kwargs)
        context['deadlines'] = Task.objects.all().filter(deadline__lt=timezone.now()).order_by('-deadline')[:20]
        context['past'] = True
        return context

class UpcomingView(generic.ListView):
    
    template_name = 'task/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.all().filter(date__gt=timezone.now()).order_by('date')[:20]

    def get_context_data(self, *args, **kwargs):
        context = super(UpcomingView, self).get_context_data(*args, **kwargs)
        context['deadlines'] = Task.objects.all().filter(deadline__gt=timezone.now()).order_by('deadline')[:20]
        return context
    
class TaskDetailView(generic.DetailView):

    template_name = 'task/task_detail.html'
    model = Task
    
    
class AddNewTask(generic.FormView):
    
    template_name = 'task/add_task.html'
    form_class = AddTask
    success_url =  reverse_lazy('task:calendar')
    
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
    
class AddDateTask(generic.FormView):
    
    template_name = 'task/add_task.html'
    form_class = AddTaskDate

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        add_form = AddTaskDate()
        date = datetime.date(year=int(self.args[0]), month=int(self.args[1]), day=int(self.args[2]))
        context.update({'add_form': add_form, 'date': date})
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        add_form = AddTaskDate(request.POST)
        
        if add_form.is_valid():
            form = add_form.save(commit=False)
            form.date = datetime.date(year=int(self.args[0]), month=int(self.args[1]), day=int(self.args[2]))
            form.save()
            return HttpResponseRedirect(reverse('task:calendar', args=(self.args)))

        context = self.get_context_data(**kwargs)
        context.update({'add_form': add_form, 'date': self.date})
        return self.render_to_response(context)

class EditTask(generic.UpdateView):
    
    template_name = 'task/add_task.html'
    form_class = AddTask
    model = Task

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
    
def task_procrastinate(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.procrastinate()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def task_invert(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.invert()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def task_remove(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def calendar(request, year=timezone.now().year, month=timezone.now().month, day=timezone.now().day):
    """
    http://uggedal.com/journal/creating-a-flexible-monthly-calendar-in-django/
    """
    # important: list of deadlines for particular day
    deadlines = Task.objects.order_by('deadline').filter(
    deadline__year=year, deadline__month=month, deadline__day=day)

    # important: list of tasks for particular day
    day_tasks = Task.objects.order_by('date').filter(
    date__year=year, date__month=month, date__day=day)

    # important to create HTMLCalendar
    my_deadlines = Task.objects.order_by('deadline').filter(
    deadline__year=year, deadline__month=month)

    # important to create HTMLCalendar
    my_tasks = Task.objects.order_by('date').filter(
    date__year=year, date__month=month)

    # important to determine the name of particular day
    my_year = int(year)
    my_month = int(month)
    my_day = int(day)

    date = datetime.date(year=my_year,day=my_day, month=my_month)
    
    if my_year == timezone.now().year and my_month == timezone.now().month:
        if my_day == timezone.now().day:
            name = 'today'
        elif my_day == (timezone.now() + datetime.timedelta(days=1)).day:
            name = 'tomorrow'
        elif my_day == (timezone.now() + datetime.timedelta(days=2)).day:
            name = 'day after tomorrow'
        elif my_day == (timezone.now() - datetime.timedelta(days=1)).day:
            name = 'yesterday'
        else:
            name = ''
    else:
        name = ''
        
    # important to handle the change of months and years        
    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
            my_previous_year = my_year - 1
            my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
            my_next_year = my_year + 1
            my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1

    # calendar
    cal = TaskCalendar(my_tasks, my_deadlines).formatmonth(int(year), int(month))
    return render_to_response('task/calendar.html', {'calendar': mark_safe(cal),
                                                     'my_tasks': day_tasks,
                                                     'deadlines': deadlines,
                                                     'day': my_day,
                                                     'month': my_month,
                                                     'year': my_year,
                                                     'date': date,
                                                     'name': name, 
                                                     'previous_month': my_previous_month,
                                                     'previous_year': my_previous_year,
                                                     'next_month': my_next_month,
                                                     'next_year': my_next_year,
                                                     'year_before_this': my_year_before_this,
                                                     'year_after_this': my_year_after_this,})
        

