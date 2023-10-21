from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.db import models
from datetime import date

class User(AbstractUser):
    personal_address = models.CharField(max_length=100, blank=False)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, blank=False)

class Membership(models.Model):
    membership_type = models.CharField(max_length=100, blank=False)
    membership_price = models.DecimalField(max_digits=20, decimal_places=2)
    #duration in days
    membership_duration = models.SmallIntegerField()
    

    def __str__(self):
        if self.membership_duration == 1 :
            return f"{self.membership_type} for {self.membership_duration} day"
        else:
            return f"{self.membership_type} for {self.membership_duration} days"


class Members(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    age = models.IntegerField(blank=False)
    gender = models.CharField(max_length=10, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    address = models.CharField(max_length=100, blank=False)
    membership = models.ManyToManyField(Membership, through = 'membership.MemberMembership')

    def latest_membership(self):        
        return MemberMembership.objects.filter(member_id = self.id).last()

    def all_memberships(self):
        return MemberMembership.objects.filter(member_id = self.id)
    
    def due_amount(self):
        sum_dict = MemberMembership.objects.filter(member_id = self.id).aggregate(
            total_amount = Sum('total_amount'),
            discount = Sum('discount'),
            paid_amount = Sum('paid_amount'),
            admission_fees = Sum('admission_fees'),
        )
        print(sum_dict)
        total_amount = sum_dict['total_amount'] if sum_dict['total_amount'] else 0
        discount = sum_dict['discount'] if sum_dict['discount'] else 0
        paid_amount = sum_dict['paid_amount'] if sum_dict['paid_amount'] else 0
        admission_fees = sum_dict['admission_fees'] if sum_dict['admission_fees'] else 0

        due = total_amount + admission_fees - discount - paid_amount
        return f'{due} MZN'


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_valid(self):
        return date.today() < self.latest_membership().expiry_date()
    

class MemberMembership(models.Model):
    membership = models.ForeignKey(Membership, models.DO_NOTHING)
    member = models.ForeignKey(Members, models.DO_NOTHING)
    purchase_date = models.DateField()
    expiry_date = models.DateField()
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    admission_fees = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=2, blank=False)

    def due_amount(self):
        return self.total_amount + self.admission_fees - self.discount - self.paid_amount

    def __str__(self):
        return f'{self.membership.membership_type} until {self.expiry_date}'


class Payment(models.Model):
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    member_membership = models.ForeignKey(MemberMembership, on_delete=models.CASCADE)