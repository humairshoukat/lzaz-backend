from django.urls import path
from app.user import apis


urlpatterns = [
    path('', apis.get_users),
    path('login/', apis.login),
    path('add/', apis.add_user),
    path('<int:user_id>/update/', apis.update_user),
    path('<int:user_id>/delete/', apis.delete_user),
    path('forgot/password/', apis.forgot_password),
    path('reset/password/', apis.reset_password),
]
