import uuid, random

from django.db import models

from django.contrib.auth.models import Group, User

from mptt.models import MPTTModel, TreeForeignKey

from allonsy_schemas import models as allonsy_schema_models


# Create your models here.
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
    ORG_RESLIFE = 'R'
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
        (ORG_RESLIFE, 'Residence Life'),
        (ORG_NOSPECIAL, 'No special class'),
    )

    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
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
    ACCT_ADM = 'A'
    STAFF = 'S'
    STUDENT = 'T'

    user_type_choices = (
        (ALLONSY_DEV, 'Allonsy Developer'),
        (ALLONSY_STAFF, 'Allonsy Staff'),
        (ACCT_DEV, 'Account Developer'),
        (ACCT_ADM, 'Account Admin'),
        (STAFF, 'Account Staff'),
        (STUDENT, 'Student')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
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


class UserAlert (models.Model):

    REMINDER = 'R'
    OVERDUE = 'O'
    ALERT = 'A'

    interaction_type_choices = (
        (REMINDER, 'Reminder'),
        (OVERDUE, 'Overdue'),
        (ALERT, 'Alert')
    )

    RECEIVED = 'R'
    DROPPED = 'D'

    interaction_direction_choices = (
        (RECEIVED, 'Target of this interaction'),
        (DROPPED, 'Dropped message')
    )

    NEW = 'O'
    READ = 'I'
    DELETED = 'X'

    interaction_status_choices = (
        (NEW, 'New interaction'),
        (READ, 'Reviewed interaction'),
        (DELETED, 'Deleted interaction'),
    )

    uuid_alert = models.UUIDField(default=uuid.uuid4)
    interaction_direction = models.CharField(max_length=1, choices=interaction_direction_choices, default=DROPPED)
    interaction_status = models.CharField(max_length=1, choices=interaction_status_choices, default=NEW)
    interaction_sender = models.ManyToManyField(User, related_name='alert_sender')
    interaction_target = models.ManyToManyField(User, related_name='alert_target')
    interaction_type = models.CharField(max_length=1, choices=interaction_type_choices, default=ALERT)
    interaction_subject = models.CharField(max_length=100, default='New message')
    interaction_text = models.CharField(max_length=1000, default='Hello!')
    date_active_start = models.DateTimeField()
    date_active_end = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.interaction_text


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
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
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
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
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
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
    uuid_org = models.OneToOneField(Organization, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['uuid_account']

    def __str__(self):
        return self.relation_name


class TreeLocation(MPTTModel):
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
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
    # Creates a permission for each User-Org assoc. By default, students have read-only on the immediate group (and
    # child groups?), faculty will have read-only on immediate group and -rw on child groups, with ability to create
    # children, staff will have -rw on immediate and child, with ability to create children, and admin will have
    # create/delete on the parent and all children. Any user may assign a task to a group for which they have -w.

    relation_name = models.CharField(max_length=100)
    relation_url = models.CharField(max_length=100)
    relation_is_primary = models.BooleanField(default=False)
    uuid_account = models.ForeignKey(allonsy_schema_models.Account, on_delete=models.CASCADE)
    uuid_user = models.ManyToManyField(UserExtension)
    uuid_org = models.ManyToManyField(Organization)
    permission_is_admin = models.BooleanField(default=False)
    permission_is_staff = models.BooleanField(default=False)
    permission_is_faculty = models.BooleanField(default=False)
    permission_is_student = models.BooleanField(default=True)
    permission_is_expired = models.BooleanField(default=False)
    #TODO: Allow users to upload permission templates via XML, for example
    permission_template = models.CharField(max_length=100)
    date_active = models.DateTimeField()
    date_expires = models.DateTimeField()
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


class RelationUserConnection (models.Model):
    ACTIVE = 'A'
    PENDING = 'P'
    REJECTED = 'R'
    DROPPED = 'D'

    relation_status_choices = (
        (ACTIVE, 'Active connection'),
        (PENDING, 'Pending connection'),
        (REJECTED, 'Rejected connection'),
        (DROPPED, 'Dropped connection'),
    )

    PERSONAL = 'L'
    ROOMMATE = 'M'
    GROUP = 'G'

    connection_type_choices = (
        (PERSONAL, 'Personal connection'),
        (ROOMMATE, 'Roommate connection'),
        #(GROUP, 'Group connection'),
    )

    uuid_relation = models.UUIDField(default=uuid.uuid4, editable=False)
    uuid_user_1 = models.ManyToManyField(User, related_name='uuid_user_1')
    uuid_user_2 = models.ManyToManyField(User, related_name='uuid_user_2')
    relation_type = models.CharField(max_length=255, choices=connection_type_choices)
    relation_status = models.CharField(max_length=255, choices=relation_status_choices)
    relation_expires = models.DateTimeField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.uuid_relation)


class UserInteractionTree (MPTTModel):

    CONNECT = 'C'
    ROOMMATE = 'R'
    MESSAGE = 'M'

    interaction_type_choices = (
        (CONNECT, 'Connection request'),
        (ROOMMATE, 'Roommate request'),
        (MESSAGE, 'Message')
    )

    RECEIVED = 'R'
    SENT = 'S'
    DROPPED = 'D'

    interaction_direction_choices = (
        (RECEIVED, 'Target of this interaction'),
        (SENT, 'Sender of this interaction'),
        (DROPPED, 'Dropped message')
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
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    #interaction_direction = models.CharField(max_length=1, choices=interaction_direction_choices, default=DROPPED)
    interaction_status = models.CharField(max_length=1, choices=interaction_status_choices, default=NEW)
    interaction_sender = models.ManyToManyField(User, related_name='interaction_sender')
    interaction_target = models.ManyToManyField(User, related_name='interaction_target')
    interaction_type = models.CharField(max_length=1, choices=interaction_type_choices, default=MESSAGE)
    interaction_subject = models.CharField(max_length=100, default='New message')
    interaction_text = models.CharField(max_length=1000, default='Hello!')
    uuid_request = models.ManyToManyField(RelationUserConnection, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['date_added']

    def __str__(self):
        return str(self.uuid_interaction)


'''class WorkflowItemTree (MPTTModel):

    WFSET = 'S'
    WFITEM = 'I'
    WFITEMTEXT = 'T'

    wf_item_is_type_choices = (
        (WFSET, 'Workflow Set'),
        (WFITEM, 'Workflow Item'),
        (WFITEMTEXT, 'Item body text'),
    )

    NOSET = 'X'
    ROUNDS = 'N'
    DUTY = 'D'
    CHECKIN = 'I'
    CHECKOUT = 'O'

    wf_set_is_type_choices = (
        (NOSET, 'No group set'),
        (ROUNDS, 'Nightly rounds'),
        (DUTY, 'On-call duty'),
        (CHECKIN, 'Room check-in'),
        (CHECKOUT, 'Room check-out')
    )

    uuid_wf_item = models.UUIDField(primary_key=True, editable=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    wf_item_name = models.CharField(max_length=64, default=uuid_wf_item)
    wf_item_type = models.CharField(max_length=1, choices=wf_item_is_type_choices, default=WFSET)
    wf_item_is_active = models.BooleanField(default=True)
    wf_item_text = models.CharField(max_length=256, blank=True)
    wf_set_is_type = models.CharField(max_length=1, choices=wf_set_is_type_choices, default=NOSET)
    wf_set_is_default_parent_for_type = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['date_added']

    def __str__(self):
        return str(self.uuid_wf_item)'''


class WorkflowSet (models.Model):

    NOSET = 'X'
    ROUNDS = 'N'
    DUTY = 'D'
    CHECKIN = 'I'
    CHECKOUT = 'O'

    wf_set_is_type_choices = (
        (NOSET, 'No group set'),
        (ROUNDS, 'Nightly rounds'),
        (DUTY, 'On-call duty'),
        (CHECKIN, 'Room check-in'),
        (CHECKOUT, 'Room check-out')
    )

    uuid_wf_set = models.UUIDField(default=uuid.uuid4, editable=False)
    wf_set_name = models.CharField(max_length=64, default=uuid_wf_set)
    wf_set_is_type = models.CharField(max_length=1, choices=wf_set_is_type_choices, default=NOSET)
    wf_set_is_default_parent_for_type = models.BooleanField(default=False)
    wf_set_has_child = models.BooleanField(default=False)
    wf_set_is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.wf_set_name)


class RelationWorkflow (models.Model):
    uuid_relation = models.UUIDField(default=uuid.uuid4, editable=False)
    wf_parent = models.ManyToManyField(WorkflowSet, related_name='wf_parent', blank=True)
    wf_child = models.ManyToManyField(WorkflowSet, related_name='wf_child', blank=True)
    wf_disp_order = models.CharField(max_length=2, default='1')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.uuid_relation)


class WorkflowItem (models.Model):
    uuid_wf_item = models.UUIDField(default=uuid.uuid4, editable=False)
    wf_item_is_active = models.BooleanField(default=True)
    wf_item_parent_wfset = models.ManyToManyField(WorkflowSet, blank=True)
    wf_item_name = models.CharField(max_length=64, blank=True)
    wf_item_text = models.CharField(max_length=256, blank=True)
    wf_item_disp_order = models.CharField(max_length=2, default='1')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.wf_item_name)


