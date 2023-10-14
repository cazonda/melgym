from django.contrib.auth.models import AbstractUser
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
    membership_duration = models.CharField(max_length=20, blank=False)

    def __str__(self):
        if self.membership_duration == "1" :
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
     
    #member.membership 
    #member.validity
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_valid(self):
        return date.today() < self.validity
    

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

    def __str__(self):
        return f'{self.membership} until {self.expiry_date}'


class Payment(models.Model):
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    member_membership = models.ForeignKey(MemberMembership, on_delete=models.CASCADE)