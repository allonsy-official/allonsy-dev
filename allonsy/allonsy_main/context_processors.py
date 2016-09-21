from allonsy_main.models import UserExtension, User, UserProfile, Organization, RelationOrganizationUser, UserAlert, UserInteractionTree
from allonsy_schemas.models import Account
from django.db.models import Q


def base_user(request):
    current_user = request.user

    if request.user.is_authenticated():

        try:
            current_user_id = current_user.id
            user_extension = UserExtension.objects.get(user=current_user_id)
            user_extension_object = UserExtension.objects.get(user=current_user_id)
            #user_account = Account.objects.get(account_name=user_extension.uuid_account)
            #user_account_url = user_account.account_url_name

            return {
                'user_extension_object': user_extension_object,
                #'user_account_url': user_account_url,
            }

        except UserExtension.DoesNotExist:

            return {
                'user_extension_object': '!',
                'user_account_url': '!',
            }

    else:
        return {
            'user_extension_object': '!',
            'user_account_url': '!',
        }


def base_interactions(request):
    current_user = request.user

    if request.user.is_authenticated():
        current_user_interactions = UserInteractionTree.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O'))
        current_user_alerts = UserAlert.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O'))
        count_current_user_interactions = UserInteractionTree.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O')).count()
        count_current_user_alerts = UserAlert.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O')).count()
        total_interactions = count_current_user_interactions + count_current_user_alerts

        return {
            'current_user_interactions': current_user_interactions,
            'current_user_alerts': current_user_alerts,
            'count_current_user_interactions': count_current_user_interactions,
            'count_current_user_alerts': count_current_user_alerts,
            'total_interactions': total_interactions,
        }

    else:
        return {
            'count_current_user_interactions': '!',
            'count_current_user_alerts': '!',
        }

