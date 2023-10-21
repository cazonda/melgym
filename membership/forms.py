from datetime import date
from django import forms
from django.forms import  DateInput, NumberInput, TextInput, EmailInput, ModelForm
from requests import request

from .models import MemberMembership, User, Membership,Members


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name','email','personal_address','date_of_birth','phone_number', 'password']
        style = 'max-width: 300px;'
        widgets = {
            'username': TextInput(attrs={
                 'class':'form-control',
                'style': style,
                'placeholder': 'Username'
            }),
            'first_name': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'First Name',
            }),
            
            'last_name': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Last Name',
            }),
            
            'email': EmailInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Email',
            }),
            
            'personal_address': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Personal Address',
            }),
            
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class':'form-control', 
                'style': style, 
                'placeholder': 'Date of Birth'}),
                 
                 
            'phone_number': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Phone Number',
            }),
            
            'gender': forms.Select(choices=(("Male","Male"),("Female","Female"),("Other","Other")),
                                   attrs={
                                       'class':'form-control','style': style}),
            
            'password': forms.PasswordInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Password',
            })
            
        }
    
    
class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['membership_type', 'membership_duration', 'membership_price']
        style = 'max-width: 300px;'
        widgets = {
            'membership_type':TextInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Type',
            }),
            
            'membership_duration':NumberInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Duration',
               'pattern':'[0-9]',
            }),
             
            'membership_price':NumberInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Price',
            }),
        }
        
        
class MemberForm(ModelForm):
    membership = forms.ModelChoiceField(queryset=Membership.objects.all(), widget=forms.Select)
    membership.widget.attrs.update({'class': 'form-control'})
    
    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop("request")
        super(MemberForm,self).__init__(*args,**kwargs)

    class Meta:
        model = Members
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'age', 'gender', 'address', 'membership']
  
        style = 'max-width: 300px;'
        widgets = {
            'first_name':TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'First Name',
            }),
            'last_name': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Last Name',
            }),
            
            'email': EmailInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Email',
            }),
            
            'phone_number': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Phone Number',
            }),
            'age': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Age',
            }),
            'gender': forms.Select(choices=(("Male","Male"),("Female","Female"),("Other","Other")),
                                attrs={
                                    'class':'form-control','style': style}),
                
            'address': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Address',
            })            
        }
        

class MemberMembershipForm(ModelForm):
    
    membership = forms.ModelChoiceField(queryset=Membership.objects.all(), widget=forms.Select)
    membership.widget.attrs.update({'class': 'form-control'})    
    
    purchase_date = forms.DateField(widget=forms.HiddenInput(), initial=date.today()) 
    admission_fees = forms.IntegerField(widget=forms.HiddenInput(), initial=0) 
    status = forms.CharField(widget=forms.HiddenInput(), initial='N')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MemberMembershipForm, self).__init__(*args,**kwargs)


    class Meta:
        model = MemberMembership
        fields = ['membership', 'member','purchase_date', 'expiry_date', 'total_amount', 'discount', 'paid_amount', 'admission_fees', 'status']

        style = 'max-width: 300px;'
        widgets = {
            'expiry_date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'type': 'date'
              }),
            'discount': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Discount',
            }),   
            'paid_amount': TextInput(attrs={
                'class':'form-control',
                'style': style,
                'placeholder': 'Paid Amount',
            })  
        }
        
class SearchForm(forms.Form):
    search = forms.CharField(label='',max_length=100,widget=forms.TextInput(attrs={
        'class':'form-control pl-3',
        'placeholder': 'Search Member',
    }))
    
        