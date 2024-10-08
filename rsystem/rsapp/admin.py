# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django import forms

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'mobile', 'ip_address', 'last_login', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('mobile', 'ip_address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('mobile', 'ip_address')}),
    )
    search_fields = ('username', 'email', 'mobile')
    ordering = ('username',)
    list_filter = ('is_staff', 'is_active')

class NormalUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'mobile', 'ip_address', 'last_login')
    search_fields = ('username', 'email', 'mobile')
    ordering = ('username',)

class ClientDetailsForm(forms.ModelForm):
    category_name = forms.ModelChoiceField(
        queryset=ReviewPrice.objects.all(), 
        to_field_name='reviewer_type',  
        required=True,
        label="Category Name"
    )

    class Meta:
        model = ClientDetails
        fields = '__all__'


class ReviewPriceAdmin(admin.ModelAdmin):
    list_display = ('reviewer_type', 'price')  # Display these fields in the list view
    search_fields = ('reviewer_type',)  # Enable search by reviewer_type

class ClientDetailsAdmin(admin.ModelAdmin):
    form = ClientDetailsForm
    list_display = ('id','client_name', 'category_name','field_name','stream_name','product_name', 'mobile', 'location', 'cost','updated_at' , 'total_reviews')  # Customize as needed
    search_fields = ('client_name', 'category_name', 'mobile')  # Enable search on these fields
    list_filter = ('category_name',)

    

    def get_readonly_fields(self, request, obj=None):
        return ['updated_at']  

class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'client_detail_id', 'review_type','review_date','location','review','link','verify_status','updated_at','created_at')

# Register the admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ReviewPrice, ReviewPriceAdmin)
admin.site.register(ClientDetails, ClientDetailsAdmin)
admin.site.register(UserHistory, UserHistoryAdmin)

# Optional: You can create a custom admin view for normal users,
# but typically normal users won't have access to the admin site.

