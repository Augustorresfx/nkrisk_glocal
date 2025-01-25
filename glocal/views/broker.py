from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect


# Importe Modelos
from ..models import Pais, Broker, Aseguradora, PendingChange

# ADMINISTRACION
@method_decorator(login_required, name='dispatch')
class BrokerView(View):
    def get(self, request, *args, **kwargs):
        
        # Obtener filtros desde los parámetros GET
        nombre_filtro = request.GET.get('nombre', '').strip()
        pais_filtro = request.GET.get('pais', '').strip()

        # Filtrar los brokers con base en los filtros
        brokers = Broker.objects.all()

        if nombre_filtro:
            brokers = brokers.filter(nombre__icontains=nombre_filtro)

        if pais_filtro:
            brokers = brokers.filter(pais__id=pais_filtro)

        # Paginación
        brokers_paginados = Paginator(brokers, 30)
        page_number = request.GET.get("page")
        filter_pages = brokers_paginados.get_page(page_number)

        # Obtener la lista de países
        paises = Pais.objects.all()

        context = {
            'brokers': brokers,
            'pages': filter_pages,
            'paises': paises,
            'filtros': {
                'nombre': nombre_filtro,
                'pais': pais_filtro,
            }
        }
        return render(request, 'administracion/brokers_admin.html', context)

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
                Broker.objects.create(
                nombre = nombre,
                pais=pais,
                activo=activo,
                )
                messages.success(request, 'Se creó un nuevo elemento de forma exitosas.')
            except Exception as e:
                messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')
 
        else:
            try:
                PendingChange.objects.create(
                    model_name='broker',
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
class EditarBrokerView(View):
    def post(self, request, matriz_id):
        broker = get_object_or_404(Broker, id=matriz_id)
        nombre = request.POST.get('editar_nombre')
        pais_id = request.POST.get('editar_pais')
        activo = 'editar_activo' in request.POST
        user = request.user

        # Si el usuario es superuser, aplicar los cambios directamente
        if user.is_superuser:
            if broker.nombre != nombre:
                broker.nombre = nombre
            if broker.pais_id != int(pais_id):
                broker.pais_id = pais_id
            if broker.activo != activo:
                broker.activo = activo

            broker.save()  # Guardar los cambios directamente
            messages.success(request, 'Los cambios se han aplicado directamente.')
            return redirect('brokers_admin')

        # Para usuarios no superuser, registrar los cambios pendientes
        changes = {}
        if broker.nombre != nombre:
            changes['nombre'] = {'old': broker.nombre, 'new': nombre}
            broker.nombre = nombre

        if broker.pais_id != int(pais_id):
            changes['pais_id'] = {'old': broker.pais_id, 'new': int(pais_id)}
            broker.pais_id = pais_id

        if broker.activo != activo:
            changes['activo'] = {'old': broker.activo, 'new': activo}
            broker.activo = activo

        if changes:
            try:
                PendingChange.objects.create(
                    model_name='broker',
                    object_id=broker.id,
                    changes=changes,
                    submitted_by=user,
                    action_type='edit'
                )
                messages.success(request, 'El cambio ha sido registrado para revisión.')
            except Exception as e:
                messages.error(request, f'Error al registrar el cambio: {str(e)}')
        else:
            messages.info(request, 'No se detectaron cambios.')

        return redirect('brokers_admin')


@method_decorator(login_required, name='dispatch')
class EliminarBrokerView(View):
    def post(self, request, broker_id):
        broker = get_object_or_404(Broker, id=broker_id)
        user = request.user

        if user.is_superuser:
            broker.delete()
            messages.success(request, 'El broker ha sido eliminado directamente.')
            return redirect('brokers_admin')

        changes = {
            'activo': {'old': broker.activo, 'new': False},  # Simula desactivación
        }
        try:
            PendingChange.objects.create(
                model_name='broker',
                object_id=broker.id,
                changes=changes,
                submitted_by=user,
                action_type='delete'  # Indica que es una solicitud de eliminación
            )
            messages.success(request, 'El cambio de eliminación se ha registrado para revisión.')
        except Exception as e:
            messages.error(request, f'Error al registrar el cambio: {str(e)}')

        return redirect('brokers_admin')

# RESUMEN