from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect

# Importe Modelos
from ..models import User, Contacto, PendingChange

# ADMINISTRACION
@method_decorator(login_required, name='dispatch')
class ContactoView(View):
    def get(self, request, *args, **kwargs):
        
        # Obtener filtros desde los parámetros GET
        nombre_filtro = request.GET.get('nombre', '').strip()
        email_filtro = request.GET.get('email', '').strip()
        telefono_filtro = request.GET.get('telefono', '').strip()
        cargo_filtro = request.GET.get('cargo', '').strip()

        # Filtrar los contactos con base en los filtros
        contactos = Contacto.objects.all()
        if nombre_filtro:
            contactos = contactos.filter(nombre__icontains=nombre_filtro)

        if email_filtro:
            contactos = contactos.filter(email__icontains=email_filtro)

        if telefono_filtro:
            contactos = contactos.filter(telefono__icontains=telefono_filtro)

        if cargo_filtro:
            contactos = contactos.filter(cargo__icontains=cargo_filtro)
        # Paginación
        contactos_paginados = Paginator(contactos, 30)
        page_number = request.GET.get("page")
        filter_pages = contactos_paginados.get_page(page_number)
        for contacto in filter_pages:

            print(contacto.user)
        # Obtener la lista de usuarios
        usuarios = User.objects.all()
        print("Usuarios: ", usuarios)
        context = {
            'contactos': contactos,
            'pages': filter_pages,
            'usuarios': usuarios,
            'filtros': {
                'nombre': nombre_filtro,
                'email': email_filtro,
                'telefono': telefono_filtro,
                'cargo': cargo_filtro,
            }
        }
        return render(request, 'administracion/contactos_admin.html', context)

    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        nombre = request.POST.get('nuevo_nombre')
        email = request.POST.get('nuevo_email')
        telefono = request.POST.get('nuevo_telefono')
        cargo = request.POST.get('nuevo_cargo')
        user_id = request.POST.get('nuevo_user')

        usuario_contacto = get_object_or_404(User, id=user_id)
        user = request.user

        # Crear una solicitud de creación pendiente
        changes = {
            'nombre': {'new': nombre},
            'email': {'new': email},
            'telefono': {'new': telefono},
            'cargo': {'new': cargo},
            'user_id': {'new': usuario_contacto.id},
        }
        if user.is_superuser:
            try:
                Contacto.objects.create(
                nombre = nombre,
                email=email,
                telefono=telefono,
                cargo=cargo,
                user = usuario_contacto
                )
                messages.success(request, 'Se creó un nuevo elemento de forma exitosa.')
            except Exception as e:
                messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')
 
        else:
            try:
                PendingChange.objects.create(
                    model_name='contacto',
                    object_id=None,  # No existe aún
                    changes=changes,
                    submitted_by=user,
                    action_type='create',
                )
                messages.success(request, 'Solicitud de creación enviada para aprobación.')
            except Exception as e:
                messages.error(request, f'Error: No se pudo enviar la solicitud. Detalles: {str(e)}')

        return HttpResponseRedirect(request.path_info)

    
@method_decorator(login_required, name='dispatch')
class EditarContactoView(View):
    def post(self, request, contacto_id):
        contacto = get_object_or_404(Contacto, id=contacto_id)
        nombre = request.POST.get('editar_nombre')
        email = request.POST.get('editar_email')
        telefono = request.POST.get('editar_telefono')
        cargo = request.POST.get('editar_cargo')
        user_id = request.POST.get('editar_usuario')
        nombre = request.POST.get('editar_nombre')

        user = request.user

        # Si el usuario es superuser, aplicar los cambios directamente
        if user.is_superuser:
            if contacto.nombre != nombre:
                contacto.nombre = nombre
            if contacto.email != email:
                contacto.email = email
            if contacto.telefono != telefono:
                contacto.telefono = telefono
            if contacto.cargo != cargo:
                contacto.cargo = cargo
            if contacto.user_id != int(user_id):
                contacto.user_id = user_id

            contacto.save()  # Guardar los cambios directamente
            messages.success(request, 'Los cambios se han aplicado directamente.')
            return redirect('contactos_admin')

        # Para usuarios no superuser, registrar los cambios pendientes
        changes = {}
        if contacto.nombre != nombre:
            changes['nombre'] = {'old': contacto.nombre, 'new': nombre}
            contacto.nombre = nombre
            
        if contacto.email != email:
            changes['email'] = {'old': contacto.email, 'new': email}
            contacto.email = email
            
        if contacto.telefono != telefono:
            changes['telefono'] = {'old': contacto.telefono, 'new': telefono}
            contacto.telefono = telefono
            
        if contacto.cargo != cargo:
            changes['cargo'] = {'old': contacto.cargo, 'new': cargo}
            contacto.cargo = cargo

        if contacto.user_id != int(user_id):
            changes['user_id'] = {'old': contacto.user_id, 'new': int(user_id)}
            contacto.user_id = user_id

        if changes:
            try:
                PendingChange.objects.create(
                    model_name='contacto',
                    object_id=contacto.id,
                    changes=changes,
                    submitted_by=user,
                    action_type='edit'
                )
                messages.success(request, 'El cambio ha sido registrado para revisión.')
            except Exception as e:
                messages.error(request, f'Error al registrar el cambio: {str(e)}')
        else:
            messages.info(request, 'No se detectaron cambios.')

        return redirect('contactos_admin')

@method_decorator(login_required, name='dispatch')
class EliminarContactoView(View):
    def post(self, request, contacto_id):
        # Obtener el contacto a través de su ID
        contacto = get_object_or_404(Contacto, id=contacto_id)
        user = request.user

        if user.is_superuser:
            # Si el usuario es superusuario, eliminamos el contacto directamente
            contacto.delete()
            messages.success(request, 'El elemento ha sido eliminado correctamente.')
            return redirect('contactos_admin')

        # Si no es superusuario, registramos la solicitud de eliminación sin modificar el modelo Contacto
        try:
            # Crear un cambio pendiente para marcar la eliminación
            PendingChange.objects.create(
                model_name='contacto',
                object_id=contacto.id,
                changes={'deleted': {'old': None, 'new': True}},  # Simulamos una eliminación
                submitted_by=user,
                action_type='delete'  # Acción de eliminación
            )
            messages.success(request, 'El cambio de eliminación se ha registrado para revisión.')
        except Exception as e:
            messages.error(request, f'Error al registrar el cambio: {str(e)}')

        return redirect('contactos_admin')

# RESUMEN