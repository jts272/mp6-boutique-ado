from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checkout"

    def ready(self):
        """Override the `ready()` method to import the signals module,
        to call `update_total` model method every time a a line item is
        saved or deleted.
        """
        import checkout.signals
