from django.contrib import messages
from django.shortcuts import render

from wallet.forms import BVNForm
from wallet.models import Wallet


# Create your views here.
def create_wallet(request):
    form = BVNForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            print('form.cleaned_data', form.cleaned_data)
            cd = form.cleaned_data
            user = request.user
            bvn = cd["bvn"]
            Wallet.objects.create(user=user)
            user.verify = True
            user.save()
            messages.success(request, "Account verified, wallet successfully created")
            return render(request, 'wallet/create_wallet.html', {'form': form})
            # new_wallet = Wallet.objects.create(user=user,
            #                                    bvn=bvn)
        else:
            messages.error(request, "Error creating wallet")
            return render(request, 'wallet/create_wallet.html', {'form': form})
    return render(request, 'wallet/create_wallet.html', {'form': form})