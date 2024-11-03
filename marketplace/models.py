from django.db import models

from menu.models import Size


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey('employee.Profile', on_delete=models.CASCADE)
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('food_item', 'size')
    def __str__(self):
        return self.food_item.food_name

    def total_price(self):
        return self.food_item.price * self.quantity

    def total_quantity(self):
        return self.quantity

    def get_total_price(self):
        return self.quantity * self.size.price if self.size else self.food_item.price
