from django import forms

from .models import Category, Product


class ProductForm(forms.ModelForm):
    """Form used by the admin panel to add and edit products.
    A ModelForm builds its fields automatically from the Product model."""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'old_price', 'stock_quantity', 'description',
            'image', 'image_2', 'image_3', 'image_4',
            'processor', 'ram', 'storage', 'display', 'battery',
            'rating', 'review_count', 'is_featured',
        ]
        labels = {
            'name': 'Product Name',
            'old_price': 'Old Price (optional)',
            'stock_quantity': 'Stock Quantity',
            'ram': 'RAM',
            'image': 'Upload Image',
            'image_2': 'Extra Image 2',
            'image_3': 'Extra Image 3',
            'image_4': 'Extra Image 4',
            'is_featured': 'Show in Featured Products',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Select category'
        # add Bootstrap classes to every field
        for name, field in self.fields.items():
            if name == 'is_featured':
                field.widget.attrs['class'] = 'form-check-input'
            elif name == 'category':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Category name'})
        self.fields['image'].widget.attrs['class'] = 'form-control'


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
