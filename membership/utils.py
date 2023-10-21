from .forms import SearchForm
from datetime import date, timedelta

def inject_form(request):
    return {'searchform': SearchForm()}

def calc_membership_expiry_date(days):
    today = date.today()
    if days%30 == 0:
        number_of_months = days // 30
        return today + timedelta(months = number_of_months)
    if days%365 == 0:
        number_of_years = days // 365
        return today + timedelta(years = number_of_years)
    
    return today + timedelta(days = days) 