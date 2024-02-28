from os import name
from django.urls import path

from . import views

app_name = 'dataction'
urlpatterns = [
    path('', views.home, name='home'),
    path('submit/',views.submit,name='submit'),
    path('point_index/',views.point_index,name="point_index"),
    path('consigne/',views.consigne,name="consigne"),
    path('test/',views.test,name='test'),
    path('<int:point_id>/',views.point_detail,name="detail"),
    path('global_map/',views.global_map,name="global_map"),
]