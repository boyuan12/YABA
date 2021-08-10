import matplotlib.pyplot as plt
from plaid_api.views import _get_transactions, _get_income
from scipy import stats
from time import sleep
from termcolor import colored


def predict_transactions(access_token, m):
    x = [1,2,3,4,5,6]
    y = []

    for i in range(1, 7):
        y.append(sum([_get_income(_get_transactions(access_token, j, 2021)) for j in range(1, i)]))

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def myfunc(x):
        return slope * x + intercept

    return myfunc(m)


def predict_income(access_token):
    x = [1,2,3,4,5,6]
    y = []

    for i in range(1, 7):
        y.append(sum([_get_income(_get_transactions(access_token, j, 2021)) for j in range(1, i)]))
        sleep(1)
        print("hi")

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def myfunc(x):
        return slope * x + intercept

    return myfunc

def random_str(n):
    import string
    import random
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def predict_income_by_date(access_token, amount):
    from datetime import date, datetime
    from dateutil.relativedelta import relativedelta

    p = predict_income(access_token)

    m = 1
    while True:
        if p(float(amount)) > float(amount):
                print(colored(p(float(amount)), "red"))
                print(colored(amount, "red"))
                print(colored(m, "red"))
                today = datetime.today()
                return date(today.year,today.month,today.day)+relativedelta(months=+m)
        m += 1
