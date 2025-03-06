from django.urls import path
from app.product import apis


urlpatterns = [
    path('', apis.get_products),
    path('add/', apis.create_product),
    path('add/bulk/', apis.add_multiple_products),
    path('<int:pd_id>/update/', apis.update_product),
    path('<int:pd_id>/delete/', apis.delete_product),
]
