from django.forms import ModelForm
# from django.contrib.admin import widgets

from .models import MsgBatch, Organisation, Topic


class MessageBatchForm(ModelForm):
    def __init__(self, current_user, *args, **kwargs):
        super(MessageBatchForm, self).__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.filter(subscription__phone_number=current_user)

    class Meta:
        model = MsgBatch
        fields = ['topic', 'to_send', 'type', 'priority', 'body']
        # widgets = {'to_send': forms.DateInput(attrs={'class': 'datepicker'})}


class TopicForm(ModelForm):
    def __init__(self, current_user, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].queryset = Organisation.objects.filter(membership__mobile=current_user)
        self.fields['parent'].queryset = Topic.objects.filter(subscription__phone_number=current_user)

    class Meta:
        model = Topic
        fields = ['organisation', 'shortcode', 'name', 'members_only', 'description', 'topic_category', 'parent',
                  'area', 'filter_by_area', 'filter_by_organisation']

