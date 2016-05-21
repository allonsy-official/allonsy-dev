import uuid

from django.db import models

from django.contrib.auth.models import Group, User

from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class Account (models.Model):
    uuid_account = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: Remove default val for account_name, account_institution_name before production
    account_name = models.CharField(max_length=100, unique=True, default="Example University")
    account_institution_name = models.CharField(max_length=100, default="Example University")
    account_billing_title = models.CharField(max_length=100, default='TESTING')
    account_billing_attn = models.CharField(max_length=100, default='TESTING')
    account_billing_country_id = models.CharField(max_length=2, default="US")
    account_billing_province_name = models.CharField(max_length=100, default='TESTING')
    account_billing_city_name = models.CharField(max_length=100, default='TESTING')
    account_billing_PostalCode = models.CharField(max_length=10, default='TESTING')
    account_billing_street_number = models.CharField(max_length=100, default='TESTING')
    account_billing_street_name = models.CharField(max_length=100, default='TESTING')
    account_billing_ApartmentNumber = models.CharField(max_length=16, blank=True)
    account_billing_CountryCode = models.CharField(max_length=3, default='555')
    account_billing_phone_value = models.CharField(max_length=10, default='TESTING')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

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

    ORG_AFFILIATION = 'A'
    ORG_INTEREST = 'I'
    ORG_ACHIEVEMENT = 'V'
    ORG_NOSPECIAL = 'X'

    org_type_choices = (
        (UNIVERSITY, 'University'),
        (SCHOOL, 'School or College'),
        (DEPARTMENT, 'Department'),
        (OFFICE, 'Office'),
        (LECTURE, 'Class or lecture'),
        (SECTION, 'Class or lecture section'),
        (GROUP, 'Group'),
    )

    org_type_special_choices = (
        (ORG_AFFILIATION, 'Affiliation'),
        (ORG_INTEREST, 'Interest'),
        (ORG_ACHIEVEMENT, 'Achievement'),
        (ORG_NOSPECIAL, 'No special class'),
    )

    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    uuid_org = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_FullName = models.CharField(max_length=100, default='TESTING')
    org_ShortName = models.CharField(max_length=32, default='TESTING')
    org_abbreviation = models.CharField(max_length=8, default='TESTING')
    org_type = models.CharField(max_length=1, choices=org_type_choices, default=GROUP)
    org_type_special = models.CharField(max_length=1, choices=org_type_special_choices, default=ORG_NOSPECIAL)
    org_HasParent = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.org_FullName


