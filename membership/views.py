from attr import attr
from decimal import Decimal
from django import forms
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import Preferences 
from membership.utils import calc_membership_expiry_date
from .models import MemberMembership, Membership, Member
from .forms import MemberMembershipForm, MembershipForm, MemberForm, SearchForm
import datetime 
from datetime import date
from django.template.loader import render_to_string


def index(request):
    return render(request, 'membership/index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'membership/login.html',
                          {'message': 'Invalid username and password'})

    return render(request, 'membership/login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


#def register(request):
#    template = 'membership/register.html'
#    if request.method == 'POST':
#        username = request.POST['username']
#        first_name = request.POST['first_name']
#        last_name = request.POST['last_name']
#        email = request.POST['email']
#        personal_address = request.POST['personal_address']
#        date_of_birth = request.POST['date_of_birth']
#        phone_number = request.POST['phone_number']
#        gender = 'Other' #request.POST['gender']
#        password = request.POST['password']
#        confirmation = request.POST['confirmation']

#        if password != confirmation:
#            return render(request, template, {'message': 'Passwords do not match'})

#        try:
#            user = User(username=username, first_name=first_name, last_name=last_name, email=email, personal_address=personal_address,
#                        date_of_birth=date_of_birth, phone_number=phone_number)
#            user.set_password(password)
#            user.save()
#        except IntegrityError:
#            return render(request, template, {
#                'message': "Email already taken."
#            })
#        login(request, user)
#        return HttpResponseRedirect(reverse('index'))

#    return render(request, template, {'form': UserForm()})


def membership(request):
    plans = Membership.objects.all().order_by('type','price')
    template = 'membership/membership.html'
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            type = form.cleaned_data['type']
            duration = form.cleaned_data['duration']
            price = form.cleaned_data['price']

            membership = Membership(name = name, type = type, duration = duration, price = price)
            membership.save()
            
            messages.success(request, 'The membership plan was successfully added')

            return render(request, template, {
                'form': MembershipForm(),
                'plans':plans
            })

    return render(request, template, {
        'form': MembershipForm(),
        'plans':plans
    })


def renew_membership(request, id):
    template = 'membership/renew-membership.html'
    member = Member.objects.get(id = id)
    if request.method == "POST":
        form = MemberMembershipForm(request.POST, request=request)
        if form.is_valid():
            membership = form.cleaned_data['membership']
            discount = form.cleaned_data['discount']
            paid_amount = form.cleaned_data['paid_amount']

            member_membership = MemberMembership(
                membership = membership,
                member = member,
                purchase_date = date.today(),
                expiry_date = calc_membership_expiry_date(membership.duration, member.latest_membership().expiry_date),
                total_amount = membership.price,
                discount = discount,
                paid_amount = paid_amount,
                training_start = datetime.time(0, 0, 0),
                training_end = datetime.time(23, 59, 59),
                #admission fee só se cobra no cadastro do membro
                admission_fees = 0,
                status = 'U'
            )
            member_membership.save()
            
            messages.success(request, 'Membership was successfully renewed')

            send_email(messageType="RENEWAL", member=member)

            return HttpResponseRedirect(reverse('member-detail', args=(id,)))
            #return render(request, template, {
            #    'form': MemberMembershipForm(request.POST,request=request),
            #    'member_id': id
            #})            
        else:
            messages.error(request, form.errors)  
            return render(request, template, {
                'form': MemberMembershipForm(request.POST,request=request),
                'member_id': id,
            })
        
    
    return render(request, template, {
        'form': MemberMembershipForm(request=request, initial = {
            'membership': member.latest_membership().membership.pk,
            'discount': '0.00',
            'paid_amount': member.latest_membership().membership.price,
        }),
        'member_id': id,
        'member': member,
    })


def pay_membership(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid Request'})
    
    data = json.loads(request.body)
    id = data.get('id','')
    discount = data.get('discount','0')
    paid_amount = data.get('paid_amount','0')
    
    member_membership = MemberMembership.objects.get(pk = id)
    member_membership.discount = Decimal(discount)
    member_membership.paid_amount = member_membership.paid_amount + Decimal(paid_amount)
    if member_membership.due_amount() > 0:
        member_membership.status = 'I'
    else:
        member_membership.status = 'P'
    member_membership.save()

    messages.success(request, 'Membership was successfully paid.')

    send_email(messageType="PAYMENT", member=member_membership.member)

    return HttpResponseRedirect(reverse('member-detail', args=(id)))

@transaction.atomic
def add_member(request):

    template = 'membership/add-member.html'
    if request.method == "POST":
        form = MemberForm(request.POST,request=request)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            date_of_birth = form.cleaned_data['date_of_birth']
            gender = form.cleaned_data['gender']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            training_objectives = form.cleaned_data['training_objectives']
            membership = form.cleaned_data['membership']           

            member = Member(
                first_name = first_name, 
                last_name = last_name, 
                email = email,
                date_of_birth = date_of_birth, 
                gender = gender,
                phone_number = phone_number,                 
                address = address,
            )
            member.save()
            member.training_objectives.set(training_objectives)

            membermembership = MemberMembership(
                member = member,
                membership = membership,
                purchase_date = date.today(),
                expiry_date = calc_membership_expiry_date(membership.duration),
                total_amount = membership.price,
                discount = 0,
                paid_amount = 0,
                admission_fees = 0,
                training_start = datetime.time(0, 0, 0) ,
                training_end = datetime.time(23, 59, 59),
                #TODO rever este status
                status = 'U'
            )
            membermembership.save()
            
            messages.success(request, 'Member was successfully added')

            send_email(messageType="WELCOME", member=member)

            return HttpResponseRedirect(reverse('all-members'))
    return render(request, template, {
        'form': MemberForm(request=request)
    })

@login_required(login_url='/login',redirect_field_name=None)
def all_members(request):
    members = Member.objects.filter(active = True).order_by('first_name').all()
    paginator = Paginator(members, 50)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return render(request, 'membership/all-members.html', {
        'page_obj': page_obj,
        'form': SearchForm()
    })


def member_search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['search']
        search_member = Member.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query),
            active = True
        ).order_by('first_name').all()

        return render(request, 'membership/member-search-results.html', {
            'search_results': search_member
        })


