from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^user/$', views.usr, name='user'),
    url(r'^user/(?P<username>\w+)/$', views.resolve_user_url, name='resolve_user_url'),
    url(r'^user/(?P<username>\w+)/edit/profile', views.do_edit_user_profile, name='do_edit_user_profile'),
    url(r'^user/(?P<username>\w+)/edit/contact', views.do_edit_user_info_contact, name='do_edit_user_info_contact'),
    url(r'^user/(?P<username>\w+)/edit/emergencycontacts', views.do_edit_user_emergency_contact, name='do_edit_user_emergency_contacts'),
    url(r'^user/(?P<username>\w+)/interactions/connect/$', views.do_user_connect, name='do_user_connect'),
    url(r'^user/(?P<username>\w+)/interactions/status/(?P<status>\w+)/(?P<cstatus>\w+)/(?P<uuidmsg>[^/]+)/$', views.do_update_connect_status, name='do_update_connect_status'),
    url(r'^user/(?P<username>\w+)/interactions/$', views.do_get_user_interactions, name='do_get_user_interactions'),
    url(r'^user/(?P<username>\w+)/interactions/reply/(?P<uuidmsg>[^/]+)/$', views.do_send_reply_message, name='do_send_reply_message'),
    url(r'^user/(?P<username>\w+)/interactions/send/$', views.do_send_message, name='do_send_message'),
    url(r'^user/(?P<username>\w+)/interactions/status/(?P<status>\w+)/(?P<uuidmsg>[^/]+)/$', views.do_update_msg_status, name='do_update_msg_status'),
    url(r'^user/(?P<username>\w+)/interactions/sent/$', views.do_get_user_sent, name='do_get_user_sent'),
    url(r'^user/(?P<username>\w+)/alerts/$', views.do_get_user_alerts, name='do_get_user_alerts'),
    url(r'^user/(?P<username>\w+)/alerts/status/(?P<status>\w+)/(?P<uuidmsg>[^/]+)/$', views.do_update_alert_status, name='do_update_alert_status'),
    url(r'^user/(?P<username>\w+)/roles/$', views.roles_dashboard, name='roles_dashboard'),
    url(r'^user/(?P<username>\w+)/roles/oncall/$', views.roles_oncall, name='roles_oncall'),
    url(r'^user/(?P<username>\w+)/roles/c/(?P<uuidparentnode>[^/]+)/$', views.do_create_wf_instance, name='do_create_wf_instance'),
    url(r'^user/(?P<username>\w+)/roles/i/(?P<uuidparentnode>[^/]+)/$', views.do_edit_wf_instance, name='do_edit_wf_instance'),
    url(r'^user/(?P<username>\w+)/roles/m/(?P<uuidparentnode>[^/]+)/$', views.do_edit_wf_instance_meta, name='do_edit_wf_instance_meta'),
    url(r'^user/(?P<username>\w+)/roles/z/(?P<uuidparentnode>[^/]+)/$', views.check_wf_before_complete, name='check_wf_before_complete'),
    url(r'^user/(?P<username>\w+)/roles/u/(?P<statuscode>[^/]+)/(?P<uuidparentnode>[^/]+)/$', views.wf_status_update, name='wf_status_update'),
    url(r'^user/(?P<username>\w+)/roles/onduty$', views.roles_onduty, name='roles_onduty'),
    # TODO: Extend the below so one function handles all calls for new reports. Need to figure out regex for lookup
    url(r'^user/(?P<username>\w+)/roles/r/c/(?P<rpttype>\w+)/$', views.roles_rpt_create_new, name='roles_rpt_create_new'),
    # url(r'^user/(?P<username>\w+)/roles/r/(?P<uuidrpt>[^/]+)/$', views.roles_get_report, name='roles_get_report'),
    url(r'^account/admin/$', views.user_admin, name='user_admin'),
    url(r'^org/(?P<orgname>[-\w]+)/$', views.resolve_org_url, name='resolve_org_url'),
    url(r'^create/$', views.create, name='create'),
    url(r'^account/admin/create/user/do/$', views.do_add_user, name='do_add_user'),
    url(r'^account/admin/create/account/do/$', views.do_add_account, name='do_add_account'),
    url(r'^account/admin/create/location/do/$', views.do_add_location, name='do_add_location'),
    # url(r'^account/admin/workflow/$', views.wf_set_add_or_edit, name='wf_set_add_or_edit'),  # remove when tree complete
    url(r'^account/admin/workflow/$', views.wf_tree_node_add_or_edit, name='wf_tree_node_add_or_edit'),
    url(r'^account/admin/workflow/e/c/(?P<uuidwfparent>[^/]+)/$', views.wf_set_add_children, name='wf_set_add_children'),
    # url(r'^account/admin/workflow/e/$', views.wf_set_add_children, name='wf_set_add_children'),
    url(r'^account/admin/workflow/e/$', views.get_tree_node_for_add_item_1, name='get_tree_node_for_add_item_1'),
    url(r'^account/admin/workflow/e/(?P<uuidtreenode>[^/]+)/$', views.get_tree_node_for_add_item_2, name='get_tree_node_for_add_item_2'),
    url(r'^account/admin/workflow/e/wf/(?P<uuidtreenode>[^/]+)/$', views.get_edit_tree_workflow_items, name='get_edit_tree_workflow_items'),
    url(r'^account/admin/workflow/e/i/(?P<uuiditemnode>[^/]+)/$', views.edit_wf_item_as_child, name='edit_wf_item_as_child'),
    url(r'^account/admin/workflow/e/d/(?P<uuiditemnode>[^/]+)/$', views.delete_wf_item_as_child, name='delete_wf_item_as_child'),
    url(r'^account/admin/workflow/e/a/(?P<uuidtreenode>[^/]+)/$', views.create_new_wf_item_as_child, name='create_new_wf_item_as_child'),
    # url(r'^account/admin/workflow/e/i/(?P<uuidwfparent>[^/]+)/$', views.wf_set_add_items, name='wf_set_add_items'),
    url(r'^create/account/$', views.create_account, name='create_account'),
    url(r'^create/organization/$', views.create_organization, name='create_organization'),
    url(r'^account/admin/create/org/do/$', views.do_add_organization, name='do_add_organization'),
    url(r'^create/location/$', views.create_account, name='create_location'),
    url(r'^create/epoch/$', views.create_account, name='create_epoch'),
    url(r'^create/epoch/do', views.do_add_account, name='do_add_epoch'),
    url(r'^user/(?P<username>\w+)/user-admin/assoc/org/do/$', views.do_assoc_organization, name='do_assoc_organization'),
    url(r'^assoc/org/usr/$', views.assoc_organization_user, name='assoc_organization_user'),
    url(r'^assoc/org/usr/do', views.do_assoc_organization_user, name='do_assoc_organization_user'),
    url(r'^$', views.app, name='app'),
    url(r'^login', views.do_login, name='login'),
    url(r'^logout', views.do_logout, name='logout'),
    #TODO: REMOVE NEXT LINE BEFORE PRODUCTION
]

