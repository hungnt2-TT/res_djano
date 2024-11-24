import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# from django.utils.http import urlquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
import datetime
from django.utils import timezone
from django.db import transaction
from paypal.pro.forms import PaymentForm

from orders.models import Order
from wallet.forms import BVNForm, VnpayPaymentForm
from wallet.models import Wallet, Event, Transaction, SubTransaction
from datetime import datetime, timedelta

from django.db import transaction

from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

from wallet.vnpay import vnpay




def payment_service_paypal(request):
    host = request.get_host()
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "20.00",
        "item_name": "Order FoodItems",
        "no_shipping": "2",
        "invoice": str(uuid.uuid4()),
        "currency_code": "USD",
        "notify_url": "https://{}{}".format(host, reverse('paypal-ipn')),
        "return_url": "https://{}{}".format(host, reverse('payment_success')),
        "cancel_return": "https://{}{}".format(host, reverse('payment_failed')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}

    return render(request, "payment/payment.html", context)


# Create your views here.
# def create_wallet(request):
#     form = BVNForm(request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             print('form.cleaned_data', form.cleaned_data)
#             cd = form.cleaned_data
#             user = request.user
#             bvn = cd["bvn"]
#             Wallet.objects.create(user=user)
#             user.verify = True
#             user.save()
#             messages.success(request, "Account verified, wallet successfully created")
#             return render(request, 'wallet/create_wallet.html', {'form': form})
#             # new_wallet = Wallet.objects.create(user=user,
#             #                                    bvn=bvn)
#         else:
#             messages.error(request, "Error creating wallet")
#             return render(request, 'wallet/create_wallet.html', {'form': form})
#     return render(request, 'wallet/create_wallet.html', {'form': form})

# class WalletBalance:
#     def __init__(self, user, value):
#         self.user = user
#         self.value = value


class WalletBalance:
    def __init__(self, user, value):
        self.user = user
        self.value = value

    def despositing(self, value):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=self.user)
            wallet.withdraw(value)
            wallet.save()
            return wallet.balance

    def withdrawing(self, value):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=self.user)
            wallet.deposit(value)
            wallet.save()
            return wallet.balance

    @staticmethod
    def transfer(wallet_id, transfer_to_wallet_id, value):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
            transfer_to_wallet = Wallet.objects.select_for_update().get(pk=transfer_to_wallet_id)
            wallet.transfer(transfer_to_wallet, value)
            wallet.save()
            return wallet.balance

    def history(self):
        return self.user.transaction_set.all()

    def check_in(self, type):
        today = timezone.now().date()
        if not Event.objects.filter(user=self.user, event_type='check_in', event_date=today).exists():
            with transaction.atomic():
                wallet = Wallet.objects.get(user=self.user)
                wallet.deposit(100, type)
                wallet.save()
                Event.objects.create(user=self.user, event_type='check_in')
            return True
        return False


@login_required
@transaction.atomic
def daily_check_in(request):
    wallet_balance = WalletBalance(request.user, 0)
    event = Event.objects.filter(user=request.user, event_type='check_in', event_date=timezone.now().date()).first()
    print('event', event)
    if wallet_balance.check_in('Daily check in'):
        messages.success(request, "You have successfully checked in and earned 100 points!")
    else:
        messages.error(request, "You have already checked in today.")
    return redirect('setting_wallet')


def setting_wallet(request):
    wallet, created = Wallet.objects.get_or_create(user_id=request.user.id)
    print(wallet.user)
    transaction = wallet.transaction_set.all()
    print('transaction', transaction)
    today = datetime.now().date()
    recent_days = [today - timedelta(days=i) for i in range(5)]
    event = Event.objects.filter(user=request.user, event_type='check_in', event_date__in=recent_days)
    checkin_dates = [checkin.event_date for checkin in event]
    checkin_status = []

    for day in recent_days:
        checked_in = day in checkin_dates
        checkin_status.append({
            'date': day,
            'checked_in': checked_in
        })
    print(checkin_status)

    transactions = Transaction.objects.filter(wallet=wallet).order_by('-create_at')[:10]
    sub_transactions = SubTransaction.objects.filter(transaction_id__in=transactions).order_by('-create_at')

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'sub_transactions': sub_transactions,
        'checkin_status': checkin_status
    }
    return render(request, 'wallet/wallet_setting.html', context)


def index(request):
    return render(request, "payment/payment_index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    print('payment', order.total)
    print('payment', order)
    if request.method == 'POST':
        print('POST', request.POST)
        data = {
            'order_id': order_id,
            'order_type': request.POST['order_type'],
            'amount': order.total,
            'order_desc': request.POST['order_desc'],
            'bank_code': request.POST['bank_code'],
            'language': request.POST['language'],
        }
        form = VnpayPaymentForm(data)
        print('form', form)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            print('amount', amount)
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code
            order_number = order.order_number  # Get the order number
            vnp_return_url = settings.VNPAY_RETURN_URL.format(order_number=order_number)
            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = vnp_return_url
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        print('GET')
        vnpay_payment_data = {
            'order_id': order_id,
            'order_type': 'billpayment',
            'amount': order.total,
            'order_desc': 'Thanh toán hóa đơn',
            'language': 'vn'
        }
        form = VnpayPaymentForm(initial=vnpay_payment_data)
        return render(request, 'payment/payment_vnpay.html', {'form': form, 'order': order})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Thành công", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Lỗi", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


n = random.randint(10 ** 11, 10 ** 12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})


def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})
