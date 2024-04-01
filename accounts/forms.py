from django import forms
from .models import UserExtraFields




class UserExtraFieldsForm(forms.ModelForm):
    
    class Meta:
        model = UserExtraFields
        fields = ['openai_api_key', 'prowritingaid_api_key']
