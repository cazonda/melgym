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

from membership.utils import calc_membership_expiry_date
from .models import Attendance, MemberMembership, Membership, Member
from .forms import MemberMembershipForm, MembershipForm, MemberForm, SearchForm
import datetime 
from datetime import date
import time

from .notifications import send_payment_confirmation_email
from .services import process_membership_renewal

import logging


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
    member = Member.objects.get(id=id)
    if request.method == "POST":
        form = MemberMembershipForm(request.POST, request=request)
        if form.is_valid():
            try:
                process_membership_renewal(
                    member_id=id,
                    membership_id=form.cleaned_data['membership'].id,
                    paid_amount=form.cleaned_data['paid_amount'],
                    discount=form.cleaned_data['discount'],
                    auto_renew=form.cleaned_data.get('auto_renew', True)
                )
                messages.success(request, 'Membership was successfully renewed')
                return HttpResponseRedirect(reverse('member-detail', args=(id,)))
            except Exception as e:
                messages.error(request, f'Error renewing membership: {str(e)}')
                return render(request, template, {
                    'form': MemberMembershipForm(request.POST, request=request),
                    'member_id': id,
                })
        else:
            messages.error(request, form.errors)  
            return render(request, template, {
                'form': MemberMembershipForm(request.POST, request=request),
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


logger = logging.getLogger(__name__)

def pay_membership(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid Request'}, status=400)

    try:
        data = json.loads(request.body)
        id = data.get('id', '')
        discount = data.get('discount', '0')
        paid_amount = data.get('paid_amount', '0')

        # Conversão segura para Decimal
        discount_decimal = Decimal(discount) if discount else Decimal('0')
        paid_amount_decimal = Decimal(paid_amount) if paid_amount else Decimal('0')

        member_membership = MemberMembership.objects.get(pk=id)
        member_membership.discount = discount_decimal
        member_membership.paid_amount += paid_amount_decimal

        if member_membership.due_amount() > 0:
            member_membership.status = 'I'
        else:
            member_membership.status = 'P'

        member_membership.save()

        # Enviar email de confirmação
        success, message = send_payment_confirmation_email(member_membership)
        if not success:
            logger.warning(f"Email não enviado: {message}")

        return JsonResponse({'success': True, 'message': 'Pagamento processado com sucesso'})

    except MemberMembership.DoesNotExist:
        return JsonResponse({'error': 'Membership not found'}, status=404)
    except (InvalidOperation, ValueError) as e:
        return JsonResponse({'error': f'Invalid value: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f"Erro no pagamento: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
    

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

def member_attendance(request, id):
    template = "membership/member-attendance.html"
    member = Member.objects.get(pk=id)
    return render(request, template, {
        'member': member
    })


@login_required
def edit_member(request, id):
    template = "membership/edit-member.html"
    member = Member.objects.get(pk=id)
    
    if request.method == 'POST':        
        form = MemberForm(request.POST, request=request, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member successfully edited.')
            return HttpResponseRedirect(reverse('member-detail', args=(id,)))
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request, template, {'form' : form, 'id': id})
    
    # Obter o plano atual do membro
    current_membership = member.latest_membership().membership if member.latest_membership() else None
    
    # Criar o formulário com o plano atual como valor inicial
    form = MemberForm(
        request=request,
        instance=member,
        initial={'membership': current_membership} if current_membership else None
    )
    
    return render(request, template, {
        'form': form,
        'id': id
    })


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
def remove_plan(request, id):
    if request.method == "POST":
        membership = Membership.objects.get(pk=id)
        membership.delete()
        messages.success(request, 'Membership plan was successfully deleted')
        return HttpResponseRedirect(reverse('membership'))
    
@login_required
def punch_member_in_or_out(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid Request'})
    
    data = json.loads(request.body)
    id = data.get('id','')  
    member = Member.objects.get(id = id)
    attendances = Attendance.objects.filter(member = member, attendance_date = date.today())
    if not attendances:
        attendance = Attendance(member=member)
        movement = 'In'        
    else:
        attendance = attendances.order_by('id').last()
        if not attendance.exit_time:
            attendance.exit_time = datetime.datetime.now().strftime("%H:%M:%S")
            movement = 'Out'
        else:
            attendance = Attendance(member=member)
            movement = 'In'
    attendance.save()
    messages.success(request, "Check-{0} Registered".format(movement))
    return HttpResponseRedirect(reverse('member-detail', args=(id)))
