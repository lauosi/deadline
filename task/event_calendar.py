from calendar import HTMLCalendar
from datetime import date
from itertools import groupby
from django.utils.html import conditional_escape as esc
from django.core.urlresolvers import reverse

class TaskCalendar(HTMLCalendar):

    def __init__(self, tasks, deadlines):
        super(TaskCalendar, self).__init__()
        self.tasks = self.group_by_day(tasks)
        self.deadlines = self.group_by_deadline(deadlines)

    def formatday(self, day, weekday):
        self.day = day
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, self.day):
                cssclass += ' today'
            if day in self.tasks:
                cssclass += ' filled'
            if day in self.deadlines:
                cssclass += ' deadline'
                body = '<span class="glyphicon glyphicon-fire" aria-hidden="true"></span>'
                return self.day_cell(cssclass, '%d %s' % (day, body))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(TaskCalendar, self).formatmonth(year, month)

    def group_by_day(self, tasks):
        field = lambda task: task.date.day
        return dict([(day, list(items)) for day, items in groupby(tasks, field)])
    
    def group_by_deadline(self, tasks):
        tasks_with_deadline = [task for task in tasks if task.deadline]        

        field = lambda task: task.deadline.day
        return dict([(day, list(items)) for day, items in groupby(tasks_with_deadline, field)])
    
    def get_absolute_url(self):
        return reverse('task:calendar', args=[self.year,self.month,self.day])
    
    def day_cell(self, cssclass, body):
        return '<td class="%s"><a href="%s">%s</a></td>' % (cssclass, self.get_absolute_url(), body)
  

    
