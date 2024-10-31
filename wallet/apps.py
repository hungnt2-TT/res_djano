from django.apps import AppConfig


class WalletConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wallet"

    def ready(self):

        import wallet.hooks
        print('wallet.hooks', wallet.hooks)