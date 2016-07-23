from django import forms
from .models import Task
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})
TimeInput = partial(forms.TimeInput, {'class': 'timepicker'})

class AddTask(forms.ModelForm):
    date = forms.DateField(widget=DateInput())
    deadline = forms.DateField(widget=DateInput(), required=False)
    time = forms.TimeField(widget=TimeInput(), required=False)
    
    class Meta:
        model = Task
        help_texts = {
            'importance': 'Choose how important is that task to you',
            'description': 'Fields time, deadline and description are optional.',
        }
        fields = ('short_command', 'importance', 'date', 'time', 'deadline', 'description')

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('login', 'Submit', css_class='btn btn-default'))

class AddTaskDate(forms.ModelForm):
    deadline = forms.DateField(widget=DateInput(), required=False)
    time = forms.TimeField(widget=TimeInput(), required=False)
    
    class Meta:
        model = Task
        help_texts = {
            'importance': 'Choose how important is that task to you.',
            'description': 'Fields time, deadline and description are optional.'
        }
        fields = ('short_command', 'importance', 'time', 'deadline', 'description',)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('login', 'Submit', css_class='btn btn-default'))
    
