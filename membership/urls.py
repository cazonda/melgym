from django.urls import path
from . import views

urlpatterns = [
    path("",views.all_members, name='index'),
    path("login",views.login_view, name='login'),
    path("logout",views.logout_view, name='logout'),
    #path("register",views.register, name='register'),
    path("membership",views.membership, name='membership'),
    path("renew-membership/<int:id>",views.renew_membership, name='renew-membership'),
    path("pay-membership",views.pay_membership, name='pay-membership'),
    path("add-member",views.add_member, name='add-member'),
    path("all-members",views.all_members, name='all-members'),
    path("member-search", views.member_search, name='member-search'),
    path("member/<int:id>", views.member_detail, name='member-detail'),
    path("member-attendance/<int:id>", views.member_attendance, name='member-attendance'),    
    path("edit-member/<int:id>", views.edit_member, name='edit-member'),
    path("punch-member", views.punch_member_in_or_out, name='punch-member'),
    path("remove/<int:id>",views.remove,name="remove"),
    path("renew",views.renew,name="renew"),
    path("edit-price", views.edit_price,name="edit-price"),
    path("remove-plan/<int:id>",views.remove_plan, name="remove-plan"),
    path("download-receipt/<int:membership_id>", views.download_receipt, name="download-receipt")
]