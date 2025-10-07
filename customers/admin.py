from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 
                   'is_deleted', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_deleted', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
        ('Audit fields', {'fields': ('is_deleted', 'deleted_at', 'created_by', 'updated_by', 'deleted_by')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'deleted_at')
    
    def get_queryset(self, request):
        # Show all customers including soft deleted ones in admin
        return Customer.objects.all()

    actions = ['soft_delete_customers', 'restore_customers']

    def soft_delete_customers(self, request, queryset):
        count = 0
        for customer in queryset:
            if not customer.is_deleted:
                customer.soft_delete(deleted_by=request.user)
                count += 1
        self.message_user(request, f'{count} customers were soft deleted.')
    soft_delete_customers.short_description = "Soft delete selected customers"

    def restore_customers(self, request, queryset):
        count = 0
        for customer in queryset:
            if customer.is_deleted:
                customer.restore()
                count += 1
        self.message_user(request, f'{count} customers were restored.')
    restore_customers.short_description = "Restore selected customers"
