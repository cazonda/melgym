from .forms import SearchForm
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def inject_form(request):
    return {'searchform': SearchForm()}

def calc_membership_expiry_date(days, last_renew_date = None):
    if last_renew_date:
        today = last_renew_date
    else:
        today = date.today()

    if days%30 == 0:
        number_of_months = days // 30
        return today + relativedelta(months = +number_of_months)
    if days%365 == 0:
        number_of_years = days // 365
        return today + relativedelta(years = +number_of_years)
    
    return today + relativedelta(days = +days) 


# Funcao para verificar em quantos dias expira a assinatura do membro
# Para renovação automática e Enviar email de confirmação
def check_expiring_memberships():
    """
    Verifica assinaturas que expiram em 5 dias e cria novas automaticamente
    """
    from datetime import date, timedelta
    
    # Verifica assinaturas que expiram em 5 dias
    five_days_from_now = date.today() + timedelta(days=5)
    
    # Busca assinaturas que expiram em 5 dias e estão pagas
    expiring_memberships = MemberMembership.objects.filter(
        expiry_date__lte=five_days_from_now,
        status='P',  # Apenas assinaturas pagas
        auto_renewal=True  # Agora usando o nome correto do campo
    )
    
    for membership in expiring_memberships:
        # Cria nova assinatura
        new_membership = MemberMembership(
            member=membership.member,
            membership=membership.membership,
            purchase_date=date.today(),
            expiry_date=calc_membership_expiry_date(membership.membership.duration),
            total_amount=membership.membership.price,
            status='U',  # Começa como não pago
            auto_renewal=True  # Usando o nome correto do campo
        )
        new_membership.save()