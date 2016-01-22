from django.db import models

from django.contrib.auth.models import User


# Create your models here.

class UserExtension(models.Model):
    STUDENT = 'STU'
    STUDENTSTAFF = 'RAS'
    STAFF = 'STA'
    STAFFADMIN = 'ADM'
    ITSERVICE = 'ITS'
    ITDEVELOPER = 'ITD'
    ALLONSYDEVELOPER = 'XAD'
    ALLONSYADMIN = 'XAA'
    ALLONSYSUPERUSER = 'XAS'

    user_role_choices = (
        (STUDENT, 'Student'),
        (STUDENTSTAFF, 'Student Staff'),
        (STAFF, 'Staff'),
        (STAFFADMIN, 'Staff Admin'),
        (ITSERVICE, 'IT Service'),
        (ITDEVELOPER, 'IT Development'),
        (ALLONSYDEVELOPER, 'Allonsy Developer'),
        (ALLONSYADMIN, 'Allonsy Admin'),
        (ALLONSYSUPERUSER, 'Allonsy Superuser'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.PositiveIntegerField(primary_key=True)
    user_role = models.CharField(max_length=3,
                                 choices=user_role_choices,
                                 default=STUDENT)

    class Choice(models.Model):
        def __str__(self):
            return self.id_user


class MeepleBasic (models.Model)
    id_user = models.OneToOneField(UserExtension.id_user, on_delete=models.CASCADE)