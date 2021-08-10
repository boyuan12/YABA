from django.shortcuts import render
import os
import plaid
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from .models import PlaidCredential
import calendar
import requests

# Create your views here.

# environment variable
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

print(PLAID_CLIENT_ID, PLAID_SECRET)
PLAID_ENV = 'development'
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_REDIRECT_URI = None

access_token = None
item_id = None

client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      environment=PLAID_ENV,
                      api_version='2019-05-29')

def index(request):
    print(PLAID_CLIENT_ID, PLAID_SECRET)
    return render(request, "plaid_api/index.html")

@csrf_exempt
def create_link_token(request):
    try:
        response = client.LinkToken.create(
            {
            'user': {
                # This should correspond to a unique id for the current user.
                'client_user_id': 'user-id',
            },
            'client_name': "Plaid Quickstart",
            'products': PLAID_PRODUCTS,
            'country_codes': PLAID_COUNTRY_CODES,
            'language': "en",
            'redirect_uri': PLAID_REDIRECT_URI,
            }
        )
        pretty_print_response(response)
        return JsonResponse(response)
    except plaid.errors.PlaidError as e:
        return JsonResponse(format_error(e))

@csrf_exempt
def get_access_token(request):
    global access_token
    global item_id
    public_token = request.POST['public_token']

    try:
        p = PlaidCredential.objects.get(user=request.user)
        request.session["access_token"] = p.access_token
        return JsonResponse({'error': None, 'access_token': p.access_token})
    except PlaidCredential.DoesNotExist:
        pass

    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return JsonResponse(format_error(e))

    pretty_print_response(exchange_response)
    request.session["access_token"] = exchange_response['access_token']
    item_id = exchange_response['item_id']

    PlaidCredential.objects.create(user=request.user,
                                   access_token=exchange_response['access_token'],
    ).save()

    return JsonResponse(exchange_response)

def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

@csrf_exempt
def info(request):
    global access_token
    global item_id
    try:
        access_token = request.session["access_token"]
    except:
        access_token = None
    return JsonResponse({
        'item_id': item_id,
        'access_token': access_token,
        'products': PLAID_PRODUCTS
    })

def get_transactions(request):
  # Pull transactions for the last 30 days
    return JsonResponse(_get_transactions(request.session["access_token"]))

def get_identity(request):
    try:
        identity_response = client.Identity.get(request.session["access_token"])
    except plaid.errors.PlaidError as e:
        return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(identity_response)
    return JsonResponse({'error': None, 'identity': identity_response['accounts']})

def get_balance(request):
    try:
        balance_response = client.Accounts.balance.get(request.session["access_token"])
    except plaid.errors.PlaidError as e:
        return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(balance_response)
    return JsonResponse(balance_response)

def get_auth(request):
    try:
        auth_response = client.Auth.get(request.session["access_token"])
    except plaid.errors.PlaidError as e:
        return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(auth_response)
    return JsonResponse(auth_response)

def get_inst_name(request):
    ins_id = request.GET.get('inst_id')
    response = client.Institutions.get_by_id(ins_id)
    print({"institution": response["institution"]["name"]})
    return JsonResponse({"institution": response["institution"]["name"]})

def _get_transactions(access_token, month=None, year=None):
    if month == None and year == None:
        given_date = datetime.datetime.today().date()
        start_date = str(given_date.replace(day=1))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
    else:
        start_date = f"{str(year)}-0{str(month)}-01"
        end_date = f"{str(year)}-0{str(month)}-{calendar.monthrange(year, month)[1]}"
    try:
        transactions_response = client.Transactions.get(access_token, start_date, end_date)
    except plaid.errors.PlaidError as e:
        return format_error(e)
    # pretty_print_response(transactions_response)
    return transactions_response

def _get_income(data):
    income = 0
    try:
        for t in data['transactions']:
            if t["amount"] < 0:
                income += t["amount"] * -1
    except:
        print(data)
        return
    return income

def _get_balance(access_token):
    try:
        balance_response = client.Accounts.balance.get(access_token)
    except plaid.errors.PlaidError as e:
        return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    return balance_response

def _get_transaction_by_category_id(access_token, category_id, month, year):
    data = _get_transactions(access_token, month, year)
    count = 0
    amount = 0
    for t in data["transactions"]:
        if t["category_id"] == category_id:
            count += 1
            amount += abs(t["amount"])
    return count, amount

def find_title_for_category_id(category_id):
    response = client.Categories.get()
    categories = response['categories']
    for c in categories:
        if c['category_id'] == category_id:
            return "/".join(c["hierarchy"])

def income_verification(request):
    data = requests.post("https://development.plaid.com/income/verification/create", headers={
        "Content-Type": "application/json",
    }, data=json.dumps({
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "webhook": "http://127.0.0.1:8000/plaid/income/webhook"
    }))
    print(data.json())
    return JsonResponse({'success': True})
