from django import template
from helpers import predict_income_by_date

register = template.Library()

def predict_amount(request, amount):
    return predict_income_by_date(request.session['access_token'], amount)

register.filter('predict', predict_amount)
