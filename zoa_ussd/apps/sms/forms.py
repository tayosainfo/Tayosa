from django import forms

class SMSReceivedForm(forms.Form):
    message_id = forms.CharField(max_length=100)
    link_id = forms.CharField(max_length=100)
    
    message_from = forms.CharField(max_length=100)
    message_to = forms.CharField(max_length=100)

    text = forms.CharField(max_length=480)
    date = forms.CharField(max_length=100)