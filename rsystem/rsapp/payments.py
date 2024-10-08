
from .serializers import Payment_InitiationSerializer, Payment_CallbackSerializer, TransactionSerializer
import re
from django.shortcuts import render
import json
import base64
import requests
import hashlib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError



def is_valid_upi_id(upi_id):
    # More specific UPI ID validation regex pattern
    upi_pattern = r'^[a-zA-Z0-9._-]{3,256}@[a-zA-Z]{2,64}$'
    
    if not re.match(upi_pattern, upi_id):
        return False
    
    # Additional checks
    parts = upi_id.split('@')
    if len(parts) != 2:
        return False
    
    username, handle = parts
    
    # Check if username starts or ends with a special character
    if username[0] in '._-' or username[-1] in '._-':
        return False
    
    # Check for consecutive special characters
    if '..' in username or '--' in username or '__' in username:
        return False
    
    # Check handle (should be a valid UPI handle)
    valid_handles = ['okaxis', 'okicici', 'okhdfcbank', 'oksbi', 'ybl', 'paytm', 'apl', 'axl', 'ibl', 'upi']
    if handle.lower() not in valid_handles:
        return False
    
    return True

def generate_checksum(data, salt_key, salt_index):
    """To Genarate checksum"""
    checksum_str = data + '/pg/v1/pay' + salt_key
    checksum = hashlib.sha256(checksum_str.encode()).hexdigest() + '###' + salt_index
    return checksum

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        # Get the order and amount from the request
        try:
            data = json.loads(request.body)
            serializer = Payment_InitiationSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                order_id = data['order_id']
                amount = data['amount']  # Amount in paise
                upi_id = data.get('upi_id', '')
                customer_user_id = data.get('customer_user_id', '')
                # Add this block to validate UPI ID
                if upi_id:
                    if not is_valid_upi_id(upi_id):
                        return JsonResponse({"error": "Invalid UPI ID"}, status=400)
                
                transaction = Transaction.objects.create(
                    order_id=order_id,
                    amount=amount,
                    status="PENDING",
                    upi_id=upi_id,
                    customer_user_id=customer_user_id
                )
                

                # Prepare the request to PhonePe
                payload = {
                    "merchantId": settings.PHONEPE_MERCHANT_ID,
                    "merchantTransactionId": transaction.transaction_id,
                    "merchantUserId": customer_user_id, 
                    "amount":float(amount * 100),  # convert to paise
                    "redirectUrl": "https://yourwebsite.com/payment/success",
                    "callbackUrl": "https://yourwebsite.com/payment/callback",
                    "paymentInstrument": {
                        "type": "UPI_INTENT",
                        "targetApp": "phonePe",
                    }
                }
                # If UPI ID is provided and valid, include it in the payload
                if upi_id:
                    payload["paymentInstrument"]["upi"] = {"vpa": upi_id}
                # Convert the payload to a string and hash it with sha256
                # payload_str = json.dumps(payload)
                # checksum = hashlib.sha256((payload_str + settings.PHONEPE_MERCHANT_KEY).encode('utf-8')).hexdigest()
                # Make the request to PhonePe
                data = base64.b64encode(json.dumps(payload).encode()).decode()
                checksum = generate_checksum(data, settings.PHONEPE_MERCHANT_KEY, settings.SALT_INDEX)
                print(data,'\n',checksum)
                final_payload = {
                    "request": data,
                }
                headers = {
                    "Content-Type": "application/json",
                    "X-VERIFY": checksum,
                }
                try:
                    response = requests.post(settings.PHONEPE_ENDPOINT, json=final_payload, headers=headers)
                    print('################################',response)
                    resp_data = response.json()
                    transaction.status = "SUCCESS" if resp_data.get('success') else "FAILED"
                    transaction.save()
                    return JsonResponse({"status": serializer.data, "data": resp_data})
                except requests.RequestException as e:
                    # This will catch any request-related errors (network issues, timeouts, etc.)
                    transaction.status = "FAILED"
                    transaction.save()
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':   
        # Handle callback data and update transaction
        data = json.loads(request.body)
        serializer = Payment_CallbackSerializer(data=data)
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transactionId']
            status = serializer.validated_data['status']

            try:
                transaction = Transaction.objects.get(transaction_id=transaction_id)
                transaction.status = status
                transaction.save()
                return JsonResponse({"status": serializer.data})
            except Transaction.DoesNotExist:
                 return JsonResponse({"status":serializer.data , "message": "Transaction not found"})

    
        else:
            return JsonResponse({"error": serializer.errors}, status=400)

    return JsonResponse({"error": "Invalid request method"})