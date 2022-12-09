from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from api.v1.users.enums import UserRoles
from django.db.models.query import QuerySet


class UserManager(BaseUserManager):

    def create_user(self, email, password, phone, first_name, last_name, organization_id, role, **extra_fields):

        if not email:
            raise ValueError('The email must not be empty')
        if not phone:
            raise ValueError('The user must have a Phonenumber')
        if not first_name:
            raise ValueError('The user must have a First Name')
        if not last_name:
            raise ValueError('The user must have a Last Name')
        if not organization_id:
            raise ValueError('The user must have a Organization')
        if not role:
            raise ValueError('The user must have a role')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            organization_id=organization_id,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, phone, first_name, last_name, organization, role, **extra_fields):
        """
            Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(
            email=email,
            phone=phone,
            first_name=first_name,
            password=password,
            last_name=last_name,
            organization_id=organization,
            role=role,
        )
        user.is_varified = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    

class SourcingDirectorManager(UserManager.from_queryset(QuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(role=UserRoles.sourcing_director.value)