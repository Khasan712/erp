from django.db import models
from django.core.exceptions import ValidationError

from api.v1.users.managers import (
    UserManager,
    SourcingDirectorManager
)
from api.v1.organization.models import Organization
from django.contrib.auth.models import (
    AbstractBaseUser, 
    PermissionsMixin
)
from .enums import UserRoles


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=50)
    role = models.CharField(max_length=22, choices=UserRoles.choices())
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_varified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'organization']

    def __str__(self) -> str:
        return f'{self.email}'

    def save(self, *args, **kwargs):
        if self.role != 'admin' and not self.organization:
            raise ValidationError('User must be choose one organization!!!')
        super().save(*args, **kwargs)

    # @property
    # def token(self):
    #     return self._generate_jwt_token()

    # def _generate_jwt_token(self):
    #     dt = datetime.now() + timedelta(days=60)

    #     token = jwt.encode({
    #         'id': self.pk,
    #         'exp': int(dt.strftime('%s'))
    #     }, settings.SECRET_KEY, algorithm='HS256')

    #     return token.decode('utf-8')

    # def save(self, *args, **kwargs):

    #     if self.is_admin == True:
    #         self.is_staff = True
    #         self.is_superuser = True
    #     return super().save(*args, **kwargs)
    

class SourcingDirector(User):
    objects = SourcingDirectorManager()

    class Meta:
        proxy = True
