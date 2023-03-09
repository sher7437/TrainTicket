from django import forms
from django.contrib.auth.models import User

from .models import Train, Ticket


class UserForm(forms.ModelForm):
    """ User对象的表单信息 """
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']


class TrainForm(forms.ModelForm):
    """ Train对象的表单信息 """

    class Meta:
        model = Train
        fields = "__all__"


class TicketForm(forms.ModelForm):
    """ Ticket对象的表单信息 """

    class Meta:
        model = Ticket
        fields = "__all__"


class TravelForm(forms.Form):
    """ 出行信息表单 """
    leave_city = forms.CharField(label='leave_city', max_length=100)
    arrive_city = forms.CharField(label='arrive_city', max_length=100)
    leave_date = forms.DateField(label='leave_date')
