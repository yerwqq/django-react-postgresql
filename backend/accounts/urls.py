from django.urls import path
from .views import LoginView, RegisterView, ProfileView, UserView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('registration/', RegisterView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('user-act/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
]