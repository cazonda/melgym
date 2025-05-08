from datetime import date
from django.db import transaction
from .models import Member, MemberMembership
from .utils import calc_membership_expiry_date
from .notifications import send_payment_confirmation_email

@transaction.atomic
def process_membership_renewal(member_id, membership_id, paid_amount=0, discount=0, auto_renew=True):
    """
    Process membership renewal for a member.
    This function can be used by both the view and scheduler.
    
    Args:
        member_id: ID of the member
        membership_id: ID of the membership plan
        paid_amount: Amount paid (default 0)
        discount: Discount amount (default 0)
        auto_renew: Whether to auto-renew (default True)
    
    Returns:
        MemberMembership: The newly created membership
    """
    member = Member.objects.get(id=member_id)
    membership = member.latest_membership().membership
    
    # Calculate expiry date based on the membership duration
    expiry_date = calc_membership_expiry_date(
        membership.duration, 
        member.latest_membership().expiry_date
    )
    
    # Create new membership
    member_membership = MemberMembership(
        membership=membership,
        member=member,
        purchase_date=date.today(),
        expiry_date=expiry_date,
        total_amount=membership.price,
        discount=discount,
        paid_amount=paid_amount,
        training_start=member.latest_membership().training_start,
        training_end=member.latest_membership().training_end,
        admission_fees=0,
        auto_renew=auto_renew
    )
    
    # Set status based on payment
    if member_membership.paid_amount == 0:
        member_membership.status = 'U'
    elif member_membership.due_amount() > 0:
        member_membership.status = 'I'
    else:
        member_membership.status = 'P'
        # Send payment confirmation email
        send_payment_confirmation_email(member_membership)
    
    member_membership.save()
    return member_membership 