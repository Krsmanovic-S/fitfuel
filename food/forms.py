from django import forms


class CheckoutForm(forms.Form):
    email = forms.EmailField(label='Email address')
    phone = forms.CharField(label='Phone')
    address = forms.CharField(label='Address')
    zipcode = forms.CharField(label='Zip Code')