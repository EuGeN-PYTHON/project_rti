import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rti_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tariffs.models import Lead


def create_operator_group():
    # Создаем группу операторов
    operator_group, created = Group.objects.get_or_create(name='Operators')

    if created:
        # Добавляем права на работу с заявками
        content_type = ContentType.objects.get_for_model(Lead)
        permissions = Permission.objects.filter(content_type=content_type)

        for permission in permissions:
            operator_group.permissions.add(permission)

        print('Группа Operators создана с правами на работу с заявками')
    else:
        print('Группа Operators уже существует')


if __name__ == '__main__':
    create_operator_group()