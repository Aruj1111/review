"""
URL configuration for rsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rsapp.views import *
from rsapp.payments import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('A2G/register/', RegisterAndSendOTPView.as_view(), name='register'),
    path('A2G/get_comments/',GetComments.as_view(),name="get_comments"),
    path('A2G/admin/', admin.site.urls),
    path('A2G/auth/login/',LoginView.as_view(), name= 'auth_register'),
    path('A2G/check/',Check.as_view(),name="check"),
    path('A2G/get_clients_data/',GetClientsdata.as_view(),name="get_clients_data"),
    path('A2G/verify_otp/',VerifyOtp.as_view(),name="verify_otp"),
    path('A2G/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('A2G/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   

    path('A2G/get-history/', GetHistory.as_view(), name='get-history'),
    path('A2G/save-history-link/', SaveHistoryLink.as_view(), name='save-history-link'),
    path('A2G/delete-client/<int:client_id>/', DeleteClientView.as_view(), name='delete-client'),
    path('A2G/admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('A2G/add-clientdetails/', AddClientDetails.as_view(), name='add-clientdetails'),
    path('A2G/change-pass/', ChangePasswordView.as_view(), name='change-pass'),
   

    path('A2G/initiate-pass-change/', InitiatePasswordChangeView.as_view(), name='initiate-pass-change'),
    path('A2G/reset-pass/', VerifyOTPAndChangePasswordView.as_view(), name='reset-pass'),
    path('A2G/client-search/', ClientDetailsSearchAPIView.as_view(), name='client-search'),
    # path('api/upload-client-image/', ClientImageUploadView.as_view(), name='upload-client-image'),
    path('initiate/', initiate_payment, name='initiate_payment'),
    path('callback/', payment_callback, name='payment_callback'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)