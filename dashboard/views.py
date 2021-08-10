import datetime
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from plaid_api.views import _get_balance, client, PLAID_COUNTRY_CODES, pretty_print_response
import requests
from plaid_api.views import _get_transactions, _get_income, _get_transaction_by_category_id, find_title_for_category_id
from helpers import predict_transactions
from .models import Goal, Budget

BASE_URL = "http://127.0.0.1:8000"

# Create your views here.
def oauth_response(request):
    return render(request, "plaid/oauth-response.html")

def index(request):
    print(request.session.get("access_token"))
    return render(request, "dashboard/index.html", {
        "currency_code": requests.get("https://gist.githubusercontent.com/Fluidbyte/2973986/raw/5fda5e87189b066e11c1bf80bbfbecb556cf2cc1/Common-Currency.json").json()
    })

def transactions(request):
    data = _get_transactions(request.session['access_token'], 8, 2021)
    spending = 0
    income = 0
    for t in data["transactions"]:
        if t["amount"] > 0:
            spending += t["amount"]
        else:
            income += t["amount"] * -1
    return render(request, "dashboard/transactions.html", {
        "transactions": data,
        "spending": spending,
        "income": income,
    })

def goal(request):
    if request.method == "POST":
        title = request.POST.get("title")
        amount = int(request.POST.get("amount"))
        description = request.POST.get("description")
        end_date = datetime.datetime.strptime(request.POST.get("end_date"), "%Y-%m-%d").date()
        goal = Goal(title=title, amount=amount, description=description, end_date=end_date, user=request.user)
        goal.save()

        return redirect("/goals/")
    else:
        c = _get_balance(request.session['access_token'])

        print(c)

        goals = Goal.objects.filter(user=request.user)

        for g in goals:
            if g.amount >= c["accounts"][0]["balances"]["available"]:
                g.is_completed = True
                g.save()

        incomplete_goals = Goal.objects.filter(user=request.user, is_completed=False)
        complete_goals = Goal.objects.filter(user=request.user, is_completed=True)

        print(incomplete_goals, complete_goals)

        return render(request, "dashboard/goal.html", {
            "ig": incomplete_goals,
            "cg": complete_goals,
            "current": c,
        })

def budget(request):
    if request.method == "POST":
        category = request.POST.get("category")
        amount = int(request.POST.get("amount"))

        Budget(category=category, amount=amount, user=request.user).save()

        return redirect("/budget/")

    else:
        response = client.Categories.get()
        categories = response['categories']

        budgets_formatted = []
        budgets = Budget.objects.filter(user=request.user)
        for b in budgets:
            count, amount = _get_transaction_by_category_id(request.session['access_token'], b.category, 7, 2021)
            budgets_formatted.append([
                b,
                amount,
                count,
                find_title_for_category_id(b.category)
            ])
        # return JsonResponse(categories, safe=False)
        return render(request, "dashboard/budget.html", {
            "budgets": budgets_formatted,
            "categories": categories
        })

def edit_budget(request, budget_id):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        budget = Budget.objects.get(id=budget_id)
        budget.amount = amount
        budget.save()
        return redirect("/budget/")

    else:
        budget = Budget.objects.get(id=budget_id)
        return render(request, "dashboard/edit_budget.html", {
            "budget": budget,
            "category": find_title_for_category_id(budget.category),
        })

def delete_budget(request, budget_id):
    budget = Budget.objects.get(id=budget_id)
    budget.delete()
    return redirect("/budget/")

def edit_goal(request, goal_id):
    if request.method == "POST":
        title = request.POST.get("title")
        amount = int(request.POST.get("amount"))
        description = request.POST.get("description")
        end_date = datetime.datetime.strptime(request.POST.get("end_date"), "%Y-%m-%d").date()
        goal = Goal.objects.get(id=request.POST.get("goal_id"))
        goal.title = title
        goal.amount = amount
        goal.description = description
        goal.end_date = end_date
        goal.save()
        return redirect("/goals/")
    else:
        goal = Goal.objects.get(id=goal_id)
        return render(request, "dashboard/edit_goal.html", {
            "goal": goal,
        })

def acme_challenge(request):
    return HttpResponse("M3m2WeBMpGxGeMD8DPR6LMvzP93nmlHSq2jjiQG6DX0.xJWc3jMocrApnPhYP7Kw3tXWvavXDmXaOU-ct6WfU0c")