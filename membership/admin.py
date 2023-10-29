from django.contrib import admin
from .models import TrainingObjective, MembershipType

@admin.register(TrainingObjective)
class TrainingObjectiveAdmin(admin.ModelAdmin):
    list_display = ('active', 'id', 'codigo', 'descricao', 'create_user')
    exclude = ('create_user','update_user')

    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'create_user'):
            obj.create_user = request.user.username
        obj.update_user = request.user.username
        obj.save()

@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('active', 'id', 'codigo', 'descricao', 'create_user')
    exclude = ('create_user','update_user')

    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'create_user'):
            obj.create_user = request.user
        obj.update_user = request.user.username
        obj.save()