class WorkflowDocumentMaster (models.Model):
    # TODO: Ensure that changes to parent form do not show after create (or perhaps submit)

    CREATE = 'C'
    INPROG = 'I'
    SUBMIT = 'S'
    REVIEW = 'R'
    APPROVE = 'A'
    COMPLETE = 'O'

    user_instance_state_choices = (
        (CREATE, 'Created'),
        (INPROG, 'Edited and saved'),
        (SUBMIT, 'Submitted for review'),
        (REVIEW, 'Reverted for edit'),
        (APPROVE, 'Approved'),
        (COMPLETE, 'Saved as complete')
    )

    uuid_doc = models.UUIDField(default=uuid.uuid4, editable=False)
    uuid_wf_user = models.ManyToManyField(User, related_name='user')
    uuid_wf_edited_user = models.ManyToManyField(User, related_name='edited_by')
    user_instance_name = models.CharField(max_length=256, default='New form')
    user_instance_state = models.CharField(max_length=1, choices=user_instance_state_choices, default=CREATE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)


class WorkflowDocumentItem (models.Model):
    # TODO: Split instance from relation so that an instance can be tracked through multiple user transactions

    uuid_doc_item = models.UUIDField(default=uuid.uuid4, editable=False)
    uuid_doc = models.ManyToManyField(WorkflowDocumentMaster, related_name='document_parent')
    wf_item_root_parent = models.ManyToManyField(WorkflowSet, related_name='root_parent')
    wf_parent_set_name = models.CharField(max_length=64)
    wf_item_sub_parent = models.ManyToManyField(WorkflowSet, related_name='immediate_parent')
    wf_sub_parent_set_name = models.CharField(max_length=64)
    wf_item_sub_parent_disp_order = models.CharField(max_length=2, default='1')
    wf_item_text = models.CharField(max_length=256, blank=True)
    user_item_state = models.CharField(max_length=16, default='Off')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)


