import string

from django import forms


def validate_alphanumeric_underscore(value):
    for char in value:
        if(char in string.ascii_letters or char in string.digits
        or char == "_"):
            pass
        else:
            break
    else:
        return
    
    raise forms.ValidationError(u"%s must contain only alphanumeric or underscore characters" % value)


class AccountRegistrationForm(forms.Form):
    name_help = "Must be between 5-16 alphanumeric, underscore and dash characters."
    password_help = "Must be between 6-32 characters."
    
    account_name = forms.SlugField(min_length=5, max_length=16, help_text=name_help)
    account_password = forms.CharField(min_length=6, max_length=32,
                                       help_text=password_help,
                                       widget=forms.widgets.PasswordInput)
