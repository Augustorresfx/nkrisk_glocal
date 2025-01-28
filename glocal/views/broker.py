from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_list_or_404

# Importe Modelos
from ..models import Pais, Broker, PendingChange, Matriz, Contacto

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

        matrices = Matriz.objects.all()

        contactos = Contacto.objects.all()

        context = {
            'brokers': brokers,
            'pages': filter_pages,
            'paises': paises,
            'matrices': matrices,
            'contactos': contactos,
            'filtros': {
                'nombre': nombre_filtro,
                'pais': pais_filtro,
            }
        }
        return render(request, 'administracion/brokers_admin.html', context)
    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        nombre = request.POST.get('nuevo_nombre')
        logo = request.FILES.get('nuevo_logo')
        domicilio = request.POST.get('nuevo_domicilio')
        web = request.POST.get('nuevo_web')
        matriz_id = request.POST.get('nuevo_matriz')
        pais_id = request.POST.get('nuevo_pais')
        activo = request.POST.get('nuevo_activo')
        contactos_ids = request.POST.getlist('nuevo_contacto') 
        print(f"Domicilio recibido: {domicilio}")
        if activo == "on":
            activo = True
        else:
            activo = False
        # Obtener objetos relacionados
        pais = get_object_or_404(Pais, id=pais_id)
        matriz = get_object_or_404(Matriz, id=matriz_id)
        contactos = get_list_or_404(Contacto, id__in=contactos_ids)
        user = request.user
        # Crear una solicitud de creación pendiente
        changes = {
            'nombre': {'new': nombre},
            'logo': {'new': logo.name if logo else None},  # Guardar el nombre del archivo
            
            'domicilio_oficina': {'new': domicilio},
            'url_web': {'new': web},
            'pais_id': {'new': pais.id},
            'matriz_id': {'new': matriz.id},
            'activo': {'new': activo},
            'contactos': {'new': [c.id for c in contactos]},  # IDs de los contactos seleccionados
        }

        if user.is_superuser:
            try:
                # Crear el objeto Broker directamente si el usuario es superusuario
                broker = Broker.objects.create(
                    nombre=nombre,
                    logo=logo,
                    domicilio_oficina=domicilio,
                    url_web=web,
                    pais=pais,
                    matriz=matriz,
                    activo=activo,
                    modified_by = user,
                )
                broker.contactos.set(contactos)  # Relación muchos a muchos
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
    def post(self, request, broker_id):
        broker = get_object_or_404(Broker, id=broker_id)
        nombre = request.POST.get('editar_nombre')
        logo = request.FILES.get('editar_logo')  # Obtener el logo del archivo subido
        pais_id = request.POST.get('editar_pais')
        domicilio = request.POST.get('editar_domicilio')
        web = request.POST.get('editar_web')
        matriz_id = request.POST.get('editar_matriz')
        activo = 'editar_activo' in request.POST
        contactos_ids = request.POST.getlist('editar_contacto') 
        
        # Obtener objetos relacionados
        pais = get_object_or_404(Pais, id=pais_id)
        matriz = get_object_or_404(Matriz, id=matriz_id)
        contactos = get_list_or_404(Contacto, id__in=contactos_ids)
        user = request.user

        # Si el usuario es superuser, aplicar los cambios directamente
        if user.is_superuser:
            if broker.nombre != nombre:
                broker.nombre = nombre
            if logo:  # Solo actualizar si se sube un nuevo logo
                broker.logo = logo
            if broker.pais_id != int(pais_id):
                broker.pais_id = pais_id
            if broker.domicilio_oficina != domicilio:
                broker.domicilio_oficina = domicilio
            if broker.url_web != web:
                broker.url_web = web
            if broker.matriz_id != int(matriz_id):
                broker.matriz_id = matriz_id
            if broker.activo != activo:
                broker.activo = activo

            broker.contactos.set(contactos)  # Actualiza los contactos asociados al broker
            broker.modified_by = user  # Registrar quién realizó el cambio
            broker.save(track_changes=False)  # Evitar registrar PendingChange
            messages.success(request, 'Los cambios se han aplicado directamente.')
            return redirect('brokers_admin')
        else:
            # Para usuarios no superuser, registrar los cambios pendientes
            changes = {}
            if broker.nombre != nombre:
                changes['nombre'] = {'old': broker.nombre, 'new': nombre}
                broker.nombre = nombre 

            if logo:  # Solo registrar cambio si se sube un logo
                changes['logo'] = {
                    'old': broker.logo.url if broker.logo else None,
                    'new': logo.name
                }
                broker.logo = logo

            if broker.pais_id != int(pais_id):
                changes['pais_id'] = {'old': broker.pais_id, 'new': int(pais_id)}
                broker.pais_id = pais_id

            if broker.domicilio_oficina != domicilio:
                changes['domicilio'] = {'old': broker.domicilio_oficina, 'new': domicilio}
                broker.domicilio_oficina = domicilio 

            if broker.url_web != web:
                changes['web'] = {'old': broker.url_web, 'new': web}
                broker.url_web = web 

            if broker.matriz_id != int(matriz_id):
                changes['matriz_id'] = {'old': broker.matriz_id, 'new': int(matriz_id)}
                broker.matriz_id = matriz_id

            if broker.activo != activo:
                changes['activo'] = {'old': broker.activo, 'new': activo}
                broker.activo = activo

            # Comparar contactos, actualizando la relación ManyToMany
            if set(broker.contactos.all()) != set(contactos):
                changes['contactos'] = {
                    'old': [contacto.id for contacto in broker.contactos.all()],
                    'new': [contacto.id for contacto in contactos]
                }

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
            messages.success(request, 'El elemento ha sido eliminado directamente.')
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