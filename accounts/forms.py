from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import translation
from core.validators import validate_image_upload
from .models import User, UserProfile, Address

class UserRegistrationForm(forms.ModelForm):
    # Honeypot bot trap: invisible to humans, bots fill it and get silently rejected.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=8
    )
    password_confirm = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'example@domain.com', 'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = translation.get_language() or 'fa'
        is_fa = str(lang).lower().startswith('fa')
        if is_fa:
            self.fields['first_name'].widget.attrs['placeholder'] = 'نام'
            self.fields['last_name'].widget.attrs['placeholder'] = 'نام خانوادگی'
            self.fields['email'].widget.attrs['placeholder'] = 'example@domain.com'
            self.fields['phone_number'].widget.attrs['placeholder'] = '۰۹۱۲۳۴۵۶۷۸۹'
            self.fields['password'].widget.attrs['placeholder'] = 'حداقل ۸ کاراکتر'
            self.fields['password_confirm'].widget.attrs['placeholder'] = 'تکرار رمز عبور'
            self.fields['password'].label = 'رمز عبور'
            self.fields['password_confirm'].label = 'تکرار رمز عبور'
        else:
            self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
            self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
            self.fields['email'].widget.attrs['placeholder'] = 'example@domain.com'
            self.fields['phone_number'].widget.attrs['placeholder'] = '09123456789'
            self.fields['password'].widget.attrs['placeholder'] = 'At least 8 characters'
            self.fields['password_confirm'].widget.attrs['placeholder'] = 'Confirm your password'
            self.fields['password'].label = 'Password'
            self.fields['password_confirm'].label = 'Confirm Password'

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            lang = translation.get_language() or 'fa'
            msg = "کاربری با این ایمیل قبلاً ثبت‌نام کرده است." if str(lang).lower().startswith('fa') else "A user with this email already exists."
            raise ValidationError(msg)
        return email

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise ValidationError("Validation error.")
        return ''

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            lang = translation.get_language() or 'fa'
            msg = "رمز عبور و تکرار آن مطابقت ندارند." if str(lang).lower().startswith('fa') else "Passwords do not match."
            raise ValidationError(msg)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailInput()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=True)


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label="نام", max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label="شماره تماس", max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = UserProfile
        fields = ['avatar', 'national_code', 'birth_date', 'notify_email', 'notify_sms']
        widgets = {
            'national_code': forms.TextInput(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        lang = translation.get_language() or 'fa'
        is_fa = str(lang).lower().startswith('fa')
        self.fields['first_name'].label = "نام" if is_fa else "First Name"
        self.fields['last_name'].label = "نام خانوادگی" if is_fa else "Last Name"
        self.fields['phone_number'].label = "شماره تماس" if is_fa else "Phone Number"
        self.fields['national_code'].widget.attrs['placeholder'] = '۱۰ رقم' if is_fa else '10 digits'
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone_number'].initial = user.phone_number

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            validate_image_upload(avatar)
        return avatar


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'receiver_name', 'receiver_phone', 'province', 'city', 'postal_code', 'address_line', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'receiver_name': forms.TextInput(attrs={'class': 'form-input'}),
            'receiver_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'province': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'address_line': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = translation.get_language() or 'fa'
        is_fa = str(lang).lower().startswith('fa')
        self.fields['title'].widget.attrs['placeholder'] = 'مثلاً: منزل یا محل کار' if is_fa else 'e.g. Home or Office'
        self.fields['receiver_name'].widget.attrs['placeholder'] = 'نام و نام خانوادگی تحویل گیرنده' if is_fa else 'Recipient full name'
        self.fields['receiver_phone'].widget.attrs['placeholder'] = '۰۹۱۲۳۴۵۶۷۸۹' if is_fa else '09123456789'
        self.fields['province'].widget.attrs['placeholder'] = 'استان (مثلاً تهران)' if is_fa else 'Province (e.g. Tehran)'
        self.fields['city'].widget.attrs['placeholder'] = 'شهر' if is_fa else 'City'
        self.fields['postal_code'].widget.attrs['placeholder'] = 'کد پستی ۱۰ رقمی' if is_fa else '10-digit postal code'
        self.fields['address_line'].widget.attrs['placeholder'] = 'خیابان، کوچه، پلاک، واحد' if is_fa else 'Street, alley, plaque, unit'
