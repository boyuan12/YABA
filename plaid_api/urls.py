from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("create_link_token/", views.create_link_token),
    path("set_access_token/", views.get_access_token),
    path("info/", views.info),
    path("transactions/", views.get_transactions),
    path("identity/", views.get_identity),
    path("balance/", views.get_balance),
    path("auth/", views.get_auth),
    path("inst_name/", views.get_inst_name),
    path("income/", views.income_verification),
]