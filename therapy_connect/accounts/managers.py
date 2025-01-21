from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, mobile_number, first_name, last_name, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not mobile_number:
            raise ValueError("User must have a mobile number")
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")

        user = self.model(
            email=self.normalize_email(email),
            mobile_number=mobile_number,
            first_name=first_name,
            last_name=last_name,
            username=email,  # Set username to email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, mobile_number, first_name, last_name, password=None
    ):
        user = self.create_user(
            email=email,
            mobile_number=mobile_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
