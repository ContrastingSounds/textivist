# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-15 20:03
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import mobiles.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mobile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('created_date', models.DateTimeField(verbose_name='Date phone number registered')),
                ('last_texted', models.DateTimeField(blank=True, null=True, verbose_name='Date latest text message was sent')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('first_name', models.CharField(default='Anonymous', max_length=40)),
                ('last_name', models.CharField(default='Mobile', max_length=40)),
                ('title', models.CharField(blank=True, max_length=4)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('state', models.CharField(choices=[('REQUESTED', 'Requested'), ('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('MARKED', 'Marked for deletion')], default='REQUESTED', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', mobiles.managers.MobileManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccountRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AreaCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.AreaCategory')),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('action', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('long_name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_date', models.DateTimeField(verbose_name='Date of the event')),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('start', models.TimeField(verbose_name='Start of event')),
                ('finish', models.TimeField(verbose_name='End of event')),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('owner', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relative_days', models.PositiveIntegerField(verbose_name='Default number of days before topic end date')),
                ('default_time', models.TimeField(verbose_name='Default time of event')),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('member_id', models.CharField(blank=True, max_length=10)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('created_date', models.DateTimeField(verbose_name='Date person registered')),
                ('properties', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('areas', models.ManyToManyField(to='mobiles.Area')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('SMS', 'SMS'), ('EMAIL', 'Email'), ('TWEET', 'Twitter'), ('FACE', 'Facebook Messenger')], default='SMS', max_length=10)),
                ('to_endpoint', models.CharField(max_length=40)),
                ('from_endpoint', models.CharField(max_length=40)),
                ('body', models.CharField(max_length=180)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('direction', models.CharField(blank=True, max_length=180)),
                ('price', models.FloatField(default=0.0)),
                ('price_unit', models.CharField(default='GBP', max_length=180)),
            ],
        ),
        migrations.CreateModel(
            name='MessagingAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(max_length=40)),
                ('account_sid', models.CharField(max_length=40)),
                ('auth_token', models.CharField(max_length=40)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MessagingEndPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint_type', models.CharField(choices=[('PHONE', 'Phone Number'), ('EMAIL', 'Email Address')], default='PHONE', max_length=10)),
                ('endpoint_address', models.CharField(max_length=40)),
                ('account_sid', models.CharField(max_length=40)),
                ('auth_token', models.CharField(max_length=40)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('messaging_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.MessagingAccount')),
            ],
        ),
        migrations.CreateModel(
            name='MessagingProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('username', models.CharField(max_length=40)),
                ('password', models.CharField(max_length=40)),
                ('email', models.CharField(max_length=40)),
                ('account_sid', models.CharField(max_length=40)),
                ('auth_token', models.CharField(max_length=40)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MsgBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(verbose_name='Date batch job was created')),
                ('to_send', models.DateTimeField(verbose_name='Time to send (e.g. 2017-03-14 15:00)')),
                ('was_sent', models.DateTimeField(blank=True, null=True, verbose_name='Time batch job was completed')),
                ('type', models.CharField(choices=[('SMS', 'SMS'), ('EMAIL', 'Email'), ('TWEET', 'Twitter'), ('FACE', 'Facebook Messenger')], default='SMS', max_length=10)),
                ('priority', models.CharField(choices=[('URGENT', 'Urgent Messages'), ('NORMAL', 'Normal Messages'), ('LOW', 'Low Priority Detail')], default='NORMAL', max_length=20)),
                ('body', models.CharField(max_length=140)),
                ('state', models.CharField(choices=[('PENDING', 'Send Job Pending'), ('ERROR', 'Error'), ('SENT', 'Messages Sent')], default='PENDING', max_length=20)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.MessagingEndPoint')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Event')),
            ],
        ),
        migrations.CreateModel(
            name='MsgTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('SMS', 'SMS'), ('EMAIL', 'Email'), ('TWEET', 'Twitter'), ('FACE', 'Facebook Messenger')], default='SMS', max_length=10)),
                ('relative_days', models.PositiveIntegerField(default=0, verbose_name='Default number of days before topic end date')),
                ('default_time', models.TimeField(verbose_name='Default time of event')),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('priority', models.CharField(choices=[('URGENT', 'Urgent Messages'), ('NORMAL', 'Normal Messages'), ('LOW', 'Low Priority Detail')], default='NORMAL', max_length=20)),
                ('body', models.CharField(max_length=140)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('event_template', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.EventTemplate')),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name='Date organisation created')),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('areas', models.ManyToManyField(to='mobiles.Area')),
                ('messaging_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mobiles.MessagingAccount')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='org_owner', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Organisation')),
            ],
        ),
        migrations.CreateModel(
            name='Outbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('SMS', 'SMS'), ('EMAIL', 'Email'), ('TWEET', 'Twitter'), ('FACE', 'Facebook Messenger')], default='SMS', max_length=10)),
                ('sent', models.DateTimeField(blank=True, null=True, verbose_name='Time message was sent')),
                ('priority', models.CharField(choices=[('URGENT', 'Urgent Messages'), ('NORMAL', 'Normal Messages'), ('LOW', 'Low Priority Detail')], default='NORMAL', max_length=20)),
                ('to_mobile', models.CharField(max_length=15)),
                ('body', models.CharField(max_length=140)),
                ('state', models.CharField(choices=[('PENDING', 'Message Pending'), ('ERROR', 'Error'), ('SENT', 'Message Sent')], default='PENDING', max_length=20)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.MessagingEndPoint')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Postcode',
            fields=[
                ('post_code', models.CharField(max_length=8, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('URGENT', 'Urgent Messages'), ('NORMAL', 'Normal Messages'), ('LOW', 'Low Priority Detail')], default='NORMAL', max_length=20)),
                ('subscribed_date', models.DateTimeField(verbose_name='Date subscription was created')),
                ('cancelled_date', models.DateTimeField(blank=True, null=True, verbose_name='Date subscription was cancelled')),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('MARKED', 'Marked for deletion')], default='ACTIVE', max_length=20)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Area')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Event')),
                ('phone_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TextivistAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name='Date organisation created')),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shortcode', models.CharField(max_length=10, unique=True)),
                ('members_only', models.BooleanField()),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('filter_by_area', models.BooleanField()),
                ('filter_by_organisation', models.BooleanField()),
                ('start', models.DateTimeField(verbose_name='Start of topic live date range')),
                ('finish', models.DateTimeField(verbose_name='End of topic live date range')),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.Area')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.Organisation')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Topic')),
            ],
        ),
        migrations.CreateModel(
            name='TopicCategory',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=2000)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('tt_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount')),
            ],
        ),
        migrations.CreateModel(
            name='TopicTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=2000)),
                ('state', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('topic_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TopicCategory')),
                ('tt_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount')),
            ],
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TopicCategory'),
        ),
        migrations.AddField(
            model_name='topic',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.Topic'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='outbox',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Topic'),
        ),
        migrations.AddField(
            model_name='outbox',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='msgtemplate',
            name='topic_category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.TopicCategory'),
        ),
        migrations.AddField(
            model_name='msgtemplate',
            name='topic_template',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.TopicTemplate'),
        ),
        migrations.AddField(
            model_name='msgtemplate',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='msgbatch',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.Topic'),
        ),
        migrations.AddField(
            model_name='msgbatch',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='messagingendpoint',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.Organisation'),
        ),
        migrations.AddField(
            model_name='messagingendpoint',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='messagingaccount',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.MessagingProvider'),
        ),
        migrations.AddField(
            model_name='messagingaccount',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='message',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='membership',
            name='organisations',
            field=models.ManyToManyField(to='mobiles.Organisation'),
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mobiles.AccountRole'),
        ),
        migrations.AddField(
            model_name='membership',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='eventtemplate',
            name='topic_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TopicCategory'),
        ),
        migrations.AddField(
            model_name='eventtemplate',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='event',
            name='topic',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Topic'),
        ),
        migrations.AddField(
            model_name='event',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='areacategory',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='area',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.AreaCategory'),
        ),
        migrations.AddField(
            model_name='area',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mobiles.Area'),
        ),
        migrations.AddField(
            model_name='area',
            name='post_codes',
            field=models.ManyToManyField(to='mobiles.Postcode'),
        ),
        migrations.AddField(
            model_name='area',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='accountrole',
            name='tt_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mobiles.TextivistAccount'),
        ),
        migrations.AddField(
            model_name='mobile',
            name='post_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='mobiles.Postcode'),
        ),
        migrations.AddField(
            model_name='mobile',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
