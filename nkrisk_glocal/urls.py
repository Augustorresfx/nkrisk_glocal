"""
URL configuration for nkrisk_glocal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from glocal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('inicio/', views.InicioView.as_view(), name='inicio'),
    
    # MATRICES
    path('administracion/matrices/', views.MatrizView.as_view(), name="matrices_admin"),
    path('administracion/matrices/<int:matriz_id>/eliminar/', views.EliminarMatrizView.as_view(), name='delete_matriz'),
    path('administracion/matrices/<int:matriz_id>/editar/', views.EditarMatrizView.as_view(), name='update_matriz'),

    # CAMBIOS PENDIENTES
    path('administracion/cambios_pendientes/', views.CambiosPendientesView.as_view(), name='cambios_pendientes'),
    path('administracion/approve-change/<int:change_id>/', views.PendingChangeApprovalView.as_view(), name='approve_change'),
    
    # AUTENTICACIÓN
    path('login/', views.SignInView.as_view(), name="login"),
    path('logout/', views.SignOutView.as_view(), name="logout"), 
]
