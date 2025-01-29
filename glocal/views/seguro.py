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
from ..models import Pais, Broker, Aseguradora, PendingChange, Matriz, Contacto, Empresa, Seguro, SeguroAccidentePersonal, SeguroResponsabilidadCivil, SeguroVehiculo, Siniestro

# ADMINISTRACION
@method_decorator(login_required, name='dispatch')
class SeguroView(View):
    def get(self, request, *args, **kwargs):
        
        # Obtener filtros desde los parámetros GET
        nombre_filtro = request.GET.get('nombre', '').strip()
        pais_filtro = request.GET.get('pais', '').strip()

        # Filtrar con base en los filtros
        seguros = Seguro.objects.all()

        if nombre_filtro:
            seguros = seguros.filter(nombre__icontains=nombre_filtro)

        if pais_filtro:
            seguros = seguros.filter(pais__id=pais_filtro)

        # Paginación
        seguros_paginados = Paginator(seguros, 30)
        page_number = request.GET.get("page")
        filter_pages = seguros_paginados.get_page(page_number)

        # Obtener la lista de países
        paises = Pais.objects.all()

        matrices = Matriz.objects.all()

        contactos = Contacto.objects.all()

        context = {
            'seguros': seguros,
            'pages': filter_pages,
            'paises': paises,
            'matrices': matrices,
            'contactos': contactos,
            'filtros': {
                'nombre': nombre_filtro,
                'pais': pais_filtro,
            }
        }
        return render(request, 'administracion/seguros_admin.html', context)
    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        matriz_id = request.POST.get('nuevo_matriz')
        pais_id = request.POST.get('nuevo_pais')
        empresa_id = request.POST.get('nuevo_empresa')
        aseguradora_id = request.POST.get('nuevo_aseguradora')
        broker_id = request.POST.get('nuevo_broker')
        moneda = request.POST.get('nuevo_moneda')
        tipo_seguro = request.POST.get('nuevo_tipo_seguro')
        nro_poliza = request.POST.get('nuevo_nro_poliza')
        vigencia_desde = request.POST.get('nuevo_vigencia_desde')
        vigencia_hasta = request.POST.get('nuevo_vigencia_hasta')
        prima_neta_emitida = request.POST.get('nuevo_prima_neta_emitida')
        limite_asegurado = request.POST.get('nuevo_limite_asegurado')
        activo = request.POST.get('nuevo_activo')
        contactos_ids = request.POST.getlist('nuevo_contacto') 
         
        if activo == "on":
            activo = True
        else:
            activo = False
        
        # Obtener objetos relacionados
        pais = get_object_or_404(Pais, id=pais_id)
        matriz = get_object_or_404(Matriz, id=matriz_id)
        empresa = get_object_or_404(Empresa, id=empresa_id)
        aseguradora = get_object_or_404(Aseguradora, id=aseguradora_id)
        broker = get_object_or_404(Broker, id=broker_id)
        
        user = request.user
        # Crear una solicitud de creación pendiente
        changes = {
            'pais_id': {'new': pais.id},
            'matriz_id': {'new': matriz.id},
            'empresa_id': {'new': empresa.id},
            'aseguradora_id': {'new': aseguradora.id},
            'broker_id': {'new': broker.id},
            'moneda': {'new': moneda},
            'tipo_seguro': {'new': tipo_seguro},
            'nro_poliza': {'new': nro_poliza},
            'vigencia_desde': {'new': vigencia_desde},
            'vigencia_hasta': {'new': vigencia_hasta},
            'prima_neta_emitida': {'new': prima_neta_emitida},
            'limite_asegurado': {'new': limite_asegurado},
            'activo': {'new': activo},
        }

        if user.is_superuser:
            try:
                # Crear el objeto directamente si el usuario es superusuario
                seguro = Seguro.objects.create(
                    pais=pais,
                    matriz=matriz,
                    empresa=empresa,
                    broker=broker,
                    moneda=moneda,
                    aseguradora=aseguradora,
                    tipo_seguro=tipo_seguro,
                    nro_poliza=nro_poliza,
                    vigencia_desde=vigencia_desde,
                    vigencia_hasta=vigencia_hasta,
                    prima_neta_emitida=prima_neta_emitida,
                    limite_asegurado=limite_asegurado,
                    activo=activo,
                    modified_by = user,
                )
                messages.success(request, 'Se creó un nuevo elemento de forma exitosas.')
            except Exception as e:
                messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')
 
        else:
            try:
                PendingChange.objects.create(
                    model_name='seguro',
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
class EditarSeguroView(View):
    def post(self, request, seguro_id):
        seguro = get_object_or_404(Seguro, id=seguro_id)
        pais_id = request.POST.get('editar_pais')
        matriz_id = request.POST.get('editar_matriz')
        empresa_id = request.POST.get('editar_empresa')
        broker_id = request.POST.get('editar_broker')
        aseguradora_id = request.POST.get('editar_aseguradora')
        moneda = request.POST.get('editar_moneda')
        tipo_seguro = request.POST.get('editar_tipo_seguro')
        nro_poliza = request.POST.get('editar_nro_poliza')
        vigencia_desde = request.POST.get('editar_vigencia_desde')
        vigencia_hasta = request.POST.get('editar_vigencia_hasta')
        prima_neta_emitida = request.POST.get('editar_prima_neta_emitida')
        limite_asegurado = request.POST.get('editar_limite_asegurado')
        activo = 'editar_activo' in request.POST
        
        # Obtener objetos relacionados
        pais = get_object_or_404(Pais, id=pais_id)
        matriz = get_object_or_404(Matriz, id=matriz_id)
        empresa = get_object_or_404(Empresa, id=empresa_id)
        aseguradora = get_object_or_404(Aseguradora, id=aseguradora_id)
        broker = get_object_or_404(Broker, id=broker_id)
        
        user = request.user

        # Si el usuario es superuser, aplicar los cambios directamente
        if user.is_superuser:
            if seguro.pais_id != int(pais_id):
                seguro.pais_id = pais_id
            if seguro.matriz_id != int(matriz_id):
                seguro.matriz_id = matriz_id
            if seguro.empresa_id != int(empresa_id):
                seguro.empresa_id = empresa_id
            if seguro.broker_id != int(broker_id):
                seguro.broker_id = broker_id
            if seguro.aseguradora_id != int(aseguradora_id):
                seguro.aseguradora_id = aseguradora_id
            if seguro.moneda != moneda:
                seguro.moneda = moneda
            if seguro.tipo_seguro != tipo_seguro:
                seguro.tipo_seguro = tipo_seguro
            if seguro.nro_poliza != nro_poliza:
                seguro.nro_poliza = nro_poliza
            if seguro.vigencia_desde != vigencia_desde:
                seguro.vigencia_desde = vigencia_desde
            if seguro.vigencia_hasta != vigencia_hasta:
                seguro.vigencia_hasta = vigencia_hasta
            if seguro.prima_neta_emitida != prima_neta_emitida:
                seguro.prima_neta_emitida = prima_neta_emitida
            if seguro.limite_asegurado != limite_asegurado:
                seguro.limite_asegurado = limite_asegurado
            if seguro.activo != activo:
                seguro.activo = activo

            seguro.modified_by = user  # Registrar quién realizó el cambio
            seguro.save(track_changes=False)  # Evitar registrar PendingChange
            messages.success(request, 'Los cambios se han aplicado directamente.')
            return redirect('seguros_admin')
        else:
            # Para usuarios no superuser, registrar los cambios pendientes
            changes = {}
            if seguro.pais_id != int(pais_id):
                changes['pais_id'] = {'old': seguro.pais_id, 'new': int(pais_id)}
                seguro.pais_id = pais_id

            if seguro.matriz_id != int(matriz_id):
                changes['matriz_id'] = {'old': seguro.matriz_id, 'new': int(matriz_id)}
                seguro.matriz_id = matriz_id

            if seguro.empresa_id != int(empresa_id):
                changes['empresa_id'] = {'old': seguro.empresa_id, 'new': int(empresa_id)}
                seguro.empresa_id = empresa_id

            if seguro.broker_id != int(broker_id):
                changes['broker_id'] = {'old': seguro.broker_id, 'new': int(broker_id)}
                seguro.broker_id = broker_id

            if seguro.aseguradora_id != int(aseguradora_id):
                changes['aseguradora_id'] = {'old': seguro.aseguradora_id, 'new': int(aseguradora_id)}
                seguro.aseguradora_id = aseguradora_id

            if seguro.moneda != moneda:
                changes['moneda'] = {'old': seguro.moneda, 'new': moneda}
                seguro.moneda = moneda 
                
            if seguro.tipo_seguro != tipo_seguro:
                changes['tipo_seguro'] = {'old': seguro.tipo_seguro, 'new': tipo_seguro}
                seguro.tipo_seguro = tipo_seguro
                
            if seguro.nro_poliza != nro_poliza:
                changes['nro_poliza'] = {'old': seguro.nro_poliza, 'new': nro_poliza}
                seguro.nro_poliza = nro_poliza
                
            if seguro.vigencia_desde != vigencia_desde:
                changes['vigencia_desde'] = {'old': seguro.vigencia_desde, 'new': vigencia_desde}
                seguro.vigencia_desde = vigencia_desde

            if seguro.vigencia_hasta != vigencia_hasta:
                changes['vigencia_hasta'] = {'old': seguro.vigencia_hasta, 'new': vigencia_hasta}
                seguro.vigencia_hasta = vigencia_hasta
            
            if seguro.prima_neta_emitida != prima_neta_emitida:
                changes['prima_neta_emitida'] = {'old': seguro.prima_neta_emitida, 'new': prima_neta_emitida}
                seguro.prima_neta_emitida = prima_neta_emitida
                
            if seguro.limite_asegurado != limite_asegurado:
                changes['limite_asegurado'] = {'old': seguro.limite_asegurado, 'new': limite_asegurado}
                seguro.limite_asegurado = limite_asegurado

            if seguro.activo != activo:
                changes['activo'] = {'old': seguro.activo, 'new': activo}
                seguro.activo = activo

            if changes:
                try:
                    PendingChange.objects.create(
                        model_name='seguro',    
                        object_id=seguro.id,
                        changes=changes,
                        submitted_by=user,
                        action_type='edit'
                    )
                    messages.success(request, 'El cambio ha sido registrado para revisión.')
                except Exception as e:
                    messages.error(request, f'Error al registrar el cambio: {str(e)}')
            else:
                messages.info(request, 'No se detectaron cambios.')

        return redirect('seguros_admin')
    
@method_decorator(login_required, name='dispatch')
class EliminarSeguroView(View):
    def post(self, request, seguro_id):
        seguro = get_object_or_404(Seguro, id=seguro_id)
        user = request.user

        if user.is_superuser:
            seguro.delete()
            messages.success(request, 'El elemento ha sido eliminado directamente.')
            return redirect('seguros_admin')

        changes = {
            'activo': {'old': seguro.activo, 'new': False},  # Simula desactivación
        }
        try:
            PendingChange.objects.create(
                model_name='seguro',
                object_id=seguro.id,
                changes=changes,
                submitted_by=user,
                action_type='delete'  # Indica que es una solicitud de eliminación
            )
            messages.success(request, 'El cambio de eliminación se ha registrado para revisión.')
        except Exception as e:
            messages.error(request, f'Error al registrar el cambio: {str(e)}')

        return redirect('seguros_admin')

# RESUMEN