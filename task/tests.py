from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

import datetime

from task.forms import AddTask, AddTaskDate
from task.models import Task

class TaskMethodAndFormTests(TestCase):
    
    def setUp(self):
        Task.objects.create(short_command='Buy a monkey',
                            importance='3',
                            date=datetime.date(year=2016, day=22, month=5),
                            deadline=datetime.date(year=2016,day=22, month=6),
                            description='')
        
    def test_addform_without(self):
        """
        Try to submit not valid form.
        """
        form_data = {}
        form = AddTask(data=form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_addform_mandatory(self):
        """
        Try to submit form only with mandatory.
        """
        form_data = {'short_command': 'Tame the monster', 'importance' : '3', 'date': datetime.date.today()}
        form = AddTask(data=form_data)
        self.assertTrue(form.is_valid())

    def test_procrastinate_date(self):
        """
        Postpone task for later.
        """
        buy_monkey = Task.objects.get(short_command="Buy a monkey")
        buy_monkey.procrastinate()
        buy_monkey.save()
        self.assertEqual(buy_monkey.date.day, 23)

    def test_invert_if_task_not_done(self):
        """
        Mark task as done.
        """
        buy_monkey = Task.objects.get(short_command="Buy a monkey")
        buy_monkey.invert()
        buy_monkey.save()
        self.assertTrue(buy_monkey.done)

def create_task(short_command, days, deadline_days=0):
    """
    Create task with given 'short_command' and given number of days
    as an offset to now (negative for tasks with date in the past ).
    'deadline_days' is an optional field that works like 'days' but
    it indicates task's deadline.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    if deadline_days != 0:
        time_deadline = timezone.now() + datetime.timedelta(days=deadline_days)
        return Task.objects.create(short_command=short_command,
                                   date=time,
                                   deadline=time_deadline,
                                   importance='2')
    else:
        return Task.objects.create(short_command=short_command,
                                   date=time,
                                   importance='2')
    
class TaskViewTests(TestCase):
    def setUp(self):
        Task.objects.create(short_command='Buy a monkey',
                            importance='2',
                            date=datetime.date(year=2018, day=30, month=8),
                            description='')
        Task.objects.create(short_command='Fix the kitchen sink',
                            importance='3',
                            date=datetime.date(year=2016, day=20, month=5),
                            description='')
        
    def test_archive_with_a_past_task(self):
        """
        Tasks with a date in the past should be displayed on archive page.
        """
        response = self.client.get(reverse('task:archive'))
        self.assertQuerysetEqual(response.context['tasks'],
                                 ['<Task: Fix the kitchen sink>'])

    def test_upcoming_with_a_future_task(self):
        """
        Tasks with a date in the future should be displayed on 'upcoming' page.
        """
        response = self.client.get(reverse('task:upcoming'))
        self.assertQuerysetEqual(response.context['tasks'],
                                 ['<Task: Buy a monkey>'])

    def test_archive_with_past_task_and_past_deadline(self):
        """
        Tasks with a date in the past should be displayed on archive page
        as well as the task with deadline in the past.
        """
        create_task("Decorate the house", -10, -5)
        response = self.client.get(reverse('task:archive'))
        self.assertQuerysetEqual(response.context['tasks'],
                                 ['<Task: Decorate the house>',
                                  '<Task: Fix the kitchen sink>'])
        self.assertQuerysetEqual(response.context['deadlines'],
                                 ['<Task: Decorate the house>'])

    def test_date_in_the_past_and_deadline_in_the_future(self):
        """
        Tasks with a date in the past should be displayed on archive page,
        tasks with a deadline in the future should be displayed on 'upcoming'
        page.
        """
        create_task("Plant a tree", -1, 90)
        response_past = self.client.get(reverse('task:archive'))
        response_future = self.client.get(reverse('task:upcoming'))
        self.assertQuerysetEqual(response_past.context['tasks'],
                                 ['<Task: Plant a tree>',
                                  '<Task: Fix the kitchen sink>',])
        self.assertQuerysetEqual(response_future.context['deadlines'],
                                 ['<Task: Plant a tree>']) 
