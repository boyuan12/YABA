from django.urls import path
from . import views

urlpatterns = [
    path('oauth-response.html/', views.oauth_response),
    path("", views.index),
    path("transactions/", views.transactions),
    path("goal/", views.goal),
    path("budget/", views.budget),
    path("edit-budget/<str:budget_id>/", views.edit_budget),
    path("delete-budget/<str:budget_id>/", views.delete_budget),
    path("edit-goal/<str:goal_id>/", views.edit_goal),
    path(".well-known/acme-challenge/M3m2WeBMpGxGeMD8DPR6LMvzP93nmlHSq2jjiQG6DX0", views.acme_challenge)
]