import re

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import MessageBatchForm, TopicForm
from .models import TextivistAccount, Organisation, Topic, Mobile, Membership, Subscription


def textivist_account_list(request):
    return render(request, 'mobiles/textivist_account_list.html', {})


def sms_received(request):
    endpoint = request.GET.get('To')
    sms_from = request.GET.get('From')
    sms_text = request.GET.get('Body')

    words = re.findall('(\w+)', sms_text)
    flag = 0
    commands = []
    parameters = []

    for word in words:
        if re.search('^[A-Z]+$', word):
            flag = 1
            commands.append(word)
        else:
            if flag == 1:
                parameters.append(word)

    from .tasks import handle_sms
    handle_sms.delay(endpoint, sms_from, commands, parameters)

    return render(request, 'mobiles/textivist_account_list.html', {})


def index(request):
    return render(request, 'mobiles/index.html', {})

@login_required
def tt_account(request, textivist_id):
    account = TextivistAccount.objects.get(pk=textivist_id)
    try:
        organisations = Organisation.objects.filter(tt_account=account)
    except Organisation.DoesNotExist:
        organisations = []
    context = {
        'account': account,
        'organisations': organisations,
    }
    return render(request, 'mobiles/textivist_account.html', context=context)

@login_required
def organisation(request, textivist_id, organisation_id):
    organisation = Organisation.objects.get(pk=organisation_id)
    topics = Topic.objects.filter(organisation=organisation)
    context = {
        'organisation': organisation,
        'topics': topics,
    }
    return render(request, 'mobiles/organisation.html', context=context)

@login_required
def mobiles_list(request):
    mobiles = Mobile.objects.all()
    context = {
        'mobiles': mobiles,
    }
    return render(request, 'mobiles/mobiles_list.html', context=context)

@login_required
def mobile(request, mobile_id):
    mobile = Mobile.objects.get(pk=mobile_id)
    memberships = Membership.objects.filter(mobile=mobile)
    subscriptions = Subscription.objects.filter(phone_number=mobile)
    context = {
        'mobile': mobile,
        'memberships': memberships,
        'subscriptions': subscriptions,
    }
    return render(request, 'mobiles/mobile.html', context=context)

@login_required
def create_batch(request):
    if request.method == "POST":
        form = MessageBatchForm(request.user, request.POST)
        if form.is_valid():
            # commit=False means the form doesn't save at this time.
            # commit defaults to True which means it normally saves.
            message_batch = form.save(commit=False)
            message_batch.endpoint = message_batch.topic.organisation.messagingendpoint_set.first()
            message_batch.created_on = timezone.now()
            message_batch.save()
            return redirect('index')
    else:
        form = MessageBatchForm(request.user)

    context = {
        'form': form,
    }
    return render(request, "mobiles/create_batch.html", context=context)


@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(pk=topic_id)
    context = {
        'topic': topic,
    }
    return render(request, "mobiles/topic.html", context=context)


@login_required
def add_topic(request):
    if request.method == "POST":
        form = TopicForm(request.user, request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.owner = request.user
            topic.tt_account = topic.organisation.tt_account
            topic.save()
            return redirect('index')
    else:
        form = TopicForm(request.user)

    context = {
        'form': form,
    }
    return render(request, "mobiles/add_topic.html", context=context)


@login_required
def my_mobile(request):
    memberships = Membership.objects.filter(mobile=request.user)
    subscriptions = Subscription.objects.filter(phone_number=request.user)
    context = {
        'mobile': request.user,
        'memberships': memberships,
        'subscriptions': subscriptions,
    }
    return render(request, "mobiles/my_account.html", context=context)


@login_required
def help(request):
    return render(request, "mobiles/help.html", {})