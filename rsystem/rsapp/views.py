from django.shortcuts import render
from rest_framework.generics import DestroyAPIView
from rest_framework import generics
from rest_framework.permissions import AllowAny ,IsAuthenticated
from .models import CustomUser 
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.core.mail import EmailMultiAlternatives
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
import random , os
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from openai import OpenAI
from django.conf import settings
client = OpenAI(api_key='')
from rest_framework import status
from django.core.mail import send_mail
from django.db.models import Q



class RegisterAndSendOTPView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate and send OTP
        otp = random.randint(100000, 999999)
        print(otp)
        email = user.email
        username = user.username

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OTP Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #333;
                }}
                p {{
                    color: #555;
                }}
                .otp {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #888;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 15px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Our Service</h1>
                <p>Hi {username},</p>
                <p>Thank you for registering with us. To complete your registration, please verify your email address using the OTP below:</p>
                <div class="otp">{otp}</div>
                <p>If you did not request this, please ignore this email.</p>
                <p>For further assistance, feel free to contact our support team.</p>
                <a href="https://example.com/verify" class="button">Verify Email</a>
                <div class="footer">
                    <p>Thank you for choosing us!</p>
                    <p>Best regards,</p>
                    <p>The Support Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = 'Verify your email address'

        email_message = EmailMultiAlternatives(subject, '', 'ankit.chaudhary.ahit@gmail.com', [email])
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)


        # Create or update UserDetails
        user_details, created = UserDetails.objects.get_or_create(user=user)
        user_details.otp = otp
        user_details.reviews_acc = "['hospital','doctor','cafe','hotels','education']"
        user_details.save()

        headers = self.get_success_headers(serializer.data)
        return Response({
            "msg": "Registration successful. OTP sent to your email.",
            "status": 201,
            "data": serializer.data
        }, status=201, headers=headers)





class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request,*args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            user_details = UserDetails.objects.filter(user = user).values()
            if not user_details[0].get('is_varified') :
                return Response({'msg':'Please verify your email', "status":401}, status=401)
            print(user,email,password)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                return Response({
                    "refresh":str(refresh),
                    "access":str(refresh.access_token),
                    "user":user_serializer.data
                })
            else:
                return Response({'msg':'Invalid Credentials', "status":401},status=401)
        except:
            return Response({'msg':'Please send Valid fields.', "status":401},status=401)



