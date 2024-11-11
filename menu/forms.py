from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Category, FoodItem, Size


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['category_name'].widget.attrs['placeholder'] = 'Menu Category Title'
        self.fields['description'].widget.attrs['placeholder'] = 'Category Description'


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['size', 'price']

class FoodItemForm(forms.ModelForm):

    class Meta:
        model = FoodItem
        fields = ['food_name', 'category', 'description', 'price', 'image', 'is_available', 'food_title',
                  'sub_food_title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['food_name'].widget.attrs['placeholder'] = 'Food Name'
        self.fields['category'].widget.attrs['placeholder'] = 'Category'
        self.fields['price'].widget.attrs['placeholder'] = 'Price'
        self.fields['image'].widget.attrs['placeholder'] = 'Image'
        self.fields['image'].widget.attrs['id'] = 'imageUpload'
        self.fields['image'].widget.attrs['class'] = 'btn btn-info'
        self.fields['food_title'].widget.attrs['placeholder'] = 'Food Title'
        self.fields['sub_food_title'].widget.attrs['placeholder'] = 'Sub Food Title'
        self.fields['is_available'].widget.attrs['placeholder'] = 'Available'
        self.fields['description'].widget = CKEditor5Widget(config_name='extends')