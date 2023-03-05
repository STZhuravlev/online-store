from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'phone', 'seller_status', )
    list_filter = ('email', 'is_staff', 'is_active', 'seller_status', )
    fieldsets = (
        (None, {'fields': ('email', 'password', 'phone',  'name', 'avatar', 'seller_status', )}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'seller_status', )}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)

    actions = ['move_to_active', 'move_to_inactive', 'move_to_pending']

    def move_to_active(self, request, queryset):
        queryset.update(seller_status='active')
        for user in queryset:
            user_email = user.email
            user = CustomUser.objects.get(email=user_email)
            user.seller_status = 'active'
            user.save()

    def move_to_inactive(self, request, queryset):
        queryset.update(seller_status='not_active')
        for user in queryset:
            user_email = user.email
            user = CustomUser.objects.get(email=user_email)
            user.seller_status = 'not_active'
            user.save()

    def move_to_pending(self, request, queryset):
        queryset.update(seller_status='pending')
        for user in queryset:
            user_email = user.email
            user = CustomUser.objects.get(email=user_email)
            user.seller_status = 'not_active'
            user.save()

    move_to_active.short_description = 'Перевести в активно'
    move_to_inactive.short_description = 'Перевести в неактивно'
    move_to_pending.short_description = 'Перевести в на рассмотрении'


admin.site.register(CustomUser, CustomUserAdmin)
