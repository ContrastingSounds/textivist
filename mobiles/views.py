import re

from django.utils import timezone
from django.shortcuts import render, redirect

from .forms import MessageBatchForm
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


def organisation(request, textivist_id, organisation_id):
    organisation = Organisation.objects.get(pk=organisation_id)
    topics = Topic.objects.filter(organisation=organisation)
    context = {
        'organisation': organisation,
        'topics': topics,
    }
    return render(request, 'mobiles/organisation.html', context=context)


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


def create_batch(request):
    if request.method == "POST":
        form = MessageBatchForm(request.POST)
        if form.is_valid():
            # commit=False means the form doesn't save at this time.
            # commit defaults to True which means it normally saves.
            message_batch = form.save(commit=False)
            #message_batch.tt_account = tt_account_
            message_batch.endpoint = message_batch.topic.organisation.messagingendpoint_set.first()
            #message_batch.topic = topic
            message_batch.created_on = timezone.now()
            message_batch.save()
            return redirect('index')
    else:
        form = MessageBatchForm()

    context = {
        'form': form,
    }
    return render(request, "mobiles/create_batch.html", context=context)


def help(request):
    return render(request, "mobiles/help.html", {})