class UserExtension (models.Model):

    ALLONSY_DEV = 'X'
    ALLONSY_STAFF = 'Z'
    ACCT_DEV = 'D'
    STAFF = 'S'
    STUDENT = 'T'

    user_type_choices = (
        (ALLONSY_DEV, 'Allonsy Developer'),
        (ALLONSY_STAFF, 'Allonsy Staff'),
        (ACCT_DEV, 'Account Developer'),
        (STAFF, 'Account Staff'),
        (STUDENT, 'Student')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    uuid_user = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name_alias = models.CharField(max_length=100, default='TESTING')
    user_role_name = models.CharField(max_length=100, default='TESTING')
    user_country_id = models.CharField(max_length=2, default='US')
    user_city_name = models.CharField(max_length=100, default='TESTING')
    user_province_name = models.CharField(max_length=100, default='TESTING')
    user_PostalCode = models.CharField(max_length=10, default='TESTING')
    user_home_street_number = models.CharField(max_length=100, default='TESTING')
    user_home_street_name = models.CharField(max_length=100, default='TESTING')
    user_home_ApartmentNumber = models.CharField(max_length=16, default='TESTING')
    user_phone_CountryCode = models.CharField(max_length=3, default='555')
    user_phone_value = models.CharField(max_length=10, default='TESTING')
    user_phone_home_CountryCode = models.CharField(max_length=3, default='555')
    user_phone_home_value = models.CharField(max_length=10, default='TESTING')
    user_personal_email_value = models.CharField(max_length=100, default='test@test.org')
    user_type = models.CharField(max_length=1, choices=user_type_choices, default='T')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    # TODO: Add logic to format US phone numbers
    # TODO: Should these fields be required in DB or better to handle with app logic?

    def __str__(self):
        return '%s' % self.user


class UserProfile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid_user = models.ForeignKey(UserExtension, on_delete=models.CASCADE)
    profile_aboutme = models.TextField(default='This user has not added any text!')
    emergency_contact_1_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_1_country_id = models.CharField(max_length=2, default='US')
    emergency_contact_1_city_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_1_province_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_1_PostalCode = models.CharField(max_length=10, default='TESTING')
    emergency_contact_1_home_street_number = models.CharField(max_length=100, default='TESTING')
    emergency_contact_1_home_street_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_1_home_ApartmentNumber = models.CharField(max_length=16, default='TESTING')
    emergency_contact_1_phone_home_CountryCode = models.CharField(max_length=3, default='555')
    emergency_contact_1_phone_home_value = models.CharField(max_length=10, default='TESTING')
    emergency_contact_1_personal_email_value = models.CharField(max_length=100, default='test@test.org')
    emergency_contact_2_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_2_country_id = models.CharField(max_length=2, default='US')
    emergency_contact_2_city_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_2_province_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_2_PostalCode = models.CharField(max_length=10, default='TESTING')
    emergency_contact_2_home_street_number = models.CharField(max_length=100, default='TESTING')
    emergency_contact_2_home_street_name = models.CharField(max_length=100, default='TESTING')
    emergency_contact_2_home_ApartmentNumber = models.CharField(max_length=16, default='TESTING')
    emergency_contact_2_phone_home_CountryCode = models.CharField(max_length=3, default='555')
    emergency_contact_2_phone_home_value = models.CharField(max_length=10, default='TESTING')
    emergency_contact_2_personal_email_value = models.CharField(max_length=100, default='test@test.org')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.user


class UserInteraction (models.Model):

    CONNECT = 'C'
    ROOMMATE = 'R'
    MESSAGE = 'M'

    interaction_type_choices = (
        (CONNECT, 'Send request to connect'),
        (ROOMMATE, 'Send request to be roommate'),
        (MESSAGE, 'Send a message')
    )

    NEW = 'O'
    READ = 'I'
    DELETED = 'X'
    BLOCKED = 'B'
    FLAGGED = 'F'

    interaction_status_choices = (
        (NEW, 'New interaction'),
        (READ, 'Reviewed interaction'),
        (DELETED, 'Deleted interaction'),
        (BLOCKED, 'Blocked interaction'),
        (FLAGGED, 'Flagged as inappropriate')
    )

    uuid_interaction = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interaction_sender = models.ManyToManyField(User, related_name='interaction_sender')
    interaction_target = models.ManyToManyField(User, related_name='interaction_target')
    interaction_type = models.CharField(max_length=1, choices=interaction_type_choices, default='M')
    interaction_status = models.CharField(max_length=1, choices=interaction_status_choices, default='O')
    interaction_subject = models.CharField(max_length=100, default='New message')
    interaction_text = models.CharField(max_length=1000, default='Hello!')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)


