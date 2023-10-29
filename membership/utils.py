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