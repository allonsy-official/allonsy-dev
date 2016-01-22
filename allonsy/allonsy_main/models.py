from django.db import models

from django.contrib.auth.models import Group, User


# Create your models here.
class Account (models.Model):
    id_account = models.PositiveIntegerField(primary_key=True)
    # TODO: Remove default val for account_name before production
    account_name = models.CharField(max_length=100, unique=True, default="Example University")

    def __str__(self):
        return self.account_name


class Organization (models.Model):

    UNIVERSITY = 'U'
    SCHOOL = 'S'
    DEPARTMENT = 'D'
    OFFICE = 'O'
    LECTURE = 'L'
    SECTION = 'E'
    GROUP = 'G'

    org_type_choices = (
        (UNIVERSITY, 'University'),
        (SCHOOL, 'School or College'),
        (DEPARTMENT, 'Department'),
        (OFFICE, 'Office'),
        (LECTURE, 'Class or lecture'),
        (SECTION, 'Class or lecture section'),
        (GROUP, 'Group'),
    )

    id_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    id_org = models.PositiveIntegerField(primary_key=True)
    org_FullName = models.CharField(max_length=100)
    org_ShortName = models.CharField(max_length=20)
    org_type = models.CharField(max_length=1, choices=org_type_choices, default=GROUP)
    org_HasParent = models.BooleanField(default=False)

    def __str__(self):
        return self.org_FullName

class UserExtension (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user_name_first = models.OneToOneField(User.first_name, on_delete=models.CASCADE)
    # user_name_last = models.OneToOneField(User.last_name, on_delete=models.CASCADE)
    id_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    id_user = models.PositiveIntegerField(primary_key=True)
    user_name_alias = models.CharField(max_length=100)
    # user_email = models.OneToOneField(User.email, on_delete=models.CASCADE)
    user_country_id = models.CharField(max_length=2, default='US')
    user_city_name = models.CharField(max_length=100)
    user_province_name = models.CharField(max_length=100)
    user_postal_code = models.CharField(max_length=10)
    user_home_street_number = models.CharField(max_length=100)
    user_home_street_name = models.CharField(max_length=100)
    user_home_ApartmentNumber = models.CharField(max_length=16)
    user_phone_CountryCode = models.IntegerField(max_length=3)
    user_phone_value = models.IntegerField(max_length=10)
    user_phone_home_CountryCode = models.IntegerField(max_length=3)
    user_phone_home_value = models.IntegerField(max_length=10)
    #TODO: Add logic to format US phone numbers
    #TODO: Should these fields be required in DB or better to handle with app logic?

    def __str__(self):
        return '%s %s' % (self.user_name_first, self.user_name_last)


class RelationsMeepleOnCampusResidence (models.Model):
    # Defines student-residence relationsip User ID, Period ID and Location ID
    # TODO: add PeriodDetail and LocationDetail tables
    # TODO: Form will have to control that id_peiod and id_residence are a set from relevant tables (distinct())
    # See http://stackoverflow.com/questions/6707991/django-modelchoicefield-using-distinct-values-from-one-model-attribute
    id_user = models.OneToOneField(UserExtension.id_user, on_delete=models.CASCADE, primary_key=True)
    id_period = models.CharField(max_length=100)
    id_residence = models.CharField(max_length=100)

    def __str__(self):
        return 'User ID # %s resides in %s' % (self.id_user, self.id_residence)
