from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.course_list, name='course_list'),
    path('add/', views.add_course, name='add_course'),
    path('detail/<str:course_id>/', views.course_detail, name='course_detail'), 

    path('enroll/<str:course_id>/', views.enroll_course, name='enroll_course'),
    path('drop/<str:course_id>/', views.drop_course, name='drop_course'),
    path('my/', views.my_courses, name='my_courses'),

]
