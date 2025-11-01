"""
URL configuration for gradesystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import logout
from django.shortcuts import redirect

# 自訂登出 view：支援 GET 登出
def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')  # 登出後導向登入頁

urlpatterns = [
    path('admin/', admin.site.urls),
    path('course/', include('course.urls')),

    # 自訂 logout (支援 GET)
    path('accounts/logout/', logout_view, name='logout'),

    # 其餘帳號相關（登入、密碼重設等）
    path('accounts/', include('django.contrib.auth.urls')),
]

