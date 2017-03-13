from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class MobileManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        mobile = self.model(phone_number=phone_number, created_date=timezone.now(), **extra_fields)
        mobile.set_password(password)
        mobile.save(using=self._db)
        return mobile

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(phone_number, password, **extra_fields)