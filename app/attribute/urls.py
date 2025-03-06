from django.urls import path
from app.attribute import apis


urlpatterns = [
    path('', apis.get_attribute_groups),
    path('add/', apis.create_attribute_group),
    path('<int:ag_id>/update/', apis.update_attribute_group),
    path('<int:ag_id>/delete/', apis.delete_attribute_group),
]
