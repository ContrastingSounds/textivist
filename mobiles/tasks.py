from celery import shared_task
from django.utils import timezone
from twilio.exceptions import TwilioException
from twilio.rest import TwilioRestClient

from .models import MessagingEndPoint, Membership, Mobile, Subscription, Topic, AreaCategory, Area, Outbox, MsgBatch


def send_pending_messages():
    """Checks for pending messages in the outbox, and transmits any found."""
    outgoing_messages = Outbox.objects.filter(state='PENDING')
    for outgoing_message in outgoing_messages:
        client = TwilioRestClient(
            outgoing_message.endpoint.account_sid,
            outgoing_message.endpoint.auth_token
        )

        try:
            client.messages.create(
                body=outgoing_message.body,
                to=outgoing_message.to_mobile,
                from_=outgoing_message.endpoint.endpoint_address,
            )
            outgoing_message.sent = timezone.now()
            outgoing_message.state = 'SENT'
            outgoing_message.save()
        except TwilioException as e:
            print(e)


def send_sms(endpoint, phone, body):
    """Places SMS in send queue. All messages are logged to database before transmission."""
    if type(endpoint) == str:
        endpoint = MessagingEndPoint.objects.get(endpoint_address=endpoint)

    Outbox.objects.create(
        tt_account=endpoint.tt_account,
        to_mobile=phone,
        endpoint=endpoint,
        body=body,
        state='PENDING'
    )

    send_pending_messages()


def sms_error(endpoint, phone, commands=None, parameters=None):
    """Sends generic 'message not understood' error text."""
    send_sms(
        endpoint,
        phone,
        'Text received by Textivist, but not understood.'
    )


def validate_phone(endpoint, phone):
    """Checks whether a mobile is registered. Returns Mobile object if verified, or None if not. """
    try:
        mobile = Mobile.objects.get(phone_number=phone)
        return mobile
    except Mobile.DoesNotExist:
        send_sms(
            endpoint,
            phone,
            'Textivist does not have an account for {}.\n\n'
            'Reply REGISTER to get an account.'.format(
                phone
            )
        )
        return None


def sms_register(endpoint, phone, commands=None, parameters=None):
    tt_account = endpoint.tt_account
    organisation = endpoint.organisation

    try:
        mobile = Mobile.objects.get(phone_number=phone)
    except Mobile.DoesNotExist:
        mobile = Mobile.objects.create(
            phone_number=phone,
            created_date=timezone.now(),
            last_texted=timezone.now(),
            state='REQUESTED'
        )

    try:
        membership = Membership.objects.get(tt_account=tt_account, mobile=mobile)
    except Membership.DoesNotExist:
        membership = Membership.objects.create(
            tt_account=tt_account,
            mobile=mobile,
            created_date=timezone.now()
        )
        membership.save()

    membership.organisations.add(organisation)

    body = 'Textivist account verified for {}\n\n' \
            'Membership to {} added.'.format(
                mobile.phone_number,
                organisation.name
            )
    send_sms(endpoint.endpoint_address, mobile.phone_number, body)


def sms_add(endpoint, phone, commands, parameters=None):
    mobile = validate_phone(endpoint, phone)

    if mobile:
        try:
            topic = commands[0]
            try:
                topic = Topic.objects.get(shortcode=topic, tt_account=endpoint.tt_account)
            except Topic.DoesNotExist:
                # Topic shortcode not found therefore send error text and return
                send_sms(
                    endpoint,
                    phone,
                    'Was not able to find {} topic with code of "{}".'.format(
                        endpoint.tt_account.name,
                        topic
                    )
                )
                return

            priority = 'NORMAL'
            Subscription.objects.create(
                tt_account=endpoint.tt_account,
                phone_number=mobile,
                topic=topic,
                priority=priority,
                subscribed_date=timezone.now()
            )
            send_sms(
                endpoint,
                phone,
                'Subscribed to {} on behalf of {}.'.format(
                    topic,
                    phone
                )
            )

        except IndexError:
            send_sms(
                endpoint,
                phone,
                'Message failed!\n'
                'ADD (Subscription) commands require a topic shortcode.'
            )


def sms_filter(endpoint, phone, commands, parameters):
    mobile = validate_phone(endpoint, phone)
    if mobile:
        try:
            topic = commands[0]
            topic = Topic.objects.get(shortcode=topic, tt_account=endpoint.tt_account)
        except IndexError:
            send_sms(
                endpoint,
                phone,
                'FILTER commands require a topic shortcode'
            )
        except Topic.DoesNotExist:
            send_sms(
                endpoint,
                phone,
                'Unable to find {} topic with shortcode "{}".'.format(
                    endpoint.tt_account.name,
                    topic
                )
            )
            return

        try:
            subscription = Subscription.objects.get(phone_number=phone, topic=topic)
        except Subscription.DoesNotExist:
            send_sms(
                endpoint,
                phone,
                'Unable able to find subscription to {} from {}.'.format(
                    topic,
                    endpoint.tt_account.name
                )
            )
            return

        area, area_category = parameters[0:2]
        try:
            area_category = AreaCategory.objects.get(name=area_category)
            area = Area.objects.get(category=area_category, name=area)
        except AreaCategory.DoesNotExist:
            send_sms(
                endpoint,
                phone,
                'Could not find Area Category'
            )
            return
        except Area.DoesNotExist:
            send_sms(
                endpoint,
                phone,
                'Could not find Area'
            )
            return

        subscription.area = area
        subscription.save()
        send_sms(
            endpoint,
            phone,
            'Subscription to {} filtered to area {}'.format(
                topic,
                area
            )
        )


