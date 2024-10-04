from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import datetime
from django.utils import timezone
from django.db import transaction
from wallet.forms import BVNForm
from wallet.models import Wallet, Event
from datetime import datetime, timedelta

from django.db import transaction


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
    context = {
        'wallet': wallet,
        'checkin_status': checkin_status
    }
    return render(request, 'wallet/wallet_setting.html', context)
