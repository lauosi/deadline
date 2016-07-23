from django.test import TestCase
from django.utils import timezone
import datetime

from task.forms import AddTask, AddTaskDate
from task.models import Task

class ManipulateTasksTest(TestCase):
    
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
        Mark as done.
        """
        buy_monkey = Task.objects.get(short_command="Buy a monkey")
        buy_monkey.invert()
        buy_monkey.save()
        self.assertTrue(buy_monkey.done)
