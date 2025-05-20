from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, first_name, password, last_name=None, **extra_fields):
        """
        Create and save a user with the given phone number, first name, and password.
        """
        if not phone_number:
            raise ValueError('The given phone number must be set')
        if not first_name:
            raise ValueError('The given first name must be set')
            
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, first_name, password=None, last_name=None, **extra_fields):
        """
        Create and save a regular user with the given phone number and first name.
        """
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, first_name, password, last_name, **extra_fields)

    def create_superuser(self, phone_number, first_name, password=None, last_name=None, **extra_fields):
        """
        Create and save a SuperUser with the given phone number and first name.
        """
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_phone_verified', True)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, first_name, password, last_name, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()