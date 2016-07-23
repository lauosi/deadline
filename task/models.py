from django.db import models
from django.utils import timezone
import datetime
from django.core.urlresolvers import reverse


class Task(models.Model):
    
    TASK_IMPORTANCE = (
    ('1', 'low'),
    ('2', 'normal'),
    ('3', 'high'),
    )
    
    short_command = models.CharField(max_length=30, verbose_name="task")
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    importance = models.CharField(
        max_length=1,
        choices=TASK_IMPORTANCE,
        default='1',)
    description = models.TextField(
        verbose_name="Description",
        blank=True, null=True)
    done = models.BooleanField(default=False)
    
    def __str__(self):
        return self.short_command

    def get_absolute_url(self):
        return reverse('task:detail', kwargs={'pk': self.id}) 

    def invert(self):
        if self.done == True:
            self.done = False
        else:
            self.done = True
        self.save()
        
    def procrastinate(self):
        self.date += datetime.timedelta(days=1)
        self.save()

