from django.urls import path
from app.family import apis


urlpatterns = [
    path('', apis.get_product_families),
    path('add/', apis.add_product_family),
    path('<int:pf_id>/attributes/', apis.get_family_attributes),
    path('<int:pd_id>/update/', apis.update_product_family),
    path('<int:pd_id>/delete/', apis.delete_product_family),
]
