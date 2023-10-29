from django.urls import path
from . import views
from .views import ChatEndpointView

urlpatterns = [
    path("", views.home_view, name="home"),
    path("ask/", ChatEndpointView.as_view(), name="chat_endpoint"),
    path(
        "terms_and_policies/", views.terms_and_policies_view, name="terms_and_policies"
    ),
]
