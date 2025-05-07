from datetime import date
from django import forms
from django.forms import  DateInput, NumberInput, TextInput, EmailInput, ModelForm
from requests import request
from django.db.models import Q

from .models import MemberMembership, Membership, Member, MembershipType, TrainingObjective


#class UserForm(ModelForm):
#    class Meta:
#        model = User
#        fields = ['username','first_name', 'last_name','email','personal_address','date_of_birth','phone_number', 'password']
#        style = 'max-width: 300px;'
#        widgets = {
#            'username': TextInput(attrs={
#                 'class':'form-control',
#                'style': style,
#                'placeholder': 'Username'
#            }),
#            'first_name': TextInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'First Name',
#            }),            
#            'last_name': TextInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'Last Name',
#            }),            
#            'email': EmailInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'Email',
#            }),            
#            'personal_address': TextInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'Personal Address',
#            }),            
#            'date_of_birth': forms.DateInput(attrs={
#                'type': 'date', 
#                'class':'form-control', 
#                'style': style, 
#                'placeholder': 'Date of Birth'
#            }),                 
#            'phone_number': TextInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'Phone Number',
#            }),            
#            'gender': forms.Select(choices=(
#                    ("Male","M"),("Female","F"),("Other","O")
#                ),
#                attrs={
#                    'class':'form-control','style': style
#            }),            
#            'password': forms.PasswordInput(attrs={
#                'class':'form-control',
#                'style': style,
#                'placeholder': 'Password',
#            })            
#        }
   
    
class MembershipForm(ModelForm):
    type = forms.ModelChoiceField(queryset=MembershipType.objects.filter(active=True), widget=forms.Select)
    type.widget.attrs.update({'class': 'form-control'})
    
    class Meta:
        model = Membership
        fields = ['name', 'type', 'duration', 'price']
        style = 'max-width: 300px;'
        widgets = {
            'name':TextInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Name',
            }),
            #'type':TextInput(attrs={
            #   'class':'form-control',
            #   'style': style,
            #   'placeholder': 'Type',
            #}),
            
            'duration':NumberInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Duration',
               'pattern':'[0-9]',
            }),
             
            'price':NumberInput(attrs={
               'class':'form-control',
               'style': style,
               'placeholder': 'Price',
            }),
        }
        
        
class MemberForm(ModelForm):
    membership = forms.ModelChoiceField(
        queryset=Membership.objects.filter(active=True), 
        widget=forms.Select
    )
    membership.widget.attrs.update({'class': 'form-control'})

    training_objectives = forms.ModelMultipleChoiceField(
        queryset = TrainingObjective.objects.filter(active=True).order_by('descricao'),
        widget=forms.CheckboxSelectMultiple,
        required=True 
    )
    
    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop("request")
        super(MemberForm,self).__init__(*args,**kwargs)
        
        # Se tiver uma instância (edição de membro existente)
        if 'instance' in kwargs:
            member = kwargs['instance']
            if hasattr(member, 'latest_membership') and member.latest_membership():
                self.fields['membership'].initial = member.latest_membership().membership
                # Forçar a atualização do queryset para incluir o plano atual
                self.fields['membership'].queryset = Membership.objects.filter(
                    Q(active=True) | Q(id=member.latest_membership().membership.id)
                )

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'address', 'membership','training_objectives']
  
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
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class':'form-control', 
                'style': style, 
                'placeholder': 'Date of Birth'
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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MemberMembershipForm, self).__init__(*args, **kwargs)
        self.fields['membership'].widget.attrs.update({'class': 'form-control'})

    membership = forms.ModelChoiceField(
        queryset=Membership.objects.all(), 
        widget=forms.Select(),
    )

    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'start_date'
        })
    )

    class Meta:
        model = MemberMembership
        fields = ['membership', 'discount', 'paid_amount', 'start_date']
        widgets = {
            'discount': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Discount',
                'min': '0.00',
                'step': '0.01',
            }),
            'paid_amount': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paid Amount',
                'min': '0.00',
                'step': '0.01',
            })
        }

class MemberMembershipEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MemberMembershipEditForm, self).__init__(*args, **kwargs)
        self.fields['membership'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = MemberMembership
        fields = ['membership', 'expiry_date', 'status']
        widgets = {
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'status': forms.Select(choices=(
                ('U', 'Unpaid'),
                ('I', 'Incomplete'),
                ('P', 'Paid')
            ), attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            })
        }

        
class SearchForm(forms.Form):
    search = forms.CharField(label='',max_length=100,widget=forms.TextInput(attrs={
        'class':'form-control pl-3',
        'placeholder': 'Search Member',
    }))
    
        