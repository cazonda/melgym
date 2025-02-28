from django.db.models import Sum
from django.db import models
from datetime import date

#class User(AbstractUser):
#    personal_address = models.CharField(max_length=100, blank=False)
#    date_of_birth = models.DateField()
#    phone_number = models.CharField(max_length=20, blank=False)

class Base(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    create_user =  models.CharField(max_length=255)
    update_date = models.DateTimeField(auto_now=True)
    update_user = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class ParCodigoDescricao(Base):
    codigo = models.CharField(max_length=10)
    descricao = models.CharField(max_length=100, blank=False)

    def __str__(self) -> str:
        return str(self.descricao)

    class Meta:
        abstract = True

class MembershipType(ParCodigoDescricao):
    pass

class TrainingObjective(ParCodigoDescricao):
    pass

class Membership(Base):
    name = models.CharField(max_length=100, blank=False)
    type = models.ForeignKey(MembershipType, models.DO_NOTHING)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    #duration in days
    duration = models.SmallIntegerField()    

    def __str__(self):
        if self.duration == 1 :
            return f"{self.name} for {self.duration} day"
        else:
            return f"{self.name} for {self.duration} days"

class Member(Base):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    address = models.CharField(max_length=100, blank=False)
    training_objectives = models.ManyToManyField(TrainingObjective)
    membership = models.ManyToManyField(Membership, through = 'membership.MemberMembership')

    def latest_membership(self):        
        return MemberMembership.objects.filter(member_id = self.id).last()

    def latest_memberships(self):
        return MemberMembership.objects.filter(member_id = self.id).order_by('-id')
    
    def attendances(self):
        return Attendance.objects.filter(member=self).order_by('-id')
    
    def due_amount(self):
        sum_dict = MemberMembership.objects.filter(member_id = self.id).aggregate(
            total_amount = Sum('total_amount'),
            discount = Sum('discount'),
            paid_amount = Sum('paid_amount'),
            admission_fees = Sum('admission_fees'),
        )
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
    

class MemberMembership(Base):
    membership = models.ForeignKey(Membership, models.DO_NOTHING)
    member = models.ForeignKey(Member, models.DO_NOTHING)
    purchase_date = models.DateField()
    expiry_date = models.DateField()
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    admission_fees = models.DecimalField(max_digits=20, decimal_places=2)
    training_start = models.TimeField() 
    training_end = models.TimeField()     
    #(U)npaid, (I)ncomplete, (P)aid
    status = models.CharField(max_length=2, blank=False)

    def due_amount(self):
        return self.total_amount + self.admission_fees - self.discount - self.paid_amount
    
    def is_late(self):
        return self.expiry_date < date.today()

    def __str__(self):
        return f'{self.membership.name} until {self.expiry_date}'


class Attendance(Base):
    member = models.ForeignKey(Member, models.DO_NOTHING)
    attendance_date = models.DateField(auto_now_add = True)
    entrance_time = models.TimeField(auto_now_add = True)
    exit_time = models.TimeField(null = True)