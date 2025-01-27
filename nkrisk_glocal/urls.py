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
from glocal.views import utils, matriz, broker, contacto
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', utils.HomeView.as_view(), name='home'),
    path('inicio/', utils.InicioView.as_view(), name='inicio'),
    
    # MATRICES
    path('administracion/matrices/', matriz.MatrizView.as_view(), name="matrices_admin"),
    path('administracion/matrices/<int:matriz_id>/eliminar/', matriz.EliminarMatrizView.as_view(), name='delete_matriz'),
    path('administracion/matrices/<int:matriz_id>/editar/', matriz.EditarMatrizView.as_view(), name='update_matriz'),
    
    # BROKERS
    path('administracion/brokers/', broker.BrokerView.as_view(), name="brokers_admin"),
    path('administracion/brokers/<int:broker_id>/eliminar/', broker.EliminarBrokerView.as_view(), name='delete_broker'),
    path('administracion/brokers/<int:broker_id>/editar/', broker.EditarBrokerView.as_view(), name='update_broker'),
    
    # CONTACTOS
    path('administracion/contactos/', contacto.ContactoView.as_view(), name="contactos_admin"),
    path('administracion/contactos/<int:contacto_id>/eliminar/', contacto.EliminarContactoView.as_view(), name='delete_contacto'),
    path('administracion/contactos/<int:contacto_id>/editar/', contacto.EditarContactoView.as_view(), name='update_contacto'),
    
    # CAMBIOS PENDIENTES
    path('administracion/cambios_pendientes/', utils.CambiosPendientesView.as_view(), name='cambios_pendientes'),
    path('administracion/approve-change/<int:change_id>/', utils.PendingChangeApprovalView.as_view(), name='approve_change'),
    
    # AUTENTICACIÓN
    path('login/', utils.SignInView.as_view(), name="login"),
    path('logout/', utils.SignOutView.as_view(), name="logout"), 

]

# Esto solo se usa en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)