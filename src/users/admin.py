from django.contrib import admin
from users.models import *

admin.site.register(User)
admin.site.register(UserProfile)

admin.site.register(EmployerRequest)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_user_phone_number', 'BIN', 'legal_address', 'actual_address',
        'phone_number', 'email', 'website', 'director_name',
        'bank_account', 'bank_name', 'BIK', 'KBE', 'OKED',
        'registration_date', 'verified'
    )
    search_fields = (
        'name', 'user_profile__user__phone_number', 'BIN', 'legal_address',
        'actual_address', 'phone_number', 'email', 'website',
        'director_name', 'bank_account', 'bank_name', 'BIK',
        'KBE', 'OKED'
    )
    list_filter = ('verified',)
    readonly_fields = ('posts_today', 'last_post_date')
    fieldsets = (
        (None, {
            'fields': ('user_profile', 'name', 'BIN', 'legal_address', 'actual_address',
                       'phone_number', 'email', 'website', 'director_name',
                       'bank_account', 'bank_name', 'BIK', 'KBE', 'OKED',
                       'registration_date', 'logo', 'documents', 'verified')
        }),
        ('Activity', {
            'fields': ('posts_today', 'last_post_date')
        }),
    )

    def get_user_phone_number(self, obj):
        """Возвращает номер телефона связанного пользователя из UserProfile."""
        return obj.user_profile.user.phone_number if obj.user_profile and obj.user_profile.user else 'Нет пользователя'
    get_user_phone_number.short_description = 'Номер телефона пользователя'