class Location (models.Model):

    # Villages are collections of Buildings, Suites are collections of rooms
    CAMPUS = 'C'
    VILLAGE = 'V'
    BUILDING = 'B'
    FLOOR = 'F'
    SUITE = 'S'
    ROOM = 'R'
    LOCATION = 'L'

    location_type_choices = (
        (CAMPUS, 'Campus'),
        (VILLAGE, 'Village'),
        (BUILDING, 'Building'),
        (FLOOR, 'Floor'),
        (SUITE, 'Suite'),
        (ROOM, 'Room'),
        (LOCATION, 'Location')
    )

    uuid_location = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    location_HasParent = models.BooleanField(default=True)
    # If below is selected, child will inherit address/contact data from parent
    location_InheritGeoFromParent = models.BooleanField(default=True)
    location_type = models.CharField(max_length=1, choices=location_type_choices)
    # Human readable identifier for sublocations. For example, A1 for a bed or conference table in a room
    # SubLocIdents will be concat to inherited location fullname (Richardson 100 A1)
    location_SubLocIdent = models.CharField(max_length=16, default='TESTING')
    location_FullName = models.CharField(max_length=100, default='TESTING')
    location_ShortName = models.CharField(max_length=32, default='TESTING')
    location_abbreviation = models.CharField(max_length=8, default='TESTING')
    location_country_id = models.CharField(max_length=2, default="US")
    location_province_name = models.CharField(max_length=100, default='TESTING')
    location_city_name = models.CharField(max_length=100, default='TESTING')
    location_PostalCode = models.CharField(max_length=10, default='TESTING')
    location_street_number = models.CharField(max_length=100, default='TESTING')
    location_street_name = models.CharField(max_length=100, default='TESTING')
    location_ApartmentNumber = models.CharField(max_length=16, default='TESTING')
    location_CountryCode = models.CharField(max_length=3, default='555')
    location_phone_value = models.CharField(max_length=10, default='TESTING')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location_FullName


class Epoch (models.Model):
    uuid_epoch = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    epoch_Name = models.CharField(max_length=100)
    epoch_StartDate = models.DateField()
    epoch_EndDate = models.DateField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.epoch_Name

    # Defines student-residence relationsip User ID, Period ID and Location ID
    # TODO: add PeriodDetail and LocationDetail tables
    # TODO: Form will have to control that id_period and id_residence are a set from relevant tables (distinct())
    # See http://stackoverflow.com/questions/6707991/django-modelchoicefield-using-distinct-values-from-one-model-attribute


class TreeOrganization(MPTTModel):
    relation_name = models.CharField(max_length=100, default='Test')
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    uuid_org = models.OneToOneField(Organization, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['uuid_account']

    def __str__(self):
        return self.relation_name


class TreeLocation(MPTTModel):
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    uuid_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['uuid_account']

    def __str__(self):
        thisname = Location.objects.get(location_FullName=self.uuid_location)
        return thisname.location_ShortName


# TODO: Remove blank=True before production
class RelationOrganizationUser (models.Model):
    relation_name = models.CharField(max_length=100)
    relation_url = models.CharField(max_length=100)
    relation_is_primary = models.BooleanField(default=False)
    uuid_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    uuid_user = models.ManyToManyField(UserExtension)
    uuid_org = models.ManyToManyField(Organization)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.relation_name

class RelationLocationTree (models.Model):
    uuid_location_child = models.CharField(max_length=100, blank=True)
    uuid_location_parent = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Parent: %s Child: %s' % (self.uuid_locaton_parent, self.uuid_location_child)


class RelationLocationOrganization (models.Model):
    uuid_org_child = models.CharField(max_length=100, blank=True)
    uuid_location_parent = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Parent: %s Child: %s' % (self.uuid_locaton_parent, self.uuid_org_child)


class RelationLocationUserTransact (models.Model):
    transaction_time = models.DateTimeField(auto_now_add=True)
    uuid_location_parent = models.CharField(max_length=100, blank=True)
    uuid_user_child = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Parent: %s Child: %s' % (self.uuid_locaton_parent, self.uuid_user_child)


class RelationUserLocationStatic (models.Model):
    uuid_user_parent = models.CharField(max_length=100, blank=True)
    uuid_location_child = models.CharField(max_length=100, blank=True)
    uuid_epoch_child = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('uuid_user_parent', 'uuid_location_child', 'uuid_epoch_child')

    def __str__(self):
        return 'Parent: %s Child: %s' % (self.uuid_user_parent, self.uuid_location_child)