## --------------------------- Password Change --------------------------------------

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                return Response({"msg": "Password updated successfully", "status":200}, status= 200)
            return Response({"msg": "Incorrect old password", "status":400}, status=400)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class InitiatePasswordChangeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InitiatePasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            username = user.username
            # Generate OTP
            otp = str(random.randint(100000, 999999))

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: auto;
                        background: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333;
                    }}
                    p {{
                        color: #555;
                    }}
                    .otp {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #4CAF50;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 12px;
                        color: #888;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 15px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset Request</h1>
                    <p>Hi {username},</p>
                    <p>We received a request to reset your account password. Use the OTP below to reset your password:</p>
                    <div class="otp">{otp}</div>
                    <p>If you did not request this, please ignore this email. Your password will remain unchanged.</p>
                    <p>If you continue to experience issues or did not request this, contact our support team.</p>
                    <a href="https://example.com/reset-password" class="button">Reset Password</a>
                    <div class="footer">
                        <p>Thank you for trusting us to secure your account!</p>
                        <p>Best regards,</p>
                        <p>The Support Team</p>
                    </div>
                </div>
            </body>
            </html>
            """


            subject = 'Verify your email address'

            email_message = EmailMultiAlternatives(subject, '', 'ankit.chaudhary.ahit@gmail.com', [email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)


            # Create or update UserDetails
            user_details, created = UserDetails.objects.get_or_create(user=user)
            user_details.otp = otp
            user_details.reviews_acc = "['hospital','doctor','cafe','hotels','education']"
            user_details.save()
            
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAndChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPAndChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = CustomUser.objects.get(email=email)
                user_details = UserDetails.objects.get(user=user)
                if user_details.otp != otp:
                    return Response({"msg": "Invalid OTP","status":400}, status=400)
                
                # Change password
                user.set_password(new_password)
                user.password_reset_otp = None  # Clear the OTP
                user.save()
                
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



## -------------------------------------Password Change End -------------------------------------------------------------


class Check(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({
            "msg":"You access your data successfully!",
            "status":200,
            "data":{
                    "user_data":user_serializer.data
                    }
            
        },status=200)





class AddClientDetails(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_superuser:
            data = request.data.copy()  # Create a mutable copy of the data
            image_file = request.FILES.get('image')

            if image_file:
                # Create client directory if it doesn't exist
                client_name = data.get('client_name')
                data['location'] = data.get('location').lower() if data.get('location') else None
                data['category'] = data.get('category').lower() if data.get('category') else None

                client_dir = os.path.join(settings.MEDIA_ROOT, client_name)
                os.makedirs(client_dir, exist_ok=True)

                # Save the image
                image_name = image_file.name
                image_path = os.path.join(client_dir, image_name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                # Create the full URL path
                relative_path = os.path.join(client_name, image_name).replace('\\', '/')
                full_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
                
                data['image_path'] = full_url
                print(data['image_path'])
            
            serializer = ClientDetailsSerializer(data=data)
            
            if serializer.is_valid():
                client_details = serializer.save()
                if 'image_path' in data:
                    client_details.image_path = data['image_path']
                    client_details.save()
                return Response({
                    "msg": 'Data added successfully!',
                    "status": 200,
                    "data": ClientDetailsSerializer(client_details).data
                }, status=200)
            else:
                return Response({
                    "msg": 'Something went wrong!',
                    "status": 400,
                    "data": serializer.errors
                }, status=400)
        else:
            return Response({
                "msg": 'You are not authorized to perform this action!',
                "status": 400
            }, status=400)
        

    
class VerifyOtp(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        username = request.data.get('username')
        try:
            user = CustomUser.objects.get(username=username)
        except:
            return Response({"msg": 'User not found.', "status":400}, status=400)
        print(user)
        otp = int(request.data.get('otp'))
        try:
            user_details = UserDetails.objects.get(user=user)
            print(user_details)
            data_otp = int(user_details.otp)
            if otp == data_otp:
                user_details, created = UserDetails.objects.get_or_create(user=user)
                user_details.is_varified = True
                user_details.save()
                return Response({"msg": 'Varification Successfull !', "status":200}, status=200)
            else:
                return Response({"msg": 'Invalid Otp.', "status":200}, status=200)

        except UserDetails.DoesNotExist:
            return Response({"msg": "User details not found.", "status":404}, status=404)
        

class  GetClientsdata(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):
        user = request.user
        if not user.is_superuser:
            try:
                user_data = UserDetails.objects.get(user=user)
                user_location = user_data.location
                client_data = ClientDetails.objects.filter(location=user_location)
            except UserDetails.DoesNotExist:
                return Response({"msg": 'User Not Found' , "status":400  }, status=400)
        else:
            client_data = ClientDetails.objects.all()
        
        for client in client_data:
            if hasattr(client, 'image_path'):
                print(f'Client {client.id} image path: {client.image_path}')
        data =  list(client_data.values())
       
        return Response({
            "msg": 'Details retrieved successfully!',
            "status": 200,
            "data": data
        }, status=200)


class GetComments(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # prompt = request.data.get("prompt")
        
        c_id = request.data.get('id')
        client_details = ClientDetails.objects.filter(id=c_id)
        serializers = ClientDetailsSerializer(client_details, many=True)
 
        ip = request.data.get('ip_address') 
        curr_client_user = serializers.data[0].get('client_name')
        curr_category_name = serializers.data[0].get('category_name')
        curr_field_name = serializers.data[0].get('field_name')
        curr_location = request.data.get('curr_location').lower()    
        user = request.user
        if user.is_superuser:
            return Response({"msg": 'Admin Can not genrate review' , "status":400  }, status=400)
        

        
        updated_at_str = serializers.data[0].get('updated_at')
        print(updated_at_str)
        updated_at = datetime.fromisoformat(updated_at_str)
        if updated_at.tzinfo is None:
           updated_at = timezone.make_aware(updated_at)

        t24_hours_later = updated_at + timedelta(hours=24)
        # dt1 = datetime.strptime(time1, fmt)
        if timezone.now() < t24_hours_later :
            curr_client_review = serializers.data[0].get('review_count')
            if curr_client_review>=serializers.data[0].get('review_limit'):
                return Response({"msg": "Today's Max Limit Reached.", "status":404}, status=404)
        else :
            client_details = ClientDetails.objects.get(id=c_id)
            client_details.updated_at = datetime.now()
            client_details.review_count = '0'
            client_details.save()
        if not UserHistory.objects.filter(user = user , ip_address = ip ,client_detail_id = c_id ).exists():                  #, client_user = curr_client_user
            return Response({"msg": "User review already done.", "status":404}, status=404)
        else : 
            category_data = ClientDetails.objects.get(client_name = curr_client_user , category_name = curr_category_name , field_name=curr_field_name , location =  curr_location  )
            print(category_data.category_name.split('-')[0])
            words = random.choice([5,10,15,20])
            emoji = random.choice([True , False])
            if emoji:
                print(emoji)
                emoji_type = random.choice(['and with emoji Happy', 'and with emoji Smiley', 'and with emoji Party', 'and with emoji Celibration', 'and with emoji enjoyed'])
            else :
                print(emoji)
                emoji_type = ''
            prompt = f"Genrate a review of {words} words {emoji_type} based having category {category_data.category_name.split('-')[0]} it's name  {category_data.field_name} it's type {category_data.stream_name} products it having {category_data.product_name} and location {category_data.location}"


    
        if prompt:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                answer = response.choices[0].message.content.strip()
                print(answer)
            except Exception as e:
                answer = f"Error: {str(e)}"
                return Response({"msg": answer, "status":404}, status=404)
        else:
            return Response({"msg": "No prompt provided.", "status":404}, status=404)
        ClientDetailsSerializer()
        user_details, created = UserHistory.objects.get_or_create(user=user , client_detail_id = c_id)
        client_details = ClientDetails.objects.get(id=c_id)
        client_details.review_count = str(int(client_details.review_count)+1)
        client_details.save()
       
        if not created:
            return Response({"msg":"Sorry Something went worng","status":400},status=400)
        else :
            user_details.ip_address = ip
            user_details.review_type = category_data.category_name
            user_details.location = curr_location
            user_details.review =answer
            user_details.verify_status = 'Review Genrated'
            user_details.save()

        return Response({"msg": "Successful!" , "answer": answer, "status":200}, status=404)



class GetHistory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if not user.is_superuser:
            
            user_history = UserHistory.objects.filter(user=user).values()
            print(user_history)
            return Response({"msg": 'Dtails got successfully!', "status":200, "data" : user_history }, status=200)
        else:
            user_history = UserHistory.objects.all().values()
            return Response({"msg": 'Dtails got successfully!', "status":200, "data" : user_history }, status=200)



class SaveHistoryLink(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        print(user)
        id = request.data.get('id')
        link = request.data.get('link')
        if link:
            print('Link')
        else:
            print('Link not provided')
        image = request.FILES.get('image')
        Verify_type = request.data.get('Verify_type')
        print("image assigned")
        print(image)
        if Verify_type.lower() == 'image':
                if image:
                    pass
                else:
                    return Response({"msg": 'Image not provided', "status":400  }, status=400)
                user_data = get_object_or_404(UserDetails, user=user)
                print(user_data.id)
                client_data = get_object_or_404(ClientDetails , id = id)
                print(client_data.client_name)
                
                client_dir = os.path.join(settings.MEDIA_ROOT, client_data.client_name)
                if os.path.exists(client_dir):
                    
                    user_dir = os.path.join(client_dir, str(user_data.id))
                else:
                   
                    user_dir = os.path.join(client_dir, str(user_data.id))
                
                os.makedirs(user_dir, exist_ok=True)

               
                image_name = image.name
                image_path = os.path.join(user_dir, image_name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

               
                relative_path = os.path.join(client_data.client_name, str(user_data.id), image_name).replace('\\', '/')
                full_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
                # return Response({"msg": full_url, "status":200}, status=200)
                c_id = request.data.get('id')
                try:
                    user_history = UserHistory.objects.get(user=user, client_detail_id=c_id)
                except:
                    return Response({"msg": 'User Not Found For This Image', "status":400  }, status=400)
                user_history.link = full_url
                user_history.verify_status = 'Verification Pending'
                user_history.save()
                return Response({"msg": 'Image saved successfully!', "status":200}, status=200)
        else:    
            # return Response({"msg": 'Link saved successfully!', "status":200}, status=200)
            c_id = request.data.get('id')
            if link:
                pass
            else:
                return Response({"msg": 'Link not provided', "status":400  }, status=400)
            try:
                user_history = UserHistory.objects.get(user=user, client_detail_id=c_id)
            except:
                return Response({"msg": 'User Not Found For This Link', "status":400  }, status=400)
            user_history.link = link
            user_history.verify_status = 'Verification Pending'
            user_history.save()
            return Response({"msg": 'Link saved successfully!', "status":200}, status=200)





class DeleteClientView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, client_id):
        client = get_object_or_404(ClientDetails, id=client_id)
        user = request.user 
        if user.is_staff or user.is_superuser:
            client.delete()
            return Response({"msg": "Client deleted successfully","status":204}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"msg": "You do not have permission to delete this client please contact admin for that.","status":403}, status=status.HTTP_403_FORBIDDEN)





# class SendEmailAPI(APIView):
#     permission_classes = (AllowAny,)
#     def post(self, request):
#         subject = request.data.get('subject', 'Test Email')
#         message = request.data.get('message', 'This is a test email from Django.')
#         to_email = request.data.get('to_email')

#         if not to_email:
#             return Response({"error": "Recipient email is required."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [to_email],
#                 fail_silently=False,
#             )
#             return Response({"msg": "Email sent successfully.","status":200}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        






class AdminLoginView(APIView):

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        data = CustomUser.objects.all()
        print(data.values())
        print(serializer)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            print("valid")
            try:
                user = CustomUser.objects.get(email  =email)
                print(user.is_superuser)
            except CustomUser.DoesNotExist:
                return Response({"msg": "No user found with this email.","status":404}, )
            
            if  user.check_password(password):
            # return Response({"error": "Incorrect password."}, status=status.HTTP_401_UNAUTHORIZED)
                print(user.is_superuser)
                if not user.is_superuser:
                    return Response({"msg": "User is not a superuser.","status":403}, status= 403)
                
                refresh = RefreshToken.for_user(user)
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                return Response({
                        "refresh":str(refresh),
                        "access":str(refresh.access_token),
                        "user":user_serializer.data
                    })
            else:
                return Response({'msg':'Invalid Credentials', "status":401},status=401)
           
        return Response(serializer.errors, status= 400)
    

class ClientDetailsSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get('query', '')

        if query:
 
            filter_query = Q(category_name__icontains=query) | \
                           Q(field_name__icontains=query) | \
                           Q(stream_name__icontains=query) | \
                           Q(product_name__icontains=query)| \
                           Q(location__icontains = query)
            
            
            clients_data = ClientDetails.objects.filter(filter_query)
        else:
            
            clients_data = ClientDetails.objects.all()

         
        if not clients_data.exists():
            return Response({
                "status": 404,
                "msg": "No matching clients found."
            }, status=status.HTTP_404_NOT_FOUND)

        
        serializer = ClientDetailsSerializer(clients_data, many=True)

        return Response({
            "status": 200,
            "msg": "Search completed successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    
