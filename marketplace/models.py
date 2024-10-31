from django.db import models

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey('employee.Profile', on_delete=models.CASCADE)
    food_item = models.ForeignKey('menu.FoodItem', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_item.food_name

    def total_price(self):
        return self.food_item.price * self.quantity

    def total_quantity(self):
        return self.quantity
