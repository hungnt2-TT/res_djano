from django import forms

from .models import Category, FoodItem


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
