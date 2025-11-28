"""
URL configuration for noticeboard project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from users.admin_site import sitds_admin
from notices.views import home

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('admin/', sitds_admin.urls),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=False
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),  # Add authentication URLs
    path('users/', include('users.urls')),  # Include users URLs
    path('', include('notices.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
