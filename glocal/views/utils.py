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
        print("Cambio en la vista: ", changes)
        for change in changes:
            change.is_deletion = change.action_type == 'delete'  # Agrega un atributo al objeto

            # Obtener el nombre del objeto
            model_class = apps.get_model(app_label='glocal', model_name=change.model_name)
            obj = model_class.objects.filter(pk=change.object_id).first()
            change.object_name = obj.nombre if obj else 'N/A'

        context = {
            'changes': changes
        }

        return render(request, 'administracion/cambios_admin.html', context=context)

@method_decorator(login_required, name='dispatch')
class PendingChangeApprovalView(View):
    def post(self, request, *args, **kwargs):
        change_id = kwargs.get("change_id")
        change = get_object_or_404(PendingChange, id=change_id)
        print("Cambio pendiente: ", change.changes)
        usuario = change.submitted_by
        action = request.POST.get("action")  # Puede ser "approve" o "reject"

        if action == "approve":
            # Obtener el modelo dinámicamente
            model = apps.get_model(app_label='glocal', model_name=change.model_name)

            # Manejar según el tipo de acción
            if change.action_type == "create":
                m2m_fields = {}  # Almacenar campos ManyToMany para asignarlos después
                regular_fields = {}

                for field, values in change.changes.items():
                    if isinstance(model._meta.get_field(field), models.ManyToManyField):
                        m2m_fields[field] = values["new"]  # Guardar los valores de ManyToManyField
                    else:
                        regular_fields[field] = values["new"]

                # Crear instancia con campos regulares
                instance = model(**regular_fields)
                instance.save()

                # Asignar relaciones ManyToMany
                for field, values in m2m_fields.items():
                    m2m_manager = getattr(instance, field)
                    m2m_manager.set(values)  # Usar set() para asignar los valores correctamente

                # Registrar quién realizó el cambio
                instance.modified_by = usuario
                instance.save(track_changes=False)  # Evitar registrar PendingChange

            elif change.action_type == "edit":
                try:
                    instance = model.objects.get(pk=change.object_id)
                except model.DoesNotExist:
                    messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
                    return redirect("cambios_pendientes")

                m2m_fields = {}
                for field, values in change.changes.items():
                    if "new" in values:
                        if isinstance(model._meta.get_field(field), models.ManyToManyField):
                            m2m_fields[field] = values["new"]
                        else:
                            setattr(instance, field, values["new"])
                
                instance.save(track_changes=False)  # Guardar cambios regulares

                # Actualizar relaciones ManyToMany
                for field, values in m2m_fields.items():
                    m2m_manager = getattr(instance, field)
                    m2m_manager.set(values)

            elif change.action_type == "delete":
                try:
                    instance = model.objects.get(pk=change.object_id)
                    instance.delete()
                except model.DoesNotExist:
                    messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
                    return redirect("cambios_pendientes")

            # Marcar el cambio como aprobado
            change.is_approved = True
            change.save()

            # Eliminar el cambio de la lista de pendientes después de procesarlo
            change.delete()

            messages.success(request, f"Cambio aprobado exitosamente por {request.user}.")

        elif action == "reject":
            # Si se rechaza, marcar como rechazado y eliminar el cambio pendiente
            change.is_approved = False
            change.save()

            # Eliminar el cambio de la lista de pendientes
            change.delete()
            messages.info(request, "Cambio rechazado.")

        return redirect("cambios_pendientes")
# Aprobar 2

# @method_decorator(login_required, name='dispatch')
# class PendingChangeApprovalView(View):
#     def post(self, request, *args, **kwargs):
#         change_id = kwargs.get("change_id")
#         change = get_object_or_404(PendingChange, id=change_id)
#         usuario = change.submitted_by
#         action = request.POST.get("action")  # Puede ser "approve" o "reject"

#         if action == "approve":
#             # Obtener el modelo dinámicamente
#             model = apps.get_model(app_label='glocal', model_name=change.model_name)

#             # Manejar según el tipo de acción
#             if change.action_type == "create":
#                 # Crear una nueva instancia del modelo sin incluir campos ManyToMany
#                 m2m_fields = {}  # Almacenar campos ManyToMany para asignarlos después
#                 regular_fields = {}

#                 for field, values in change.changes.items():
#                     if isinstance(model._meta.get_field(field), models.ManyToManyField):
#                         m2m_fields[field] = values["new"]  # Guardar los valores de ManyToManyField
#                     else:
#                         regular_fields[field] = values["new"]