def sms_mute(endpoint, phone, commands, parameters=None):
    mobile = validate_phone(endpoint, phone)
    if mobile:
        try:
            topic = commands[0]
            try:
                topic = Topic.objects.get(shortcode=topic)
                subscription = Subscription.objects.get(phone_number=mobile, topic=topic)
            except Topic.DoesNotExist:
                send_sms(
                    endpoint,
                    phone,
                    'Could not find a topic with shortcode of "{}".'.format(
                        topic
                    )
                )
                return
            except Subscription.DoesNotExist:
                send_sms(
                    endpoint,
                    phone,
                    'Could not find subscription to {}.'.format(
                        topic
                    )
                )
                return

            subscription.cancelled_date = timezone.now()
            subscription.state = 'INACTIVE'
            subscription.save()
            send_sms(
                endpoint,
                phone,
                'Subscription to {} cancelled.'.format(
                    topic
                )
            )

        except Exception as e:
            print(e)


def sms_stop(endpoint, phone, commands=None, parameters=None):
    try:
        mobile = Mobile.objects.get(pk=phone)
        mobile.state = 'INACTIVE'
        mobile.save()
    except Exception as e:
        print(e)


def sms_set(endpoint, phone, commands, parameters):
    mobile = validate_phone(endpoint, phone)

    if mobile:
        if endpoint.organisation.owner != mobile:
            send_sms(
                endpoint,
                phone,
                'Permission denied.'
            )
            return
        def set_owner(parameters):
            try:
                mobile.first_name = parameters[0]
            except IndexError:
                pass

            try:
                mobile.last_name = parameters[1]
            except IndexError:
                pass

            mobile.save()

            send_sms(
                endpoint,
                phone,
                'Setting named owner of {} to {} {}'.format(
                    phone,
                    mobile.first_name,
                    mobile.last_name
                )
            )

        def set_error():
            send_sms(
                endpoint,
                phone,
                'SET message received, but not understood.'
            )

        set_commands = {
            'OWNER': set_owner,
        }

        try:
            command = commands[0]
        except IndexError:
            command = 'OWNER'

        try:
            set_commands[command](parameters)
        except KeyError:
            set_error()


def sms_cast(endpoint, phone, commands, parameters):
    mobile = validate_phone(endpoint, phone)
    if mobile:
        try:
            topic = commands[0]
        except IndexError:
            send_sms(
                endpoint,
                phone,
                'Message failed!\n'
                'Broadcasting texts require a topic shortcode.'
            )
            return

        try:
            topic = Topic.objects.get(shortcode=topic, tt_account=endpoint.tt_account)
            if topic.owner != mobile:
                send_sms(
                    endpoint,
                    phone,
                    'Permission denied.'
                )
                return
        except Topic.DoesNotExist:
            send_sms(
                endpoint,
                phone,
                'Cannot broadcast message. Could not find a {} topic with shortcode of "{}".'.format(
                    endpoint.tt_account.name,
                    topic
                )
            )
            return

        body = ' '.join(commands[1:] + parameters)
        send_sms(
            endpoint,
            phone,
            'Broadcasting to {}: {}'.format(
                topic,
                body
            )
        )
        subscribers = Subscription.objects.filter(topic=topic)
        for subscription in subscribers:
            Outbox.objects.create(
                tt_account=endpoint.tt_account,
                topic=topic,
                priority='NORMAL',
                to_mobile=subscription.phone_number.phone_number,
                endpoint=endpoint,
                body=body,
                state='PENDING'
            )

        send_pending_messages()


sms_commands = {
    'REGISTER': sms_register,

    # Industry standard subscribe/re-subscribe codes, enforced by providers
    'START': sms_register,
    'YES': sms_register,
    'UNSTOP': sms_register,

    # Industry standard stop/unsubscribe codes, enforced by provides
    'STOP': sms_stop,
    'STOPALL': sms_stop,
    'UNSUBSCRIBE': sms_stop,
    'CANCEL': sms_stop,
    'END': sms_stop,
    'QUIT': sms_stop,

    'ADD': sms_add,
    'FILTER': sms_filter,
    'MUTE': sms_mute,
    'SET': sms_set,
    'CAST': sms_cast,
    'ERROR': sms_error,
}


@shared_task
def handle_sms(endpoint, sms_from, commands, parameters):
    """Converts endpoint address to Django object, and calls appropriate function"""
    try:
        endpoint = MessagingEndPoint.objects.get(endpoint_address=endpoint)
    except MessagingEndPoint.DoesNotExist as e:
        print(e)
        return

    try:
        command = commands[0]
    except IndexError:
        command = 'ERROR'

    if len(commands) > 1:
        additional_commands = commands[1:]
    else:
        additional_commands = []

    try:
        sms_commands[command](endpoint, sms_from, additional_commands, parameters)
    except KeyError:
        sms_commands['ERROR'](endpoint, sms_from, additional_commands, parameters)

    # sms_commands[command](endpoint, sms_from, additional_commands, parameters)

@shared_task
def send_message_batches():
    """Send any message batches due to run"""

    batch_jobs = MsgBatch.objects.filter(state='PENDING', to_send__lte=timezone.now())
    for batch in batch_jobs:
        subscriptions = Subscription.objects.filter(topic=batch.topic)
        for subscription in subscriptions:
            Outbox.objects.create(
                tt_account=batch.tt_account,
                topic=batch.topic,
                priority=batch.priority,
                to_mobile=subscription.phone_number.phone_number,
                endpoint=batch.endpoint,
                body=batch.body,
                state='PENDING'
            )

        batch.state = 'SENT'
        batch.was_sent = timezone.now()
        batch.save()

    send_pending_messages()