def member_detail(request, id):
    template = "membership/member-detail.html"
    member = Member.objects.get(pk=id)
    return render(request, template, {
        'member': member
    })


@login_required
def edit(request):
    if request.method != 'POST':
        JsonResponse({'error': 'Invalid request'})

    data = json.loads(request.body)
    id = data.get('id','')
    email = data.get('email', '')
    age = data.get('age', '')
    phone_number = data.get('phone', '')
    address = data.get('address', '')

    member = Member.objects.get(pk=id)
    member.email = email
    member.age = age
    member.phone_number = phone_number
    member.address = address
    member.save()
    messages.success(request, 'Member detail was successfully edited. Please reload the page to view the change.')

    return HttpResponseRedirect(reverse('member-detail', args=(id,)))


@login_required
def remove(request,id):
    if request.method == "POST":
        member = Member.objects.get(pk=id)
        member.active = False
        member.save()
        messages.success(request, 'Member was successfully deleted')
        return HttpResponseRedirect(reverse('all-members'))
    else:
        return render(request, "membership/remove-member.html",{
            "member":Member.objects.get(pk=id)

        })
        

@login_required
def renew(request):
    if request.method != 'POST':
        JsonResponse({'error':'Invalid Request.'})
        
    data = json.loads(request.body)
    id  = data.get('id','')
    date = data.get('date','')
    
    member  = Member.objects.get(pk=id)
    member.validity = date
    member.save()
    

    messages.success(request, 'Membership validity was successfully renewed.')
    return HttpResponseRedirect(reverse('member-detail', args=(id)))



def edit_price(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid Request'})
    
    data = json.loads(request.body)
    id = data.get('id','')
    new_price = data.get('new_price','')
    
    membership = Membership.objects.get(pk = id)
    membership.membership_price = new_price
    membership.save()
    
    
    
@login_required
def remove_plan(request,id):
    if request.method == "POST":
        membership = Membership.objects.get(pk=id)
        membership.delete()
        messages.success(request, 'Membership plan was successfully deleted')
        return HttpResponseRedirect(reverse('membership'))
    
def send_email(messageType, member):
    try:
        preferences = Preferences.objects.filter(messageType=messageType).first()
        subject = preferences.subject
        message = preferences.message.format(member_first_name=member.first_name)
    except Preferences.DoesNotExist:
        subject = f'{messageType}'
        message = 'null'

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER, 
        [member.email],
        fail_silently=False
    )