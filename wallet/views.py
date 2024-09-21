from django.contrib import messages
from django.shortcuts import render

from wallet.forms import BVNForm
from wallet.models import Wallet

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