from django.contrib import admin

from .models import Mobile, Command, AuditLog
from .models import TextivistAccount, Postcode, AreaCategory, Area, Organisation, AccountRole, Membership
from .models import MessagingProvider, MessagingAccount, MessagingEndPoint
from .models import TopicCategory, TopicTemplate, EventTemplate, MsgTemplate, Topic, Event, Subscription
from .models import MsgBatch, Message


class MobileAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'title', 'last_name', 'first_name', 'created_date', 'last_texted', 'state')
    list_filter = ('last_texted',)
admin.site.register(Mobile, MobileAdmin)

admin.site.register(Command)
admin.site.register(AuditLog)

admin.site.register(TextivistAccount)
admin.site.register(Postcode)
admin.site.register(AreaCategory)
admin.site.register(Area)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('parent', 'name', 'owner')
    list_display_links = ('name',)
    list_filter = ('areas', 'owner')
    ordering = ('parent', 'name')
admin.site.register(Organisation, OrganisationAdmin)

admin.site.register(AccountRole)
admin.site.register(Membership)

admin.site.register(MessagingProvider)
admin.site.register(MessagingAccount)
admin.site.register(MessagingEndPoint)

admin.site.register(TopicCategory)
admin.site.register(TopicTemplate)
admin.site.register(EventTemplate)
admin.site.register(MsgTemplate)


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_category')
admin.site.register(Topic, TopicAdmin)

admin.site.register(Event)
admin.site.register(Subscription)

admin.site.register(MsgBatch)
admin.site.register(Message)