#                 # Crear instancia con campos regulares
#                 instance = model(**regular_fields)
#                 instance.save()

#                 # Asignar relaciones ManyToMany
#                 for field, values in m2m_fields.items():
#                     m2m_manager = getattr(instance, field)
#                     m2m_manager.set(values)  # Usar set() para asignar los valores correctamente

#                 # Registrar quién realizó el cambio
#                 instance.modified_by = usuario
#                 instance.save(track_changes=False)  # Evitar registrar PendingChange

#             elif change.action_type == "edit":
#                 try:
#                     instance = model.objects.get(pk=change.object_id)
#                 except model.DoesNotExist:
#                     messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
#                     return redirect("cambios_pendientes")

#                 m2m_fields = {}
#                 for field, values in change.changes.items():
#                     if "new" in values:
#                         if isinstance(model._meta.get_field(field), models.ManyToManyField):
#                             m2m_fields[field] = values["new"]
#                         else:
#                             setattr(instance, field, values["new"])
                
#                 instance.save(track_changes=False)  # Guardar cambios regulares

#                 # Actualizar relaciones ManyToMany
#                 for field, values in m2m_fields.items():
#                     m2m_manager = getattr(instance, field)
#                     m2m_manager.set(values)

#             elif change.action_type == "delete":
#                 try:
#                     instance = model.objects.get(pk=change.object_id)
#                     instance.delete()
#                 except model.DoesNotExist:
#                     messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
#                     return redirect("cambios_pendientes")

#             # Marcar el cambio como aprobado y eliminarlo
#             change.is_approved = True
#             change.save()
#             change.delete()
#             messages.success(request, f"Cambio aprobado exitosamente por {request.user}.")

#         elif action == "reject":
#             # Si se rechaza, marcar como rechazado y eliminar el cambio pendiente
#             change.is_approved = False
#             change.save()
#             change.delete()  # Eliminar el cambio de la lista de pendientes
#             messages.info(request, "Cambio rechazado.")

#         return redirect("cambios_pendientes")

# Aprobar 1

# @method_decorator(login_required, name='dispatch')
# class PendingChangeApprovalView(View):
#     def post(self, request, *args, **kwargs):
#         change_id = kwargs.get("change_id")
#         change = get_object_or_404(PendingChange, id=change_id)
#         usuario = change.submitted_by
#         action = request.POST.get("action")  # Puede ser "approve" o "reject"

#         if action == "approve":
#             # Obtener el modelo dinámicamente
#             model = apps.get_model(app_label='glocal', model_name=change.model_name)

#             # Manejar según el tipo de acción
#             if change.action_type == "create":
#                 # Crear una nueva instancia del modelo
#                 instance = model(**{field: values["new"] for field, values in change.changes.items()})

#                 instance.save()

#                 instance.modified_by = usuario  # Registrar quién realizó el cambio (sino es null)
#                 instance.save(track_changes=False)  # Evitar registrar PendingChange
                
                

#             elif change.action_type == "edit":
#                 # Buscar la instancia existente y aplicar los cambios
#                 try:
#                     instance = model.objects.get(pk=change.object_id)
#                 except model.DoesNotExist:
#                     messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
#                     return redirect("cambios_pendientes")

#                 # Actualizar los campos con los valores nuevos
#                 for field, values in change.changes.items():
#                     if "new" in values:
#                         setattr(instance, field, values["new"])
#                     else:
#                         messages.error(request, f"Error: No se encontró el valor 'new' para el campo {field}.")
#                         return redirect("cambios_pendientes")
#                 instance.save(track_changes=False)  # Evitar registrar PendingChange

#             elif change.action_type == "delete":
#                 # Buscar y eliminar la instancia existente
#                 try:
#                     instance = model.objects.get(pk=change.object_id)
#                     instance.delete()
#                 except model.DoesNotExist:
#                     messages.error(request, f"Error: No se encontró la instancia con ID {change.object_id}.")
#                     return redirect("cambios_pendientes")

#             # Marcar el cambio como aprobado y eliminarlo
#             change.is_approved = True
#             change.save()
#             change.delete()
#             messages.success(request, f"Cambio aprobado exitosamente por {request.user}.")

#         elif action == "reject":
#             # Si se rechaza, marcar como rechazado y eliminar el cambio pendiente
#             change.is_approved = False
#             change.save()
#             change.delete()  # Eliminar el cambio de la lista de pendientes
#             messages.info(request, "Cambio rechazado.")

#         return redirect("cambios_pendientes")


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
        