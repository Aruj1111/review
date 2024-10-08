from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator

from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','mobile']

    def __str__(self):
        return self.username



# Create your models here.
class ReviewerTypes(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    MODERATOR = 'Client', 'Client'
    USER = 'User', 'User'

class UserDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_details') 
    otp = models.CharField(max_length=6, null=True, blank=True) 
    reviewer_type = models.CharField(max_length=10, choices=ReviewerTypes.choices, default=ReviewerTypes.USER)
    reviews_acc  = models.CharField(max_length=255 , null=False, blank=False)
    location = models.CharField(max_length=150 , null=False , blank=False)
    is_varified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ReviewPrice(models.Model):
    reviewer_type = models.CharField(max_length=100) 
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    def __str__(self):
        return f"{self.reviewer_type} - {self.price}"


class ClientDetails(models.Model):
    # client_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_category')
    client_name = models.CharField(max_length=255 , null=False,blank=False)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    category_name = models.CharField(max_length=100 , null=True , blank=True)
    field_name = models.CharField(max_length=100,null=False,blank=False)
    stream_name = models.CharField(max_length=100,null=False,blank=False)
    product_name = models.CharField(max_length=100,null=False,blank=False)
    location = models.CharField(max_length=150 , null=False,blank=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    review_link = models.CharField(max_length=2000)
    total_reviews = models.CharField(max_length=100)
    image_path = models.CharField(max_length=255)

    review_limit =  models.CharField(max_length=100, default='3', null=False, blank=False)
    review_count = models.CharField(max_length=100,default='0',null=False, blank=False)

    description = models.CharField(max_length=1000 , default='Cozy and inviting, our café offers the perfect atmosphere to relax, unwind, and enjoy delicious coffee and fresh pastries. Whether you are looking for a quiet corner to work, meet with friends, or simply savor a moment alone, we provide a warm and friendly environment. Our menu features a variety of specialty coffees, teas, and a selection of homemade treats made with the finest ingredients. Stop by for a cup of your favorite brew and experience the welcoming charm of our café.', null=False,blank=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name
    

    # def save(self, *args, **kwargs):
    #     try:
    #         review_price = ReviewPrice.objects.get(reviewer_type=self.category_name)
    #         self.cost = review_price.price
    #         print(self.cost)
    #     except ReviewPrice.DoesNotExist:
    #         self.cost = None
    #     super(ClientDetails, self).save(*args, **kwargs)
    

    

    

class UserHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_history')
    review_type = models.CharField(max_length=100,null=False,blank=False)
    review_date = models.DateTimeField(default=timezone.now)
    # client_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_user_history')
    client_detail = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='user_histories')
    location = models.CharField(max_length=150 , null=False,blank=False)
    ip_address = models.CharField(max_length=255 , null=False,blank=False)
    review = models.CharField(max_length=255, default='None', null=False, blank=False)
    link = models.URLField(max_length=200, default='None', blank=True, null=True)
    verify_status = models.CharField(max_length=100, default='None', null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}/{self.client_detail.client_name}'



#####========================================  payment ================================================#####

import uuid
from django.core.exceptions import ValidationError

def generate_unique_transaction_id():
    return str(uuid.uuid4())
from django.db import models

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100,unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    upi_id = models.CharField(max_length=50, blank=True)
    customer_user_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_unique_transaction_id()  # Implement this function
        super().save(*args, **kwargs)
        
    def clean(self):
            # Custom validation for order_id
            if Transaction.objects.filter(order_id=self.order_id).exists():
                raise ValidationError("This order_id already exists.")
