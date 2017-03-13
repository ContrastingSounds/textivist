from django.forms import ModelForm
# from django.contrib.admin import widgets

from .models import MsgBatch


class MessageBatchForm(ModelForm):
    class Meta:
        model = MsgBatch
        fields = ['tt_account', 'topic', 'to_send', 'type', 'priority', 'body']
        # widgets = {'to_send': forms.DateInput(attrs={'class': 'datepicker'})}
