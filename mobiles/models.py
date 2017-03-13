import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.fields import JSONField

from .managers import MobileManager

# Application wide choices
PRIORITIES = (
    ('URGENT', 'Urgent Messages'),
    ('NORMAL', 'Normal Messages'),
    ('LOW', 'Low Priority Detail'),
)

MSG_TYPES = (
    ('SMS', 'SMS'),
    ('EMAIL', 'Email'),
    ('TWEET', 'Twitter'),
    ('FACE', 'Facebook Messenger')
)


class TextivistAccount(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    name = models.CharField(max_length=200)
    created_date = models.DateTimeField('Date organisation created')
    owner = models.ForeignKey('Mobile', on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Postcode(models.Model):
    post_code = models.CharField(max_length=8, primary_key=True)

    def post_region(self):
        return self.post_code[:-4]

    def __str__(self):
        return self.post_code


class AreaCategory(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Area(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey(TextivistAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    category = models.ForeignKey('AreaCategory', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    post_codes = models.ManyToManyField('Postcode')
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Organisation(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey(TextivistAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField('Date organisation created')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey('Mobile', blank=True, null=True, on_delete=models.CASCADE, related_name='org_owner')
    areas = models.ManyToManyField('Area')
    messaging_account = models.ForeignKey('MessagingAccount', on_delete=models.SET_NULL, blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=90) <= self.created_date <= now

    was_created_recently.admin_order_field = 'created_date'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'New organisation?'


class AccountRole(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey(TextivistAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class MessagingProvider(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    name = models.CharField(max_length=40)
    username = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    account_sid = models.CharField(max_length=40)
    auth_token = models.CharField(max_length=40)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class MessagingAccount(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey(TextivistAccount, on_delete=models.CASCADE)
    provider = models.ForeignKey(MessagingProvider, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=40)
    account_sid = models.CharField(max_length=40)
    auth_token = models.CharField(max_length=40)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.account_name


class MessagingEndPoint(models.Model):
    ENDPOINT_TYPES = (
        ('PHONE', 'Phone Number'),
        ('EMAIL', 'Email Address'),
    )
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey(TextivistAccount, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    messaging_account = models.ForeignKey(MessagingAccount, on_delete=models.CASCADE)
    endpoint_type = models.CharField(max_length=10, choices=ENDPOINT_TYPES, default='PHONE')
    endpoint_address = models.CharField(max_length=40)
    account_sid = models.CharField(max_length=40)
    auth_token = models.CharField(max_length=40)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return '{}: {}'.format(
            self.messaging_account,
            self.endpoint_address
        )


class Mobile(AbstractBaseUser, PermissionsMixin):
    STATES = (
        ('REQUESTED', 'Requested'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MARKED', 'Marked for deletion')
    )

    phone_number = models.CharField(max_length=15, unique=True)
    created_date = models.DateTimeField('Date phone number registered')
    last_texted = models.DateTimeField('Date latest text message was sent', blank=True, null=True)
    post_code = models.ForeignKey('Postcode', blank=True, null=True, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=40, default='Anonymous')
    last_name = models.CharField(max_length=40, default='Mobile')
    title = models.CharField(max_length=4, blank=True)
    email = models.EmailField(blank=True)
    state = models.CharField(max_length=20, choices=STATES, default='REQUESTED')

    objects = MobileManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        users_name = ' '.join([self.first_name, self.last_name])
        return '{}: *{}'.format(
            users_name,
            self.phone_number[-4:]
        )

    def get_short_name(self):
        return 'Mobile *{}'.format(
            self.phone_number[-4:]
        )

    def __str__(self):
        users_name = ' '.join([self.first_name, self.last_name])
        return '{}: *{}'.format(
            users_name,
            self.phone_number[-4:]
        )

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=90) <= self.created_date <= now

    was_created_recently.admin_order_field = 'created_date'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Registered recently?'

    def text_mobile(self):
        """Send test message to mobile, not implemented"""
        pass

    # def save(self, *args, **kwargs):
    #     """Custom save method which also sends a confirmation text"""
    #
    #     super(Mobile, self).save(*args, **kwargs)
    #
    #     from .tasks import send_registration_confirmation
    #     send_registration_confirmation.delay(self.pk)


class Membership(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    mobile = models.ForeignKey('Mobile', on_delete=models.CASCADE)
    role = models.ForeignKey('AccountRole', on_delete=models.SET_NULL, blank=True, null=True)
    email = models.EmailField(blank=True)
    areas = models.ManyToManyField('Area')
    organisations = models.ManyToManyField('Organisation')
    member_id = models.CharField(max_length=10, blank=True)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')
    created_date = models.DateTimeField('Date person registered')
    properties = JSONField(blank=True, null=True)

    def __str__(self):
        orglist = ', '.join(org.name for org in self.organisations.all())
        return '{} - {} - {}'.format(
            self.mobile.get_short_name(),
            self.tt_account,
            orglist
        )

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=90) <= self.created_date <= now

    was_created_recently.admin_order_field = 'created_date'
    was_created_recently.boolean = True
    was_created_recently.short_description = 'Registered recently?'


class Command(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    code = models.CharField(max_length=10)
    long_name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return '{}: {}'.format(
            self.code,
            self.long_name
        )


class TopicCategory(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    name = models.CharField(max_length=40, primary_key=True)
    description = models.CharField(max_length=2000)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Topic(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    shortcode = models.CharField(max_length=10, unique=True)
    members_only = models.BooleanField()
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    topic_category = models.ForeignKey(TopicCategory, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True)
    filter_by_area = models.BooleanField()
    filter_by_organisation = models.BooleanField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    owner = models.ForeignKey(Mobile, on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField('Start of topic live date range')
    finish = models.DateTimeField('End of topic live date range')
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Event(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    event_date = models.DateTimeField('Date of the event')
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    topic = models.ForeignKey(Topic, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Mobile, blank=True, on_delete=models.CASCADE)
    start = models.TimeField('Start of event')
    finish = models.TimeField('End of event')
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MARKED', 'Marked for deletion')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    phone_number = models.ForeignKey(Mobile, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='NORMAL')
    subscribed_date = models.DateTimeField('Date subscription was created')
    cancelled_date = models.DateTimeField('Date subscription was cancelled', blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return '{} subscribes to {}'.format(
            self.phone_number,
            self.topic
        )


class TopicTemplate(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    topic_category = models.ForeignKey(TopicCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class EventTemplate(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    topic_category = models.ForeignKey(TopicCategory, on_delete=models.CASCADE)
    relative_days = models.PositiveIntegerField('Default number of days before topic end date')
    default_time = models.TimeField('Default time of event')
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class MsgTemplate(models.Model):
    STATES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    topic_category = models.ForeignKey(TopicCategory, blank=True, on_delete=models.CASCADE)
    topic_template = models.ForeignKey(TopicTemplate, blank=True, on_delete=models.CASCADE)
    event_template = models.ForeignKey(EventTemplate, blank=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=MSG_TYPES, default='SMS')
    relative_days = models.PositiveIntegerField('Default number of days before topic end date', default=0)
    default_time = models.TimeField('Default time of event')
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='NORMAL')
    body = models.CharField(max_length=140)
    state = models.CharField(max_length=20, choices=STATES, default='ACTIVE')

    def __str__(self):
        return self.name


class MsgBatch(models.Model):
    STATES = (
        ('PENDING', 'Send Job Pending'),
        ('ERROR', 'Error'),
        ('SENT', 'Messages Sent')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    endpoint = models.ForeignKey('MessagingEndPoint', on_delete=models.CASCADE)
    created_on = models.DateTimeField('Date batch job was created')
    to_send = models.DateTimeField('Time batch job to be run')
    was_sent = models.DateTimeField('Time batch job was completed', blank=True, null=True)
    type = models.CharField(max_length=10, choices=MSG_TYPES, default='SMS')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='NORMAL')
    body = models.CharField(max_length=140)
    state = models.CharField(max_length=20, choices=STATES, default='PENDING')

    def __str__(self):
        return 'MsgBatch for Topic: {} - {}...'.format(
            self.topic.name,
            self.body[0:20]
        )


class Outbox(models.Model):
    STATES = (
        ('PENDING', 'Message Pending'),
        ('ERROR', 'Error'),
        ('SENT', 'Message Sent')
    )

    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=MSG_TYPES, default='SMS')
    sent = models.DateTimeField('Time message was sent', blank=True, null=True)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='NORMAL')
    to_mobile = models.CharField(max_length=15)
    endpoint = models.ForeignKey('MessagingEndPoint', on_delete=models.CASCADE)
    body = models.CharField(max_length=140)
    state = models.CharField(max_length=20, choices=STATES, default='PENDING')

    def __str__(self):
        return 'Message for Topic: {} - {}...'.format(
            self.topic.name,
            self.body[0:20]
        )


class Message(models.Model):
    tt_account = models.ForeignKey('TextivistAccount', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=MSG_TYPES, default='SMS')
    to_endpoint = models.CharField(max_length=40)
    from_endpoint = models.CharField(max_length=40)
    body = models.CharField(max_length=180)
    description = models.CharField(max_length=180, blank=True)
    direction = models.CharField(max_length=180, blank=True)
    price = models.FloatField(default=0.0)
    price_unit = models.CharField(max_length=180, default='GBP')


class AuditLog(models.Model):
    timestamp = models.DateTimeField()
    user = models.ForeignKey(Mobile, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=40)
    description = models.CharField(max_length=2000)
