from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect


# Importe Modelos
from ..models import Pais, Matriz, Broker, Aseguradora, PendingChange

# ADMINISTRACION
@method_decorator(login_required, name='dispatch')
class MatrizView(View):
    def get(self, request, *args, **kwargs):
        
        # Obtener filtros desde los parámetros GET
        nombre_filtro = request.GET.get('nombre', '').strip()
        pais_filtro = request.GET.get('pais', '').strip()

        # Filtrar las matrices con base en los filtros
        matrices = Matriz.objects.all()

        if nombre_filtro:
            matrices = matrices.filter(nombre__icontains=nombre_filtro)

        if pais_filtro:
            matrices = matrices.filter(pais__id=pais_filtro)

        # Paginación
        matrices_paginados = Paginator(matrices, 30)
        page_number = request.GET.get("page")
        filter_pages = matrices_paginados.get_page(page_number)

        # Obtener la lista de países
        paises = Pais.objects.all()

        context = {
            'matrices': matrices,
            'pages': filter_pages,
            'paises': paises,
            'filtros': {
                'nombre': nombre_filtro,
                'pais': pais_filtro,
            }
        }
        return render(request, 'administracion/matrices_admin.html', context)

    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        nombre = request.POST.get('nuevo_nombre')
        pais_id = request.POST.get('nuevo_pais')
        activo = request.POST.get('nuevo_activo')
        if activo == "on":
            activo = True
        else:
            activo = False
        pais = get_object_or_404(Pais, id=pais_id)
        user = request.user

        # Crear una solicitud de creación pendiente
        changes = {
            'nombre': {'new': nombre},
            'pais_id': {'new': pais.id},
            'activo': {'new': activo},
        }
        if user.is_superuser:
            try:
                Matriz.objects.create(
                nombre = nombre,
                pais=pais,
                activo=activo,
                )
                messages.success(request, 'Se creó un nuevo elemento de forma exitosa.')
            except Exception as e:
                messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')
 
        else:
            try:
                PendingChange.objects.create(
                    model_name='matriz',
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
class EditarMatrizView(View):
    def post(self, request, matriz_id):
        matriz = get_object_or_404(Matriz, id=matriz_id)
        nombre = request.POST.get('editar_nombre')
        pais_id = request.POST.get('editar_pais')
        activo = 'editar_activo' in request.POST
        user = request.user

        # Si el usuario es superuser, aplicar los cambios directamente
        if user.is_superuser:
            if matriz.nombre != nombre:
                matriz.nombre = nombre
            if matriz.pais_id != int(pais_id):
                matriz.pais_id = pais_id
            if matriz.activo != activo:
                matriz.activo = activo

            matriz.save()  # Guardar los cambios directamente
            messages.success(request, 'Los cambios se han aplicado directamente.')
            return redirect('matrices_admin')

        # Para usuarios no superuser, registrar los cambios pendientes
        changes = {}
        if matriz.nombre != nombre:
            changes['nombre'] = {'old': matriz.nombre, 'new': nombre}
            matriz.nombre = nombre

        if matriz.pais_id != int(pais_id):
            changes['pais_id'] = {'old': matriz.pais_id, 'new': int(pais_id)}
            matriz.pais_id = pais_id

        if matriz.activo != activo:
            changes['activo'] = {'old': matriz.activo, 'new': activo}
            matriz.activo = activo

        if changes:
            try:
                PendingChange.objects.create(
                    model_name='matriz',
                    object_id=matriz.id,
                    changes=changes,
                    submitted_by=user,
                    action_type='edit'
                )
                messages.success(request, 'El cambio ha sido registrado para revisión.')
            except Exception as e:
                messages.error(request, f'Error al registrar el cambio: {str(e)}')
        else:
            messages.info(request, 'No se detectaron cambios.')

        return redirect('matrices_admin')


@method_decorator(login_required, name='dispatch')
class EliminarMatrizView(View):
    def post(self, request, matriz_id):
        matriz = get_object_or_404(Matriz, id=matriz_id)
        user = request.user

        if user.is_superuser:
            matriz.delete()
            messages.success(request, 'El elemento ha sido eliminado directamente.')
            return redirect('matrices_admin')

        changes = {
            'activo': {'old': matriz.activo, 'new': False},  # Simula desactivación
        }
        try:
            PendingChange.objects.create(
                model_name='matriz',
                object_id=matriz.id,
                changes=changes,
                submitted_by=user,
                action_type='delete'  # Indica que es una solicitud de eliminación
            )
            messages.success(request, 'El cambio de eliminación se ha registrado para revisión.')
        except Exception as e:
            messages.error(request, f'Error al registrar el cambio: {str(e)}')

        return redirect('matrices_admin')

# RESUMEN