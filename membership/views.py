import re
from tkinter import Widget
from attr import attr
from django import forms
from django.db import IntegrityError
from django.forms import EmailInput, ModelForm, TextInput
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .models import MemberMembership, User, Membership, Members
from .forms import MemberMembershipForm, MembershipForm, UserForm, MemberForm, SearchForm


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


def register(request):
    template = 'membership/register.html'
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        personal_address = request.POST['personal_address']
        date_of_birth = request.POST['date_of_birth']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        #gym_name = request.POST['gym_name']
        #gym_location = request.POST['gym_location']
        #gym_phone = request.POST['gym_phone']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        if password != confirmation:
            return render(request, template, {'message': 'Passwords do not match'})

        try:
            user = User(username=username, first_name=first_name, last_name=last_name, email=email, personal_address=personal_address,
                        date_of_birth=date_of_birth, phone_number=phone_number, gender=gender)
            user.set_password(password)
            user.save()
        except IntegrityError:
            return render(request, template, {
                'message': "Email already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))

    return render(request, template, {'form': UserForm()})


def membership(request):
    plans = Membership.objects.all().order_by('membership_type','membership_price')
    template = 'membership/membership.html'
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            mem_type = form.cleaned_data['membership_type']
            mem_duration = form.cleaned_data['membership_duration']
            mem_price = form.cleaned_data['membership_price']

            membership = Membership(user=request.user, membership_type=mem_type,
                                    membership_duration=mem_duration, membership_price=mem_price)
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
    if request.method == "POST":
        form = MemberMembershipForm(request.POST, request=request)
        if form.is_valid():
            membership = form.cleaned_data['membership']
            member = form.cleaned_data['member']
            purchase_date = form.cleaned_data['purchase_date']
            expiry_date = form.cleaned_data['expiry_date']
            total_amount = form.cleaned_data['total_amount']
            discount = form.cleaned_data['discount']
            paid_amount = form.cleaned_data['paid_amount']
            admission_fees = form.cleaned_data['admission_fees']
            status = form.cleaned_data['status']

            member_membership = MemberMembership(
                membership = membership,
                member = member,
                purchase_date = purchase_date,
                expiry_date = expiry_date,
                total_amount = total_amount,
                discount = discount,
                paid_amount = paid_amount,
                admission_fees = admission_fees,
                status = status
            )
            member_membership.save()
            
            messages.success(request, 'Membership was successfully renewed')

            return render(request, template, {
                'form': MemberMembershipForm(request.POST,request=request)
            })
        else:
            print(form.errors)
        
    return render(request, template, {
        'form': MemberMembershipForm(request=request),
        'member_id': id
    })


def add_members(request):
    template = 'membership/add-members.html'
    if request.method == "POST":
        form = MemberForm(request.POST,request=request)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            age = form.cleaned_data['age']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            #membership = form.cleaned_data['membership']
            #validity = form.cleaned_data['validity']

            member = Members(first_name=first_name, last_name=last_name, email=email,
                             phone_number=phone_number, age=age, gender=gender, address=address)
            member.save()
            
            messages.success(request, 'Member was successfully added')

            return render(request, template, {
                'form': MemberForm(request.POST,request=request)
            })

    return render(request, template, {
        'form': MemberForm(request=request)
    })

@login_required(login_url='/login',redirect_field_name=None)
def all_members(request):
    members = Members.objects.all()
    paginator = Paginator(members, 5)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return render(request, 'membership/all-members.html', {
        'page_obj': page_obj,
        'form': SearchForm()
    })


@login_required(login_url='/login',redirect_field_name=None)
def all_memberships(request):
    members = MemberMembership.objects.all()
    paginator = Paginator(members, 5)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return render(request, 'membership/all-memberships.html', {
        'page_obj': page_obj,
        'form': SearchForm()
    })


def member_search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['search']
        search_member = Members.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).order_by('first_name').all()

        return render(request, 'membership/member-search-results.html', {
            'search_results': search_member
        })


def member_detail(request, id):
    template = "membership/member-detail.html"
    member = Members.objects.get(pk=id)
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

    member = Members.objects.get(pk=id)
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
        member = Members.objects.get(pk=id)
        member.delete()
        messages.success(request, 'Member was successfully deleted')
        return HttpResponseRedirect(reverse('all-members'))
    else:
        return render(request, "membership/remove-member.html",{
            "member":Members.objects.get(pk=id)

        })
        

@login_required
def renew(request):
    if request.method != 'POST':
        JsonResponse({'error':'Invalid Request.'})
        
    data = json.loads(request.body)
    id  = data.get('id','')
    date = data.get('date','')
    
    member  = Members.objects.get(pk=id)
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