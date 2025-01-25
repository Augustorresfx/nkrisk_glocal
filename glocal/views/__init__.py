from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseServerError
from django.apps import apps
from django.db import models

# Importe Modelos
from ..models import Pais, Matriz, Broker, Aseguradora, PendingChange
    
    
# Usuarios / roles
def is_admin(user):
    return user.is_superuser
    
# Home
class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')
        else:
            return redirect('login')
    
# Inicio
@method_decorator(login_required, name='dispatch')
class InicioView(View):
    def get(self, request, *args, **kwargs):
        
        context = {
            
        }
        return render(request, 'homepage/index.html', context)
    
# Cambios
@method_decorator(login_required, name='dispatch')
class CambiosPendientesView(View):
    def get(self, request, *args, **kwargs):
        changes = PendingChange.objects.filter(approved__isnull=True)

        for change in changes:
            change.is_deletion = change.action_type == 'delete'  # Agrega un atributo al objeto

            # Obtener el nombre del objeto
            model_class = apps.get_model(app_label='glocal', model_name=change.model_name)  # Cambia 'app_name' por el nombre de tu aplicación
            obj = model_class.objects.filter(pk=change.object_id).first()
            change.object_name = obj.nombre if obj else 'N/A'

        context = {
            'changes': changes
        }

        return render(request, 'administracion/cambios_admin.html', context=context)

# Utils
@method_decorator(login_required, name='dispatch')
class PendingChangeApprovalView(View):
    def post(self, request, change_id):
        change = get_object_or_404(PendingChange, id=change_id)
        usuario = change.submitted_by
        action = request.POST.get("action")

        if action == "approve":
            # Obtener el modelo dinámicamente
            model = apps.get_model(app_label='glocal', model_name=change.model_name)
            instance = model.objects.get(pk=change.object_id)

            for field, values in change.changes.items():
                if "new" not in values:
                    messages.error(request, f"Error: No se encontró el valor 'nuevo' para el campo {field}")
                    return redirect('cambios_pendientes')

                # Detectar dinámicamente si el campo es un ForeignKey
                field_object = instance._meta.get_field(field)
                if isinstance(field_object, models.ForeignKey):
                    # Obtener el modelo relacionado
                    related_model = field_object.related_model
                    # Obtener la instancia del modelo relacionado
                    related_instance = get_object_or_404(related_model, id=values["new"]["id"])
                    setattr(instance, field, related_instance)
                elif field == "modified_by" or field == "submitted_by":
                    setattr(instance, field, usuario)
                else:
                    setattr(instance, field, values["new"]["id"] if isinstance(values["new"], dict) else values["new"])

            # Guardar la instancia actualizada
            instance.save()

            # Actualizar el estado del cambio pendiente
            change.approved = True
            change.save()

            messages.success(request, "Cambio aprobado exitosamente.")
            return redirect('cambios_pendientes')

        elif action == "reject":
            # Si se rechaza, actualizar el estado del cambio
            change.approved = False
            change.save()
            messages.info(request, "Cambio rechazado.")

        return redirect('cambios_pendientes')

# Autenticación
class SignOutView(View):
    def get(self, request, *args, **kwargs):
        try:
            logout(request)
            
            pass
        except Exception as e:
            # Log del error
            print(e)
            return HttpResponseServerError("Error interno del servidor.")
        
        return redirect('login')

class SignInView(View):
    def get(self, request, *args, **kwargs):    
        if request.user.is_authenticated:
            return redirect('inicio')
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
        
        return render(request, 'login.html', {
            'form': form,
            'error': 'El nombre de usuario o la contraseña no existen',
        })
        