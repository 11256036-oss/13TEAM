from django.urls import path
from django.views.generic import RedirectView 
from . import views


urlpatterns = [
    # ✅ 首頁 index（登入後會用到）
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),

    path('register/', views.register, name='register'),

    path('teacher/', views.teacher_courses, name='teacher_courses'),
    path('teacher/create/', views.create_course, name='create_course'),
    path('teacher/course/<int:course_id>/', views.course_students, name='course_students'),

    path('student/', views.student_courses, name='student_courses'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll_course'),
    path('drop/<int:course_id>/', views.drop, name='drop_course'),
    path('grades/', views.my_grades, name='my_grades'),

    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('after-login/', views.after_login, name='after_login'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('teacher/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]
