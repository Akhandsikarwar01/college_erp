from django.urls import path
from . import views

urlpatterns = [
    path("structure/",                views.fee_structure_list,   name="fee_structure_list"),
    path("structure/add/",            views.add_fee_structure,    name="add_fee_structure"),
    path("generate/",                 views.generate_fees,        name="generate_fees"),
    path("report/",                   views.fee_collection_report, name="fee_collection_report"),
    path("<int:fee_id>/pay/",         views.record_payment,       name="record_payment"),
    path("my-fees/",                  views.my_fees,              name="my_fees"),
]
