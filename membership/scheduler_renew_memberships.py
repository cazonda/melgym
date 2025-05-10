from django.utils import timezone
from datetime import date
from .models import MemberMembership
from .services import process_membership_renewal

def check_and_renew_memberships():
    today = date.today()
    print(f"\nIniciando verificação de planos para {today}")
    
    # Busca planos que expiram hoje
    expiring_memberships = MemberMembership.objects.filter(
        expiry_date=today,
        auto_renew=True,
        # status='P'
    )
    print(f"Encontrados {expiring_memberships.count()} planos para renovar")

    renewed_count = 0
    # Para cada plano que expira hoje
    for membership in expiring_memberships:
        try:
            print(f"Processando renovação para {membership.member.first_name} (ID: {membership.id})")
            # Processa a renovação usando o serviço
            process_membership_renewal(
                member_id=membership.member.id,
                membership_id=membership.membership.id,
                paid_amount=0,  # Começa como não pago
                discount=0,
                auto_renew=True
            )
            renewed_count += 1
            print(f"✓ Renovado com sucesso: {membership.member.first_name}")
        except Exception as e:
            print(f"✗ Erro ao renovar plano para {membership.member.first_name}: {e}")

    # Busca planos que começam hoje
    starting_memberships = MemberMembership.objects.filter(
        purchase_date=today,
        status='P'
    )
    print(f"\nEncontrados {starting_memberships.count()} planos para ativar")

    activated_count = 0
    # Para cada plano que começa hoje
    for membership in starting_memberships:
        try:
            print(f"Processando ativação para {membership.member.first_name} (ID: {membership.id})")
            # Ativa o plano
            membership.status = 'A'  # 'A' para ativo
            membership.save()
            activated_count += 1
            print(f"✓ Ativado com sucesso: {membership.member.first_name}")
        except Exception as e:
            print(f"✗ Erro ao ativar plano para {membership.member.first_name}: {e}")

    print(f"\nResumo da execução:")
    print(f"- Planos renovados: {renewed_count}")
    print(f"- Planos ativados: {activated_count}")
    
    return {
        'renewed': renewed_count,
        'activated': activated_count
    }