from rest_framework import serializers
from .models import *
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
# from disposable_email_checker.validators import validate_disposable_email
from .validators import validate_disposable_email
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username','email','mobile','ip_address')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'mobile': {'required': True},
            'ip_address': {'required': True},
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(validators=[validate_disposable_email])
    location = serializers.CharField(required=True, write_only=True)
    class Meta:
        model = CustomUser
        fields = ('username','email','password','mobile','ip_address',"password2","location")
        extra_kwargs = {
            'email': {'required': True},
            'mobile': {'required': True},
            'ip_address': {'required': True},
        }

        


    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        location = validated_data.pop('location', None)

        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            ip_address=validated_data['ip_address']
        )

        user.set_password(validated_data['password'])
        user.save()

        user_details, created = UserDetails.objects.get_or_create(user=user)
        user_details.location = location
        user_details.save()

        print(user)
        return user
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user_details = UserDetails.objects.get(user=instance)
        ret['location'] = user_details.location
        return ret


    

    

    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required = True,write_only = True)






class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = '__all__'


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)


class ClientDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        fields = [
            'id',
            'client_name',
            'mobile',
            'category_name',
            'field_name',
            'stream_name',
            'product_name',
            'location',
            'cost',
            'review_link',
            'total_reviews',
            'updated_at',
            'description',
            'review_limit',
            'created_at',
            'review_count'
        ]
        read_only_fields = ['updated_at','review_count','created_at']

    def validate_mobile(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Mobile number should contain only digits.")
        return value

    def validate_cost(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Cost cannot be negative.")
        return value
    


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    


    
class InitiatePasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    mobile = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        mobile = data.get('mobile')
        
        try:
            user = CustomUser.objects.get(email=email)
            if not hasattr(user, 'mobile') or user.mobile != mobile:
                raise serializers.ValidationError("Email and mobile number do not match.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        
        return data

class VerifyOTPAndChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    

### ++++++++++++++++++++++++++++++++++  Payment app ++++++++++++++++++++++++++++++++++++++++++++####

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'order_id', 'amount', 'status', 'upi_id', 'customer_user_id']
        read_only_fields = ['transaction_id', 'status']

class Payment_InitiationSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    upi_id = serializers.CharField(required=False, allow_blank=True)
    customer_user_id = serializers.CharField(required=False, allow_blank=True)

class Payment_CallbackSerializer(serializers.Serializer):
    transactionId = serializers.CharField()
    status = serializers.CharField()