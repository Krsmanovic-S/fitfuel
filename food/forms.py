from django import forms


class CheckoutForm(forms.Form):    
    email = forms.EmailField(label='Email address')
    phone = forms.CharField(label='Phone')
    address = forms.CharField(label='Address')
    city = forms.CharField(label='City')
    zip_code = forms.CharField(label='Zip Code')