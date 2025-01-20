from datetime import datetime
import logging
from datetime import datetime

from .models import VehiculoFlota, TarifaFlota
from decimal import Decimal
from collections import defaultdict
from decimal import Decimal

from .models import Movimiento, VehiculoFlota, VehiculoInfoAuto, Flota, PrecioAnual, Localidad, TarifaFlota
import calendar
def get_tarifas():
    # Consultar todas las tarifas necesarias
    tarifas = TarifaFlota.objects.all()
    
    # Crear un diccionario para almacenar las tarifas
    tarifas_dict = defaultdict(dict)
    
    for tarifa in tarifas:
        zona = tarifa.zona
        tipo_vehiculo = tarifa.tipo_vehiculo
        antiguedad = tarifa.antiguedad
        tipo_cobertura = tarifa.tipo_cobertura
        tasa = tarifa.tasa
        prima_rc_anual = tarifa.prima_rc_anual
        
        # Almacenar la tarifa en el diccionario
        tarifas_dict[zona][(tipo_vehiculo, antiguedad, tipo_cobertura)] = {'tasa': tasa, 'prima_rc_anual': prima_rc_anual}
    
    return tarifas_dict

def convert_date_to_YYYY_MM_DD(fecha_str):
    try:
        # Intenta convertir la cadena a un objeto datetime
        fecha_nueva = datetime.strptime(fecha_str, "%Y/%m/%d")
        return fecha_nueva
    except ValueError:
        # Si hay un error en la conversión, imprime un mensaje y retorna None
        print(f"Error en la conversión de fecha: {fecha_str}")
        return None
    
def convert_date(fecha_str):
    try:
        # Intenta convertir la cadena a un objeto datetime
        fecha_nueva = datetime.strptime(fecha_str, "%d/%m/%Y")
        return fecha_nueva
    except ValueError:
        # Si hay un error en la conversión, imprime un mensaje y retorna None
        print(f"Error en la conversión de fecha: {fecha_str}")
        return None

def get_vehicle_type(tipo_vehiculo):
    tipo_vehiculo_a_categoria = {
    "SE": "AUTO",
    "SED": "AUTO",
    "CAB": "AUTO",
    "CUP": "AUTO",
    "PKA": "PICK UP CLASE A",
    "FUA": "PICK UP CLASE A",
    "WA4": "AUTO",
    "WAG": "AUTO",
    "RUR": "AUTO",
    "PKB": "PICK UP CLASE B",
    "PB4": "PICK UP CLASE B",
    "FUB": "PICK UP CLASE B",
    "JEE": "PICK UP 4X4",
    "MIV": "AUTO",
    "VAN": "AUTO",
    "MBU": "PICK UP CLASE B",
    "LIV": "PICK UP CLASE B",
    "PES": "PICK UP CLASE B",
    "SPE": "PICK UP CLASE B",
}
    return tipo_vehiculo_a_categoria.get(tipo_vehiculo, "Desconocido")

def convert_tipo_cobertura(tipo_cobertura):
    tipo_cobertura_a_formatear = {
        "TODO AUTO FCIA. IMP. $112.500.-": "COB TODO AUTO",
        "POLIZA CLASICA": "COB CLASICA",
        "TODO RIESGO CON FRANQUICIA $75.000": "COB TODO AUTO",
        "A - RESPONSABILIDAD CIVIL": "",
    }
    return tipo_cobertura_a_formatear.get(tipo_cobertura, "")
            
def handle_modificacion_datos(existing_vehicle, data, movimiento):
    existing_vehicle.marca = data['marca']
    existing_vehicle.modelo = data['modelo']
    existing_vehicle.descripcion = data['descripcion']
    existing_vehicle.patente = data['patente']
    existing_vehicle.anio = data['anio']
    existing_vehicle.okm = data['okm']
    existing_vehicle.localidad = data['localidad_vehiculo']
    existing_vehicle.zona = data['localidad'].zona
    existing_vehicle.suma_asegurada = data['precio']
    existing_vehicle.usuario_item = data['usuario_item']
    existing_vehicle.valor_actual = data['valor_actual']
    existing_vehicle.tipo_cobertura = data['tipo_de_cobertura']
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.uso_vehiculo = data['uso_vehiculo']
    existing_vehicle.tiene_accesorios = data['accesorios']
    if data['suma_aseg_acc'] != 0:
        existing_vehicle.suma_asegurada_accesorios = Decimal(data['suma_aseg_acc'])
    existing_vehicle.save()

def handle_aumento_suma_asegurada(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.tiene_accesorios = data['accesorios']
    existing_vehicle.suma_asegurada_accesorios = data['suma_aseg_acc']
    existing_vehicle.suma_asegurada = data['suma_aseg']
    existing_vehicle.prima_tecnica = existing_vehicle.prima_tecnica + data['prima_tecnica_vigente']
    existing_vehicle.prima_pza = existing_vehicle.prima_pza + data['prima_pza_vigente']
    existing_vehicle.premio_sin_iva = existing_vehicle.premio_sin_iva + data['premio_vigente_sin_iva']
    existing_vehicle.premio_con_iva = existing_vehicle.premio_con_iva + data['premio_vigente_con_iva']
    existing_vehicle.save()

def handle_cambio_cobertura(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.tipo_cobertura = data['tipo_de_cobertura']
    existing_vehicle.save()

def handle_baja_items(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.prima_tecnica = data['prima_tecnica_vigente']
    existing_vehicle.prima_pza = data['prima_pza_vigente']
    existing_vehicle.premio_sin_iva = data['premio_vigente_sin_iva']
    existing_vehicle.premio_con_iva = data['premio_vigente_con_iva']
    existing_vehicle.save()

def handle_renovacion_alta_items(data, movimiento):
    vehiculo = VehiculoFlota(
        created=data['created'],
        cod=data['codia'],
        flota = data['flota'],
        marca=data['marca'],
        modelo=data['modelo'],
        movimiento=movimiento,
        descripcion=data['descripcion'],
        tipo_vehiculo=data['tipo_vehiculo'],
        usuario_item=data['usuario_item'],
        patente=data['patente'],
        anio=data['anio'],
        okm=data['okm'],
        motor=data['motor'],
        chasis=data['chasis'],
        localidad=data['localidad_vehiculo'],
        zona=data['localidad'].zona,
        vigencia_desde=data['fecha_operacion'],
        vigencia_hasta=data['fecha_vigencia'],
        estado=data['estado'],
        uso_vehiculo=data['uso_vehiculo'],
        suma_asegurada=data['precio'],
        valor_actual=data['valor_actual'],
        tipo_cobertura=data['tipo_de_cobertura'],
        tasa=data['tasa'],
        prima_rc=data['prima_rc_anual'],
        tiene_accesorios=data['accesorios'],
        suma_asegurada_accesorios=data['suma_aseg_acc'],
        observacion=data['observacion'],
        prima_tecnica=data['prima_tecnica_vigente'],
        prima_pza=data['prima_pza_vigente'],
        premio_sin_iva=data['premio_vigente_sin_iva'],
        premio_con_iva=data['premio_vigente_con_iva'],
    )
    vehiculo.save()
    
def comparar_totales(workbook, flota_id, cliente):
    # Obtener la flota
    flota = Flota.objects.get(id=flota_id)
    # Obtener todos los movimientos vinculados a esa flota
    movimientos = Movimiento.objects.filter(flota=flota)
    
    sheet = workbook.active
    # Obtener todas las hojas en el workbook
    sheets = workbook.sheetnames
    # Encontrar el índice de la hoja activa
    current_index = sheets.index(sheet.title)

    # Mover a la siguiente hoja si existe
    if current_index < len(sheets) - 1:
        next_sheet = workbook[sheets[current_index + 2]]
        sheet = next_sheet  # Ahora 'sheet' es la tercer hoja

    total_prima_excel = 0
    total_premio_excel = 0
    total_prima_mov = 0
    total_premio_mov = 0

    for row_number, (orden, poliza, endoso, motivo_endoso, cliente_excel, aseguradora, riesgo, vig_op_desde_, vig_op_hasta, moneda, prima, premio, saldo, _,_,_,_,_,_,_,_) in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        row_values = sheet.cell(row=row_number, column=1).value
        if row_values is None:
            # Salir del bucle si la fila está vacía
            break
        try:
            # Buscar el movimiento correspondiente
            movimiento = movimientos.get(numero_orden=orden)
            print(movimiento.motivo_endoso)
            if motivo_endoso in ['ALTA DE ITEMS', 'AUMENTO DE SUMA ASEGURADA', 'RENOVACIÓN']:
                prima_diferencia = ((Decimal(prima) - movimiento.prima_tec_total) / Decimal(prima)) * 100 if movimiento.prima_tec_total else 0
                premio_diferencia = ((Decimal(premio) - movimiento.premio_con_iva_total) / Decimal(premio)) * 100 if movimiento.premio_con_iva_total else 0
                prima_num_diferencia = (Decimal(prima) - movimiento.prima_tec_total)
                premio_num_diferencia = (Decimal(premio) - movimiento.premio_con_iva_total)
            
            elif motivo_endoso == 'BAJA DE ITEMS':
                prima_diferencia = ((Decimal(prima) + (movimiento.prima_tec_total * -1)) / Decimal(prima)) * 100 if movimiento.prima_tec_total else 0
                premio_diferencia = ((Decimal(premio) + (movimiento.premio_con_iva_total * -1)) / Decimal(premio)) * 100 if movimiento.premio_con_iva_total else 0
                prima_num_diferencia = (Decimal(prima) - movimiento.prima_tec_total)
                premio_num_diferencia = (Decimal(premio) - movimiento.premio_con_iva_total)
            
            print(prima_diferencia)
            print(premio_diferencia)

            movimiento.prima_pza_porcentaje_diferencia = prima_diferencia
            movimiento.premio_con_iva_porcentaje_diferencia = premio_diferencia
            movimiento.save()

            total_prima_mov += movimiento.prima_pza_total
            total_premio_mov += movimiento.premio_con_iva_total

            # Obtener los vehículos afectados por el movimiento
            vehiculos = VehiculoFlota.history.filter(movimiento=movimiento).exclude(estado="Baja")
            num_vehiculos = vehiculos.count()

            # Calcular la diferencia porcentual y distribuirla entre los vehículos
            total_prima_excel += Decimal(prima)
            total_premio_excel += Decimal(premio)
            print("Premio diferencia num: ", premio_num_diferencia)
            if num_vehiculos > 0:
                prima_diferencia_a_distribuir = prima_num_diferencia / num_vehiculos
                premio_diferencia_a_distribuir = premio_num_diferencia / num_vehiculos
                print("Prima diferencia a distrubuir: ", prima_diferencia_a_distribuir)
                print("Premio diferencia a distrubuir: ", premio_diferencia_a_distribuir)
                print(num_vehiculos)
                for vehiculo in vehiculos:
                    vehiculo.prima_pza += prima_diferencia_a_distribuir
                    vehiculo.premio_con_iva += premio_diferencia_a_distribuir
                    vehiculo.save()

            # Añadir logs para verificar valores
            print(f"Orden: {orden} - Prima diferencia: {prima_diferencia}, Premio diferencia: {premio_diferencia}")

        except Movimiento.DoesNotExist:
            pass

    print("Prima total exc (comparar totales): ", total_prima_excel)
    print("Premio total exc (comparar totales): ", total_premio_excel)
    print("Prima total mov (comparar totales): ", total_prima_mov)
    print("Premio total mov (comparar totales): ", total_premio_mov)

    
    
def importar_datos_roemmers_saicf(workbook, flota_id, fuente_datos, cliente):
    # api_manager = ApiManager()
    created = datetime.now()
    lista_errores = []
    flota = Flota.objects.get(pk=flota_id)
   
    # Variables usadas para crear movimientos
    numero_orden_actual = None
    nuevo_movimiento = None
    prima_tec_total = 0
    prima_pza_total = 0
    premio_sin_iva_total = 0
    premio_con_iva_total = 0
    
    # if fuente_datos == 'info_auto':
    #     access_token = api_manager.get_valid_access_token()
    
    sheet = workbook.active
    
    for row_number, (nro_orden, cliente_excel, productor, aseguradora, riesgo, tipo_refacturacion, vinculante, poliza, endoso, motivo_endoso, fecha_operacion_str, fecha_vigencia_str, prima, premio, estado, vigencia_desde, vigencia_hasta, clau_ajuste, codia, marca, modelo, descripcion, usuario_item, patente, anio, okm, motor, chasis, localidad_vehiculo, uso_vehiculo, suma_aseg, valor_actual, tipo_cobertura, tasa_excel, prima_rc_excel, prima_total, accesorios, clau_ajuste_item, suma_aseg_acc, acreedor, usuario, observacion, fecha_alta_op_str, tasa, prima_rc_anual) in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        row_values = sheet.cell(row=row_number, column=1).value
        if row_values is None:
            # Salir del bucle si la fila está vacía
            break

        fecha_operacion = convert_date(fecha_operacion_str)
        fecha_vigencia = convert_date(fecha_vigencia_str)
        fecha_alta_op = fecha_alta_op_str.strftime("%Y-%m-%d")
        created = datetime.now()
        
        # Verificar si el número de orden cambió (crea un movimiento por c/nro de orden)
        if nro_orden != numero_orden_actual:
            # Guardar el movimiento anterior si existe
            if nuevo_movimiento:
                nuevo_movimiento.prima_tec_total = prima_tec_total
                nuevo_movimiento.prima_pza_total = prima_pza_total
                nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
                nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
                nuevo_movimiento.save()
                
            nuevo_movimiento = Movimiento(
                created=created,
                numero_endoso=endoso,
                motivo_endoso=motivo_endoso,
                flota=flota,
                numero_orden=nro_orden,
                vigencia_desde=fecha_operacion,
                vigencia_hasta=fecha_vigencia,
                fecha_alta_op=fecha_alta_op,
                prima_tec_total = prima_tec_total,
                prima_pza_total = prima_pza_total,
                premio_sin_iva_total = premio_sin_iva_total,
                premio_con_iva_total = premio_con_iva_total,
            )
            nuevo_movimiento.save()
            
            prima_tec_total = 0
            prima_pza_total = 0
            premio_sin_iva_total = 0
            premio_con_iva_total = 0

        # Actualizar el número de orden actual
        numero_orden_actual = nro_orden
        
        anio_vehiculo = int(anio)
        anio_actual = datetime.now().year
        
        # Formateo del tipo de cobertura
        tipo_de_cobertura = convert_tipo_cobertura(tipo_cobertura)
        print("Tipo de cobertura: ", tipo_de_cobertura)
        
        # Usar el precio de vehiculo que este en el Excel

        precio = Decimal(suma_aseg)
        # Consultar solo el tipo de vehículo
        vehiculo_info = VehiculoInfoAuto.objects.filter(codigo=codia).values_list('tipo_vehiculo', flat=True).first()
        tipo_vehiculo = get_vehicle_type(vehiculo_info)
        # Si el motivo es AUMENTO DE SUMA ASEGURADA buscar el vehiculo
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            vehiculo_anterior = VehiculoFlota.objects.filter(cod=codia, patente=patente).first()
            # Si la suma asegurada es distinta el precio será la diferencia entre sumas
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                precio = Decimal(suma_aseg) - vehiculo_anterior.suma_asegurada
            # Si la suma no es distinta, no hay diferencia, por lo tanto el precio será cero (y la tasa y la prima rc)
            else:
                precio = 0

        # # Usar los datos de vehiculo de info auto
        # elif fuente_datos == 'info_auto':
        #     precios_vehiculo = api_manager.get_vehicle_price(access_token, codia)
        #     tipo_vehiculo = api_manager.get_vehicle_features(access_token, codia)
        #     # Obtener el último elemento de la lista (correspondiente al último año)
        #     ultimo_ano = precios_vehiculo[-1]
            
        #     # Obtener el valor 'price' del último año
        #     precio = ultimo_ano['price']
        #     precio = None
            
        #     for precio_anual in precios_vehiculo:
        #         if precio_anual['year'] == anio_vehiculo:
        #             precio = precio_anual['price']
        #             break
                
        #     # Si no se encuentra el precio para el año asignar 0 como valor
        #     if precio is None:
        #         precio = 0
        # Usar los datos de vehiculos de la base de datos propia
        elif fuente_datos == 'base_datos':
            vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
            precios_vehiculo =  PrecioAnual.objects.filter(vehiculo=vehiculo)
            precio_anio = precios_vehiculo.get(anio=anio_vehiculo)
            precio = precio_anio.precio
            # Si no se encuentra el precio para el año asignar 0 como valor
            if precio is None:
                precio = 0
                
            tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)
                    
        # Calcula la antiguedad del vehiculo
        antiguedad_vehiculo = anio_actual - anio_vehiculo
        
        # Usa el año actual para calcular, si el año de la fecha de vigencia es distinto usa ese
        anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else fecha_vigencia.year
        
        # Buscar zona de riesgo mediante la localidad que este en el Excel
        localidades_encontradas = Localidad.objects.filter(nombre_localidad=localidad_vehiculo)

        # Si no se encuentra ninguna coincidencia por nombre de localidad, buscar por nombre de provincia
        if not localidades_encontradas.exists():
            localidades_encontradas = Localidad.objects.filter(nombre_provincia=localidad_vehiculo)
        if localidades_encontradas.exists():
            localidad = localidades_encontradas.first()
            print(f"Localidad encontrada: {localidad.nombre_localidad}")
            
            print(f"Zona encontrada: {localidad.zona}")
        else:
            error_message = f"No se encontró zona para la localidad: {localidad_vehiculo}"
            print(error_message)
            lista_errores.append(error_message)
        
        """  
        # Código para buscar la tarifa
        
        # Mapeo de antigüedad a categoría
        if antiguedad_vehiculo > 10:
            antiguedad_categoria = "MÁS DE 10"
        elif 6 <= antiguedad_vehiculo <= 10:
            antiguedad_categoria = "6 A 10"
        else:
            antiguedad_categoria = "5"
        
        print(motivo_endoso)

        # Buscar la tarifa en el diccionario
        tarifa_info = tarifas_dict.get(localidad.zona, {}).get((tipo_vehiculo, antiguedad_categoria, tipo_de_cobertura), None)

        # Verificar si se encontró la tarifa
        if tarifa_info:
            tasa = tarifa_info['tasa']
            prima_rc_anual = tarifa_info['prima_rc_anual']
        else:
            # Manejar el caso en el que no se encuentra la tarifa
            error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {localidad.zona}, {tipo_de_cobertura}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        
        print(tasa)
        print(tasa/1000)
        print("Rc:", prima_rc_anual)
        
        # Impuestos
        recargo_financiero = cliente.recargo_financiero
        imp_y_sellados = cliente.imp_y_sellados
        iibb = cliente.iibb
        iva = cliente.iva
        
        # Constantes
        CIEN = Decimal('100')
        MIL = Decimal('1000')
        COBERTURA_NACIONAL = 75000
        COBERTURA_IMPORTADO = 112500
        RECARGO_ADMINISTRATIVO = Decimal('10.5')
        IVA_RG_3337 = Decimal('3')
        DERECHO_EMISION = 2400
            
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            # Si el motivo es aumento de suma y es diferente a la anterior, usar la tasa anterior, la prima rc se cobra una única vez
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                tasa = vehiculo_anterior.tasa
                prima_rc_anual = 0
            # Si el motivo es aumento de suma y no es diferente a la anterior, no calcular nada (prima y premio = 0)
            else:
                prima_rc_anual = 0
                tasa = 0
                DERECHO_EMISION = 0
                COBERTURA_IMPORTADO = 0
                COBERTURA_NACIONAL = 0
        # CASO TRAILERS, AUTOELEVADORES Y TRACTORES QUE NO TIENEN SUMA ASEGURADA
        if suma_aseg == 0:
            precio = 0
            tasa = 0
        
        # Si el motivo es renovación o alta de items hay que tener en cuenta la suma aseg de los accesorios en el total
        if accesorios == 'SI' and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS' or motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            precio += suma_aseg_acc
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        precio = Decimal(str(precio))
        tasa = Decimal(str(tasa))
        prima_rc_anual = Decimal(str(prima_rc_anual))
        
        # Determinar si el año siguiente es bisiesto
        dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

        # Calcular los días de vigencia
        dias_vigencia = (fecha_vigencia - fecha_operacion).days
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        dias_vigencia = Decimal(str(dias_vigencia))
        dias_totales = Decimal(str(dias_totales))
        print(dias_vigencia)
        print(dias_totales)
        dias_calculado = dias_vigencia/dias_totales
        
        # Calcular prima tecnica
        prima_tecnica_anual = ((precio) * (tasa / MIL)) + prima_rc_anual
        
        # Prima prorrateada
        prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales

        # Sumar Derecho de emision
        prima_tecnica_anual += DERECHO_EMISION
        prima_tecnica_vigente += DERECHO_EMISION
        
        # Prima tecnica prorrateada x 10,5
        prima_tecnica_vigente_por_recargo_administrativo = (prima_tecnica_vigente * RECARGO_ADMINISTRATIVO) / CIEN
        
        # Prima poliza anual
        prima_tecnica_anual_por_recargo_administrativo = (prima_tecnica_anual * RECARGO_ADMINISTRATIVO) / CIEN
        prima_pza_anual = prima_tecnica_anual + prima_tecnica_anual_por_recargo_administrativo

        # Prima poliza prorrateada
        prima_pza_vigente = prima_tecnica_vigente + prima_tecnica_vigente_por_recargo_administrativo 
        
        # Determinar la cobertura según si la unidad es importada o no
        cobertura = COBERTURA_IMPORTADO if tipo_cobertura == "TODO AUTO FCIA. IMP. $112.500.-" else COBERTURA_NACIONAL

        # Base imponible
        prima_pza_vigente_por_recargo_financiero = prima_pza_vigente * recargo_financiero / CIEN
        base_imponible = prima_pza_vigente + prima_pza_vigente_por_recargo_financiero
        base_imponible_por_imp_y_sellados = base_imponible * imp_y_sellados / CIEN

        # Premio sin IVA ni IIBB
        premio_vigente_sin_iva = base_imponible + base_imponible_por_imp_y_sellados
        premio_vigente_por_iibb = premio_vigente_sin_iva * iibb / CIEN
        premio_vigente_por_iva = premio_vigente_sin_iva * iva / CIEN
        
        # Premio FINAL
        premio_vigente_con_iva = premio_vigente_sin_iva + premio_vigente_por_iibb + premio_vigente_por_iva
       
        # Sumar valores para el total del movimiento
        prima_tec_total += prima_tecnica_vigente
        prima_pza_total += prima_pza_vigente
        premio_sin_iva_total += premio_vigente_sin_iva
        premio_con_iva_total += premio_vigente_con_iva
        
        # Redondear valores
        prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
        prima_pza_vigente = round(prima_pza_vigente, 2)
        premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
        premio_vigente_con_iva = round(premio_vigente_con_iva, 2)
        
        print("Prima tecnica: ", prima_tecnica_vigente)
        
        print("Prima vigente: ", prima_pza_vigente)
        
        print("Premio sin iva: ", premio_vigente_sin_iva)
        
        print("Premio con iva: ", premio_vigente_con_iva)
        # Actualizar los valores en las columnas existentes
        """"
        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
        """    
        
        # Crear un diccionario para mapear los motivos de endoso a las funciones correspondientes
        motivo_endoso_handlers = {
            'MODIFIC. DATOS DEL VEHICULO AÑO  MODELO': handle_modificacion_datos,
            'MODIFICACION DE DATOS DEL ASEGURADO': handle_modificacion_datos,
            'MODIFICACION DE ITEMS': handle_modificacion_datos,
            'AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            ' AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            'CAMBIO DE COBERTURA': handle_cambio_cobertura,
            'BAJA DE ITEMS': handle_baja_items,
        }
        # Verificar si el vehículo ya existe
        existing_vehicle = VehiculoFlota.objects.filter(cod=codia, patente=patente, localidad=localidad_vehiculo).first()

        # Si existe, obtener el handler correspondiente al motivo de endoso y ejecutarlo
        if existing_vehicle and motivo_endoso in motivo_endoso_handlers:
            data = {
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'precio': precio,
                'usuario_item': usuario_item,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'suma_aseg': suma_aseg,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'observacion': observacion,
                'created': created,
                'codia': codia,
                'nuevo_movimiento': nuevo_movimiento,
                'tipo_vehiculo': vehiculo_info,
                'motor': motor,
                'chasis': chasis,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
            }
            motivo_endoso_handlers[motivo_endoso](existing_vehicle, data, nuevo_movimiento)
        
        elif not existing_vehicle and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
            # Si no existe, crear un nuevo vehículo
            print(type(flota), flota)
            handle_renovacion_alta_items({
                'created': created,
                'codia': codia,
                'flota': flota,
                'nuevo_movimiento': nuevo_movimiento,
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'tipo_vehiculo': vehiculo_info,
                'usuario_item': usuario_item,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'motor': motor,
                'chasis': chasis,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'precio': suma_aseg,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'observacion': observacion,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
            }, nuevo_movimiento)
    # Guardar la hoja de cálculo actualizada
    # output = BytesIO()
    # workbook.save(output)
    # output.seek(0)
    # Guardar el último movimiento después de salir del bucle
    if nuevo_movimiento:
        nuevo_movimiento.prima_tec_total = prima_tec_total
        nuevo_movimiento.prima_pza_total = prima_pza_total
        nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
        nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
        nuevo_movimiento.save()
    # Crear una respuesta HTTP con el archivo adjunto
    #response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'
    
    
    # ROFINA SAICF
    
def importar_datos_rofina_saicf(workbook, flota_id, fuente_datos, cliente):
    # api_manager = ApiManager()
    created = datetime.now()
    lista_errores = []
    flota = Flota.objects.get(pk=flota_id)
   
    # Variables usadas para crear movimientos
    numero_orden_actual = None
    nuevo_movimiento = None
    prima_tec_total = 0
    prima_pza_total = 0
    premio_sin_iva_total = 0
    premio_con_iva_total = 0
    
    # if fuente_datos == 'info_auto':
    #     access_token = api_manager.get_valid_access_token()
    
    sheet = workbook.active
    
    for row_number, (nro_orden, cliente_excel, productor, aseguradora, riesgo, tipo_refacturacion, poliza, endoso, motivo_endoso, estado, fecha_operacion_str, fecha_vigencia_str, clau_ajuste, nro_item, nro_item_cia, codia, marca, modelo, descripcion, usuario_item, patente, anio, okm, motor, chasis, localidad_vehiculo, uso_vehiculo, suma_aseg, valor_actual, tipo_cobertura, tasa_excel, prima_rc_excel, prima_total_excel, accesorios, clau_ajuste_item, suma_aseg_acc, acreedor, usuario, observacion, fecha_alta_op, dif_valor_veh, tasa, prima_rc_anual, dias_vigencia_excel, _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,) in enumerate(sheet.iter_rows(min_row=5, values_only=True), start=5):
        row_values = sheet.cell(row=row_number, column=1).value
        if row_values is None:
            # Salir del bucle si la fila está vacía
            break
        
        fecha_operacion = fecha_operacion_str
        fecha_vigencia = fecha_vigencia_str
        fecha_alta_op = fecha_alta_op
        created = datetime.now()
        # Verificar si el número de orden cambió (crea un movimiento por c/nro de orden)
        if nro_orden != numero_orden_actual:
            # Guardar el movimiento anterior si existe
            if nuevo_movimiento:
                nuevo_movimiento.prima_tec_total = prima_tec_total
                nuevo_movimiento.prima_pza_total = prima_pza_total
                nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
                nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
                nuevo_movimiento.save()
                
            nuevo_movimiento = Movimiento(
                created=created,
                numero_endoso=endoso,
                motivo_endoso=motivo_endoso,
                flota=flota,
                numero_orden=nro_orden,
                vigencia_desde=fecha_operacion,
                vigencia_hasta=fecha_vigencia,
                fecha_alta_op=fecha_alta_op,
                prima_tec_total = prima_tec_total,
                prima_pza_total = prima_pza_total,
                premio_sin_iva_total = premio_sin_iva_total,
                premio_con_iva_total = premio_con_iva_total,
            )
            nuevo_movimiento.save()
            
            prima_tec_total = 0
            prima_pza_total = 0
            premio_sin_iva_total = 0
            premio_con_iva_total = 0

        # Actualizar el número de orden actual
        numero_orden_actual = nro_orden
        
        anio_vehiculo = int(anio)
        anio_actual = datetime.now().year
        
        # Formateo del tipo de cobertura
        tipo_de_cobertura = convert_tipo_cobertura(tipo_cobertura)
        print("Tipo de cobertura: ", tipo_de_cobertura)
        
        # Usar el precio de vehiculo que este en el Excel

        precio = Decimal(suma_aseg)
        # Consultar solo el tipo de vehículo
        vehiculo_info = VehiculoInfoAuto.objects.filter(codigo=codia).values_list('tipo_vehiculo', flat=True).first()
        tipo_vehiculo = get_vehicle_type(vehiculo_info)
        # Si el motivo es AUMENTO DE SUMA ASEGURADA buscar el vehiculo
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            vehiculo_anterior = VehiculoFlota.objects.filter(cod=codia, patente=patente).first()
            # Si la suma asegurada es distinta el precio será la diferencia entre sumas
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                precio = Decimal(suma_aseg) - vehiculo_anterior.suma_asegurada
            # Si la suma no es distinta, no hay diferencia, por lo tanto el precio será cero (y la tasa y prima rc)
            else:
                precio = 0

        # # Usar los datos de vehiculo de info auto
        # elif fuente_datos == 'info_auto':
        #     precios_vehiculo = api_manager.get_vehicle_price(access_token, codia)
        #     tipo_vehiculo = api_manager.get_vehicle_features(access_token, codia)
        #     # Obtener el último elemento de la lista (correspondiente al último año)
        #     ultimo_ano = precios_vehiculo[-1]
            
        #     # Obtener el valor 'price' del último año
        #     precio = ultimo_ano['price']
        #     precio = None

        #     for precio_anual in precios_vehiculo:
        #         if precio_anual['year'] == anio_vehiculo:
        #             precio = precio_anual['price']
        #             break

        #     # Si no se encuentra el precio para el año asignar 0 como valor
        #     if precio is None:
        #         precio = 0
        # Usar los datos de vehiculos de la base de datos propia
        elif fuente_datos == 'base_datos':
            vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
            precios_vehiculo =  PrecioAnual.objects.filter(vehiculo=vehiculo)
            precio_anio = precios_vehiculo.get(anio=anio_vehiculo)
            precio = precio_anio.precio
            # Si no se encuentra el precio para el año asignar 0 como valor
            if precio is None:
                precio = 0
                
            tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)

        # Calcula la antiguedad del vehiculo
        antiguedad_vehiculo = anio_actual - anio_vehiculo

        # Usa el año actual para calcular, si el año de la fecha de vigencia es distinto usa ese
        anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else fecha_vigencia.year

        # Buscar zona de riesgo mediante la localidad que este en el Excel
        localidades_encontradas = Localidad.objects.filter(nombre_localidad=localidad_vehiculo)

        # Si no se encuentra ninguna coincidencia por nombre de localidad, buscar por nombre de provincia
        if not localidades_encontradas.exists():
            localidades_encontradas = Localidad.objects.filter(nombre_provincia=localidad_vehiculo)
        if localidades_encontradas.exists():
            localidad = localidades_encontradas.first()
            print(f"Localidad encontrada: {localidad.nombre_localidad}")
            
            print(f"Zona encontrada: {localidad.zona}")
        else:
            error_message = f"No se encontró zona para la localidad: {localidad_vehiculo}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        # Código para buscar la tarifa
        
        # Mapeo de antigüedad a categoría
        if antiguedad_vehiculo > 10:
            antiguedad_categoria = "MÁS DE 10"
        elif 6 <= antiguedad_vehiculo <= 10:
            antiguedad_categoria = "6 A 10"
        else:
            antiguedad_categoria = "5"
        
        print(motivo_endoso)

        # Buscar la tarifa en el diccionario
        tarifa_info = tarifas_dict.get(localidad.zona, {}).get((tipo_vehiculo, antiguedad_categoria, tipo_de_cobertura), None)

        # Verificar si se encontró la tarifa
        if tarifa_info:
            tasa = tarifa_info['tasa']
            prima_rc_anual = tarifa_info['prima_rc_anual']
        else:
            # Manejar el caso en el que no se encuentra la tarifa
            error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {localidad.zona}, {tipo_de_cobertura}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        
        print(tasa)
        print(tasa/1000)
        print("Rc:", prima_rc_anual)
        
        # Impuestos
        recargo_financiero = cliente.recargo_financiero
        imp_y_sellados = cliente.imp_y_sellados
        iibb = cliente.iibb
        iva = cliente.iva
        
        # Constantes
        CIEN = Decimal('100')
        MIL = Decimal('1000')
        COBERTURA_NACIONAL = 75000
        COBERTURA_IMPORTADO = 112500
        RECARGO_ADMINISTRATIVO = Decimal('10.5')
        IVA_RG_3337 = Decimal('3')
        DERECHO_EMISION = 2400
            
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            # Si el motivo es aumento de suma y es diferente a la anterior, usar la tasa anterior, la prima rc se cobra una única vez
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                tasa = vehiculo_anterior.tasa
                prima_rc_anual = 0
            # Si el motivo es aumento de suma y no es diferente a la anterior, no calcular nada (prima y premio = 0)
            else:
                prima_rc_anual = 0
                tasa = 0
                DERECHO_EMISION = 0
                COBERTURA_IMPORTADO = 0
                COBERTURA_NACIONAL = 0
        # CASO TRAILERS, AUTOELEVADORES Y TRACTORES QUE NO TIENEN SUMA ASEGURADA
        if suma_aseg == 0:
            precio = 0
            tasa = 0
        
        # Si el motivo es renovación o alta de items hay que tener en cuenta la suma aseg de los accesorios en el total
        if accesorios == 'SI' and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS' or motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            precio += suma_aseg_acc
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        precio = Decimal(str(precio))
        tasa = Decimal(str(tasa))
        prima_rc_anual = Decimal(str(prima_rc_anual))
        
        # Determinar si el año siguiente es bisiesto
        dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

        # Calcular los días de vigencia
        dias_vigencia = (fecha_vigencia - fecha_operacion).days
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        dias_vigencia = Decimal(str(dias_vigencia))
        dias_totales = Decimal(str(dias_totales))
        print(dias_vigencia)
        print(dias_totales)
        dias_calculado = dias_vigencia/dias_totales
        
        # Calcular prima tecnica
        prima_tecnica_anual = ((precio) * (tasa / MIL)) + prima_rc_anual
        
        # Prima prorrateada
        prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales

        # Sumar Derecho de emision
        prima_tecnica_anual += DERECHO_EMISION
        prima_tecnica_vigente += DERECHO_EMISION
        
        # Prima tecnica prorrateada x 10,5
        prima_tecnica_vigente_por_recargo_administrativo = (prima_tecnica_vigente * RECARGO_ADMINISTRATIVO) / CIEN
        
        # Prima poliza anual
        prima_tecnica_anual_por_recargo_administrativo = (prima_tecnica_anual * RECARGO_ADMINISTRATIVO) / CIEN
        prima_pza_anual = prima_tecnica_anual + prima_tecnica_anual_por_recargo_administrativo

        # Prima poliza prorrateada
        prima_pza_vigente = prima_tecnica_vigente + prima_tecnica_vigente_por_recargo_administrativo 
        
        # Determinar la cobertura según si la unidad es importada o no
        cobertura = COBERTURA_IMPORTADO if tipo_cobertura == "TODO AUTO FCIA. IMP. $112.500.-" else COBERTURA_NACIONAL

        # Base imponible
        prima_pza_vigente_por_recargo_financiero = prima_pza_vigente * recargo_financiero / CIEN
        base_imponible = prima_pza_vigente + prima_pza_vigente_por_recargo_financiero
        base_imponible_por_imp_y_sellados = base_imponible * imp_y_sellados / CIEN

        # Premio sin IVA ni IIBB
        premio_vigente_sin_iva = base_imponible + base_imponible_por_imp_y_sellados
        premio_vigente_por_iibb = premio_vigente_sin_iva * iibb / CIEN
        premio_vigente_por_iva = premio_vigente_sin_iva * iva / CIEN
        
        # Premio FINAL
        premio_vigente_con_iva = premio_vigente_sin_iva + premio_vigente_por_iibb + premio_vigente_por_iva
       
        # Sumar valores para el total del movimiento
        prima_tec_total += prima_tecnica_vigente
        prima_pza_total += prima_pza_vigente
        premio_sin_iva_total += premio_vigente_sin_iva
        premio_con_iva_total += premio_vigente_con_iva
        
        # Redondear valores
        prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
        prima_pza_vigente = round(prima_pza_vigente, 2)
        premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
        premio_vigente_con_iva = round(premio_vigente_con_iva, 2)
        
        print("Prima tecnica: ", prima_tecnica_vigente)
        
        print("Prima vigente: ", prima_pza_vigente)
        
        print("Premio sin iva: ", premio_vigente_sin_iva)
        
        print("Premio con iva: ", premio_vigente_con_iva)
        # Actualizar los valores en las columnas existentes
        """"
        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
        """    
        
        # Crear un diccionario para mapear los motivos de endoso a las funciones correspondientes
        motivo_endoso_handlers = {
            'MODIFIC. DATOS DEL VEHICULO AÑO  MODELO': handle_modificacion_datos,
            'MODIFICACION DE DATOS DEL ASEGURADO': handle_modificacion_datos,
            'MODIFICACION DE ITEMS': handle_modificacion_datos,
            'AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            ' AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            'CAMBIO DE COBERTURA': handle_cambio_cobertura,
            'BAJA DE ITEMS': handle_baja_items,
        }
        # Verificar si el vehículo ya existe
        existing_vehicle = VehiculoFlota.objects.filter(cod=codia, patente=patente, localidad=localidad_vehiculo).first()

        # Si existe, obtener el handler correspondiente al motivo de endoso y ejecutarlo
        if existing_vehicle and motivo_endoso in motivo_endoso_handlers:
            data = {
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'precio': precio,
                'usuario_item': usuario_item,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'suma_aseg': suma_aseg,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'observacion': observacion,
                'created': created,
                'codia': codia,
                'nuevo_movimiento': nuevo_movimiento,
                'tipo_vehiculo': vehiculo_info,
                'motor': motor,
                'chasis': chasis,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
            }
            motivo_endoso_handlers[motivo_endoso](existing_vehicle, data, nuevo_movimiento)
        
        elif not existing_vehicle and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
            # Si no existe, crear un nuevo vehículo
            print(type(flota), flota)
            handle_renovacion_alta_items({
                'created': created,
                'codia': codia,
                'flota': flota,
                'nuevo_movimiento': nuevo_movimiento,
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'tipo_vehiculo': vehiculo_info,
                'usuario_item': usuario_item,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'motor': motor,
                'chasis': chasis,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'precio': suma_aseg,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'observacion': observacion,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
            }, nuevo_movimiento)
    # Guardar la hoja de cálculo actualizada
    # output = BytesIO()
    # workbook.save(output)
    # output.seek(0)
    # Guardar el último movimiento después de salir del bucle
    if nuevo_movimiento:
        nuevo_movimiento.prima_tec_total = prima_tec_total
        nuevo_movimiento.prima_pza_total = prima_pza_total
        nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
        nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
        nuevo_movimiento.save()
    # Crear una respuesta HTTP con el archivo adjunto
    #response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'
    
# --- ROEMMERS ALBERTO GUILLERMO ---

def importar_datos_roemmers_alberto_guillermo(workbook, flota_id, fuente_datos, cliente):
    # api_manager = ApiManager()
    created = datetime.now()
    lista_errores = []
    flota = Flota.objects.get(pk=flota_id)
   
    # Variables usadas para crear movimientos
    numero_orden_actual = None
    nuevo_movimiento = None
    prima_tec_total = 0
    prima_pza_total = 0
    premio_sin_iva_total = 0
    premio_con_iva_total = 0
    
    # if fuente_datos == 'info_auto':
    #     access_token = api_manager.get_valid_access_token()
    
    sheet = workbook.active
    
    for row_number, (nro_orden, cliente_excel, productor, aseguradora, riesgo, tipo_refacturacion, poliza, endoso, motivo_endoso, estado, fecha_operacion_str, fecha_vigencia_str, clau_ajuste, codia, marca, modelo, descripcion, usuario_item, patente, anio, okm, motor, chasis, localidad_vehiculo, uso_vehiculo, suma_aseg, valor_actual, tipo_cobertura, tasa_excel, prima_rc_excel, prima_total_excel, accesorios, clau_ajuste_item, suma_aseg_acc, acreedor, usuario, observacion, fecha_alta_op, dif_valor_veh,  tasa, prima_rc_anual, dias_vigencia_excel, _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,) in enumerate(sheet.iter_rows(min_row=5, values_only=True), start=5):
        row_values = sheet.cell(row=row_number, column=1).value
        if row_values is None:
            # Salir del bucle si la fila está vacía
            break
        
        fecha_operacion = fecha_operacion_str
        fecha_vigencia = fecha_vigencia_str
        fecha_alta_op = fecha_alta_op
        created = datetime.now()
        # Verificar si el número de orden cambió (crea un movimiento por c/nro de orden)
        if nro_orden != numero_orden_actual:
            # Guardar el movimiento anterior si existe
            if nuevo_movimiento:
                nuevo_movimiento.prima_tec_total = prima_tec_total
                nuevo_movimiento.prima_pza_total = prima_pza_total
                nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
                nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
                nuevo_movimiento.save()
                
            nuevo_movimiento = Movimiento(
                created=created,
                numero_endoso=endoso,
                motivo_endoso=motivo_endoso,
                flota=flota,
                numero_orden=nro_orden,
                vigencia_desde=fecha_operacion,
                vigencia_hasta=fecha_vigencia,
                fecha_alta_op=fecha_alta_op,
                prima_tec_total = prima_tec_total,
                prima_pza_total = prima_pza_total,
                premio_sin_iva_total = premio_sin_iva_total,
                premio_con_iva_total = premio_con_iva_total,
            )
            nuevo_movimiento.save()
            
            prima_tec_total = 0
            prima_pza_total = 0
            premio_sin_iva_total = 0
            premio_con_iva_total = 0

        # Actualizar el número de orden actual
        numero_orden_actual = nro_orden
        
        anio_vehiculo = int(anio)
        anio_actual = datetime.now().year
        
        # Formateo del tipo de cobertura
        tipo_de_cobertura = convert_tipo_cobertura(tipo_cobertura)
        print("Tipo de cobertura: ", tipo_de_cobertura)
        
        # Usar el precio de vehiculo que este en el Excel

        precio = Decimal(suma_aseg)
        # Consultar solo el tipo de vehículo
        vehiculo_info = VehiculoInfoAuto.objects.filter(codigo=codia).values_list('tipo_vehiculo', flat=True).first()
        tipo_vehiculo = get_vehicle_type(vehiculo_info)
        # Si el motivo es AUMENTO DE SUMA ASEGURADA buscar el vehiculo
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            vehiculo_anterior = VehiculoFlota.objects.filter(cod=codia, patente=patente).first()
            # Si la suma asegurada es distinta el precio será la diferencia entre sumas
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                precio = Decimal(suma_aseg) - vehiculo_anterior.suma_asegurada
            # Si la suma no es distinta, no hay diferencia, por lo tanto el precio será cero (y la tasa y prima rc)
            else:
                precio = 0

        # # Usar los datos de vehiculo de info auto
        # elif fuente_datos == 'info_auto':
        #     precios_vehiculo = api_manager.get_vehicle_price(access_token, codia)
        #     tipo_vehiculo = api_manager.get_vehicle_features(access_token, codia)
        #     # Obtener el último elemento de la lista (correspondiente al último año)
        #     ultimo_ano = precios_vehiculo[-1]
            
        #     # Obtener el valor 'price' del último año
        #     precio = ultimo_ano['price']
        #     precio = None

        #     for precio_anual in precios_vehiculo:
        #         if precio_anual['year'] == anio_vehiculo:
        #             precio = precio_anual['price']
        #             break

        #     # Si no se encuentra el precio para el año asignar 0 como valor
        #     if precio is None:
        #         precio = 0
        # Usar los datos de vehiculos de la base de datos propia
        elif fuente_datos == 'base_datos':
            vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
            precios_vehiculo =  PrecioAnual.objects.filter(vehiculo=vehiculo)
            precio_anio = precios_vehiculo.get(anio=anio_vehiculo)
            precio = precio_anio.precio
            # Si no se encuentra el precio para el año asignar 0 como valor
            if precio is None:
                precio = 0
                
            tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)

        # Calcula la antiguedad del vehiculo
        antiguedad_vehiculo = anio_actual - anio_vehiculo

        # Usa el año actual para calcular, si el año de la fecha de vigencia es distinto usa ese
        anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else fecha_vigencia.year

        # Buscar zona de riesgo mediante la localidad que este en el Excel
        localidades_encontradas = Localidad.objects.filter(nombre_localidad=localidad_vehiculo)

        # Si no se encuentra ninguna coincidencia por nombre de localidad, buscar por nombre de provincia
        if not localidades_encontradas.exists():
            localidades_encontradas = Localidad.objects.filter(nombre_provincia=localidad_vehiculo)
        if localidades_encontradas.exists():
            localidad = localidades_encontradas.first()
            print(f"Localidad encontrada: {localidad.nombre_localidad}")
            
            print(f"Zona encontrada: {localidad.zona}")
        else:
            error_message = f"No se encontró zona para la localidad: {localidad_vehiculo}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        # Código para buscar la tarifa
        
        # Mapeo de antigüedad a categoría
        if antiguedad_vehiculo > 10:
            antiguedad_categoria = "MÁS DE 10"
        elif 6 <= antiguedad_vehiculo <= 10:
            antiguedad_categoria = "6 A 10"
        else:
            antiguedad_categoria = "5"
        
        print(motivo_endoso)

        # Buscar la tarifa en el diccionario
        tarifa_info = tarifas_dict.get(localidad.zona, {}).get((tipo_vehiculo, antiguedad_categoria, tipo_de_cobertura), None)

        # Verificar si se encontró la tarifa
        if tarifa_info:
            tasa = tarifa_info['tasa']
            prima_rc_anual = tarifa_info['prima_rc_anual']
        else:
            # Manejar el caso en el que no se encuentra la tarifa
            error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {localidad.zona}, {tipo_de_cobertura}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        
        print(tasa)
        print(tasa/1000)
        print("Rc:", prima_rc_anual)
        
        # Impuestos
        recargo_financiero = cliente.recargo_financiero
        imp_y_sellados = cliente.imp_y_sellados
        iibb = cliente.iibb
        iva = cliente.iva
        
        # Constantes
        CIEN = Decimal('100')
        MIL = Decimal('1000')
        COBERTURA_NACIONAL = 75000
        COBERTURA_IMPORTADO = 112500
        RECARGO_ADMINISTRATIVO = Decimal('10.5')
        IVA_RG_3337 = Decimal('3')
        DERECHO_EMISION = 2400
            
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            # Si el motivo es aumento de suma y es diferente a la anterior, usar la tasa anterior, la prima rc se cobra una única vez
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                tasa = vehiculo_anterior.tasa
                prima_rc_anual = 0
            # Si el motivo es aumento de suma y no es diferente a la anterior, no calcular nada (prima y premio = 0)
            else:
                prima_rc_anual = 0
                tasa = 0
                DERECHO_EMISION = 0
                COBERTURA_IMPORTADO = 0
                COBERTURA_NACIONAL = 0
        # CASO TRAILERS, AUTOELEVADORES Y TRACTORES QUE NO TIENEN SUMA ASEGURADA
        if suma_aseg == 0:
            precio = 0
            tasa = 0
        
        # Si el motivo es renovación o alta de items hay que tener en cuenta la suma aseg de los accesorios en el total
        if accesorios == 'SI' and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS' or motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            precio += suma_aseg_acc
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        precio = Decimal(str(precio))
        tasa = Decimal(str(tasa))
        prima_rc_anual = Decimal(str(prima_rc_anual))
        
        # Determinar si el año siguiente es bisiesto
        dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

        # Calcular los días de vigencia
        dias_vigencia = (fecha_vigencia - fecha_operacion).days
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        dias_vigencia = Decimal(str(dias_vigencia))
        dias_totales = Decimal(str(dias_totales))
        print(dias_vigencia)
        print(dias_totales)
        dias_calculado = dias_vigencia/dias_totales
        
        # Calcular prima tecnica
        prima_tecnica_anual = ((precio) * (tasa / MIL))+ prima_rc_anual
        
        # Prima prorrateada
        prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales

        # Sumar Derecho de emision
        prima_tecnica_anual += DERECHO_EMISION
        prima_tecnica_vigente += DERECHO_EMISION
        
        # Prima tecnica prorrateada x 10,5
        prima_tecnica_vigente_por_recargo_administrativo = (prima_tecnica_vigente * RECARGO_ADMINISTRATIVO) / CIEN
        
        # Prima poliza anual
        prima_tecnica_anual_por_recargo_administrativo = (prima_tecnica_anual * RECARGO_ADMINISTRATIVO) / CIEN
        prima_pza_anual = prima_tecnica_anual + prima_tecnica_anual_por_recargo_administrativo

        # Prima poliza prorrateada
        prima_pza_vigente = prima_tecnica_vigente + prima_tecnica_vigente_por_recargo_administrativo 
        
        # Determinar la cobertura según si la unidad es importada o no
        cobertura = COBERTURA_IMPORTADO if tipo_cobertura == "TODO AUTO FCIA. IMP. $112.500.-" else COBERTURA_NACIONAL

        # Base imponible
        prima_pza_vigente_por_recargo_financiero = prima_pza_vigente * recargo_financiero / CIEN
        base_imponible = prima_pza_vigente + prima_pza_vigente_por_recargo_financiero
        base_imponible_por_imp_y_sellados = base_imponible * imp_y_sellados / CIEN

        # Premio sin IVA ni IIBB
        premio_vigente_sin_iva = base_imponible + base_imponible_por_imp_y_sellados
        
        # Endoso 3 y 4 NO se facturaron con IIBB
        if (endoso == 3 or endoso == 4):
            iibb = 0
            
        # Endoso 5 y 6 facturaron 4% de IIBB
        if (endoso == 5 or endoso == 6):
            iibb = 4
            
        premio_vigente_por_iibb = premio_vigente_sin_iva * iibb / CIEN
        premio_vigente_por_iva = premio_vigente_sin_iva * iva / CIEN
        
        # Premio FINAL
        premio_vigente_con_iva = premio_vigente_sin_iva + premio_vigente_por_iibb + premio_vigente_por_iva
       
        # Sumar valores para el total del movimiento
        prima_tec_total += prima_tecnica_vigente
        prima_pza_total += prima_pza_vigente
        premio_sin_iva_total += premio_vigente_sin_iva
        premio_con_iva_total += premio_vigente_con_iva
        
        # Redondear valores
        prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
        prima_pza_vigente = round(prima_pza_vigente, 2)
        premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
        premio_vigente_con_iva = round(premio_vigente_con_iva, 2)
        
        print("Prima tecnica: ", prima_tecnica_vigente)
        
        print("Prima vigente: ", prima_pza_vigente)
        
        print("Premio sin iva: ", premio_vigente_sin_iva)
        
        print("Premio con iva: ", premio_vigente_con_iva)
        # Actualizar los valores en las columnas existentes
        """"
        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
        """    
        
        # Crear un diccionario para mapear los motivos de endoso a las funciones correspondientes
        motivo_endoso_handlers = {
            'MODIFIC. DATOS DEL VEHICULO AÑO  MODELO': handle_modificacion_datos,
            'MODIFICACION DE DATOS DEL ASEGURADO': handle_modificacion_datos,
            'MODIFICACION DE ITEMS': handle_modificacion_datos,
            'AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            ' AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            'CAMBIO DE COBERTURA': handle_cambio_cobertura,
            'BAJA DE ITEMS': handle_baja_items,
        }
        # Verificar si el vehículo ya existe
        existing_vehicle = VehiculoFlota.objects.filter(cod=codia, patente=patente, localidad=localidad_vehiculo).first()

        # Si existe, obtener el handler correspondiente al motivo de endoso y ejecutarlo
        if existing_vehicle and motivo_endoso in motivo_endoso_handlers:
            data = {
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'precio': precio,
                'usuario_item': usuario_item,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'suma_aseg': suma_aseg,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'observacion': observacion,
                'created': created,
                'codia': codia,
                'nuevo_movimiento': nuevo_movimiento,
                'tipo_vehiculo': vehiculo_info,
                'motor': motor,
                'chasis': chasis,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
            }
            motivo_endoso_handlers[motivo_endoso](existing_vehicle, data, nuevo_movimiento)
        
        elif not existing_vehicle and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
            # Si no existe, crear un nuevo vehículo
            print(type(flota), flota)
            handle_renovacion_alta_items({
                'created': created,
                'codia': codia,
                'flota': flota,
                'nuevo_movimiento': nuevo_movimiento,
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'tipo_vehiculo': vehiculo_info,
                'usuario_item': usuario_item,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'motor': motor,
                'chasis': chasis,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'precio': suma_aseg,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'observacion': observacion,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
            }, nuevo_movimiento)
    # Guardar la hoja de cálculo actualizada
    # output = BytesIO()
    # workbook.save(output)
    # output.seek(0)
    # Guardar el último movimiento después de salir del bucle
    if nuevo_movimiento:
        nuevo_movimiento.prima_tec_total = prima_tec_total
        nuevo_movimiento.prima_pza_total = prima_pza_total
        nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
        nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
        nuevo_movimiento.save()
    # Crear una respuesta HTTP con el archivo adjunto
    #response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'


    
# --- GANADERA SANTA ISABEL ---

def importar_datos_ganadera_santa_isabel(workbook, flota_id, fuente_datos, cliente):
    # api_manager = ApiManager()
    created = datetime.now()
    lista_errores = []
    flota = Flota.objects.get(pk=flota_id)
    
    # Variables usadas para crear movimientos
    numero_orden_actual = None
    nuevo_movimiento = None
    prima_tec_total = 0
    prima_pza_total = 0
    premio_sin_iva_total = 0
    premio_con_iva_total = 0
    
    
    
    # if fuente_datos == 'info_auto':
    #     access_token = api_manager.get_valid_access_token()
    
    sheet = workbook.active
    
    for row_number, (nro_orden, cliente_excel, productor, aseguradora, riesgo, tipo_refacturacion, poliza, endoso, motivo_endoso, estado, fecha_operacion_str, fecha_vigencia_str, clau_ajuste, nro_item, nro_item_cia, codia, marca, modelo, descripcion, usuario_item, patente, anio, okm, motor, chasis, localidad_vehiculo, uso_vehiculo, suma_aseg, valor_actual, tipo_cobertura, tasa_excel, prima_rc_anual_excel, prima_total, accesorios, clau_ajuste_item, suma_aseg_acc, acreedor, usuario, observacion, fecha_alta_op_str, dif_valor_veh, tasa, prima_rc_anual, dias_vigencia_excel, _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,) in enumerate(sheet.iter_rows(min_row=5, values_only=True), start=5):
        row_values = sheet.cell(row=row_number, column=1).value
        if row_values is None:
            # Salir del bucle si la fila está vacía
            break
        
        fecha_operacion = fecha_operacion_str
        fecha_vigencia = fecha_vigencia_str
        fecha_alta_op = fecha_alta_op_str
        created = datetime.now()
        # Verificar si el número de orden cambió (crea un movimiento por c/nro de orden)
        if nro_orden != numero_orden_actual:
            # Guardar el movimiento anterior si existe
            if nuevo_movimiento:
                nuevo_movimiento.prima_tec_total = prima_tec_total
                nuevo_movimiento.prima_pza_total = prima_pza_total
                nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
                nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
                nuevo_movimiento.save()
                
            nuevo_movimiento = Movimiento(
                created=created,
                numero_endoso=endoso,
                motivo_endoso=motivo_endoso,
                flota=flota,
                numero_orden=nro_orden,
                vigencia_desde=fecha_operacion,
                vigencia_hasta=fecha_vigencia,
                fecha_alta_op=fecha_alta_op,
                prima_tec_total = prima_tec_total,
                prima_pza_total = prima_pza_total,
                premio_sin_iva_total = premio_sin_iva_total,
                premio_con_iva_total = premio_con_iva_total,
            )
            nuevo_movimiento.save()
            
            prima_tec_total = 0
            prima_pza_total = 0
            premio_sin_iva_total = 0
            premio_con_iva_total = 0

        # Actualizar el número de orden actual
        numero_orden_actual = nro_orden
        
        anio_vehiculo = int(anio)
        anio_actual = datetime.now().year
        
        # Formateo del tipo de cobertura
        tipo_de_cobertura = convert_tipo_cobertura(tipo_cobertura)
        print("Tipo de cobertura: ", tipo_de_cobertura)
        
        # Usar el precio de vehiculo que este en el Excel
    
        precio = Decimal(suma_aseg)
        # Consultar solo el tipo de vehículo
        vehiculo_info = VehiculoInfoAuto.objects.filter(codigo=codia).values_list('tipo_vehiculo', flat=True).first()
        tipo_vehiculo = get_vehicle_type(vehiculo_info)
        # Si el motivo es AUMENTO DE SUMA ASEGURADA buscar el vehiculo
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            vehiculo_anterior = VehiculoFlota.objects.filter(cod=codia, patente=patente).first()
            # Si la suma asegurada es distinta el precio será la diferencia entre sumas
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                precio = Decimal(suma_aseg) - vehiculo_anterior.suma_asegurada
            # Si la suma no es distinta, no hay diferencia, por lo tanto el precio será cero (y la tasa y la prima rc)
            else:
                precio = 0

        # # Usar los datos de vehiculo de info auto
        # elif fuente_datos == 'info_auto':
        #     precios_vehiculo = api_manager.get_vehicle_price(access_token, codia)
        #     tipo_vehiculo = api_manager.get_vehicle_features(access_token, codia)
        #     # Obtener el último elemento de la lista (correspondiente al último año)
        #     ultimo_ano = precios_vehiculo[-1]
            
        #     # Obtener el valor 'price' del último año
        #     precio = ultimo_ano['price']
        #     precio = None
            
        #     for precio_anual in precios_vehiculo:
        #         if precio_anual['year'] == anio_vehiculo:
        #             precio = precio_anual['price']
        #             break
                
        #     # Si no se encuentra el precio para el año asignar 0 como valor
        #     if precio is None:
        #         precio = 0
        # Usar los datos de vehiculos de la base de datos propia
        elif fuente_datos == 'base_datos':
            vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
            precios_vehiculo =  PrecioAnual.objects.filter(vehiculo=vehiculo)
            precio_anio = precios_vehiculo.get(anio=anio_vehiculo)
            precio = precio_anio.precio
            # Si no se encuentra el precio para el año asignar 0 como valor
            if precio is None:
                precio = 0
                
            tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)
                    
        # Calcula la antiguedad del vehiculo
        antiguedad_vehiculo = anio_actual - anio_vehiculo
        
        # Usa el año actual para calcular, si el año de la fecha de vigencia es distinto usa ese
        anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else fecha_vigencia.year
        
        # Buscar zona de riesgo mediante la localidad que este en el Excel
        localidades_encontradas = Localidad.objects.filter(nombre_localidad=localidad_vehiculo)

        # Si no se encuentra ninguna coincidencia por nombre de localidad, buscar por nombre de provincia
        if not localidades_encontradas.exists():
            localidades_encontradas = Localidad.objects.filter(nombre_provincia=localidad_vehiculo)
        if localidades_encontradas.exists():
            localidad = localidades_encontradas.first()
            print(f"Localidad encontrada: {localidad.nombre_localidad}")
            
            print(f"Zona encontrada: {localidad.zona}")
        else:
            error_message = f"No se encontró zona para la localidad: {localidad_vehiculo}"
            print(error_message)
            lista_errores.append(error_message)
        
        """  
        # Código para buscar la tarifa
        
        # Mapeo de antigüedad a categoría
        if antiguedad_vehiculo > 10:
            antiguedad_categoria = "MÁS DE 10"
        elif 6 <= antiguedad_vehiculo <= 10:
            antiguedad_categoria = "6 A 10"
        else:
            antiguedad_categoria = "5"
        
        print(motivo_endoso)

        # Buscar la tarifa en el diccionario
        tarifa_info = tarifas_dict.get(localidad.zona, {}).get((tipo_vehiculo, antiguedad_categoria, tipo_de_cobertura), None)

        # Verificar si se encontró la tarifa
        if tarifa_info:
            tasa = tarifa_info['tasa']
            prima_rc_anual = tarifa_info['prima_rc_anual']
        else:
            # Manejar el caso en el que no se encuentra la tarifa
            error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {localidad.zona}, {tipo_de_cobertura}"
            print(error_message)
            lista_errores.append(error_message)
        
        """
        
        print(tasa)
        print(tasa/1000)
        print("Rc:", prima_rc_anual)
        
        # Impuestos
        recargo_financiero = cliente.recargo_financiero
        imp_y_sellados = cliente.imp_y_sellados
        iibb = cliente.iibb
        iva = cliente.iva
        
        # Constantes
        CIEN = Decimal('100')
        MIL = Decimal('1000')
        COBERTURA_NACIONAL = 75000
        COBERTURA_IMPORTADO = 112500
        RECARGO_ADMINISTRATIVO = Decimal('10.5')
        IVA_RG_3337 = Decimal('3')
        DERECHO_EMISION = 2400
            
        if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            # Si el motivo es aumento de suma y es diferente a la anterior, usar la tasa anterior, la prima rc se cobra una única vez
            if suma_aseg != vehiculo_anterior.suma_asegurada:
                tasa = vehiculo_anterior.tasa
                prima_rc_anual = 0
            # Si el motivo es aumento de suma y no es diferente a la anterior, no calcular nada (prima y premio = 0)
            else:
                prima_rc_anual = 0
                tasa = 0
                DERECHO_EMISION = 0
                COBERTURA_IMPORTADO = 0
                COBERTURA_NACIONAL = 0
        # CASO TRAILERS, AUTOELEVADORES Y TRACTORES QUE NO TIENEN SUMA ASEGURADA
        if suma_aseg == 0:
            precio = 0
            tasa = 0
        
        # Si el motivo es renovación o alta de items hay que tener en cuenta la suma aseg de los accesorios en el total
        if accesorios == 'SI' and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS' or motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
            precio += suma_aseg_acc
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        precio = Decimal(str(precio))
        tasa = Decimal(str(tasa))
        prima_rc_anual = Decimal(str(prima_rc_anual))
        
        # Determinar si el año siguiente es bisiesto
        dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

        # Calcular los días de vigencia
        dias_vigencia = (fecha_vigencia - fecha_operacion).days
        
        # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
        dias_vigencia = Decimal(str(dias_vigencia))
        dias_totales = Decimal(str(dias_totales))
        print(dias_vigencia)
        print(dias_totales)
        dias_calculado = dias_vigencia/dias_totales
        
        # Calcular prima tecnica
        prima_tecnica_anual = ((precio) * (tasa / MIL)) + prima_rc_anual
        
        # Prima prorrateada
        prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales

        # Sumar Derecho de emision
        prima_tecnica_anual += DERECHO_EMISION
        prima_tecnica_vigente += DERECHO_EMISION
        
        # Prima tecnica prorrateada x 10,5
        prima_tecnica_vigente_por_recargo_administrativo = (prima_tecnica_vigente * RECARGO_ADMINISTRATIVO) / CIEN
        
        # Prima poliza anual
        prima_tecnica_anual_por_recargo_administrativo = (prima_tecnica_anual * RECARGO_ADMINISTRATIVO) / CIEN
        prima_pza_anual = prima_tecnica_anual + prima_tecnica_anual_por_recargo_administrativo

        # Prima poliza prorrateada
        prima_pza_vigente = prima_tecnica_vigente + prima_tecnica_vigente_por_recargo_administrativo 
        
        # Determinar la cobertura según si la unidad es importada o no
        cobertura = COBERTURA_IMPORTADO if tipo_cobertura == "TODO AUTO FCIA. IMP. $112.500.-" else COBERTURA_NACIONAL

        # Base imponible
        prima_pza_vigente_por_recargo_financiero = prima_pza_vigente * recargo_financiero / CIEN
        base_imponible = prima_pza_vigente + prima_pza_vigente_por_recargo_financiero
        base_imponible_por_imp_y_sellados = base_imponible * imp_y_sellados / CIEN

        # Premio sin IVA ni IIBB
        premio_vigente_sin_iva = base_imponible + base_imponible_por_imp_y_sellados
        premio_vigente_por_iibb = premio_vigente_sin_iva * iibb / CIEN
        premio_vigente_por_iva = premio_vigente_sin_iva * iva / CIEN
        
        # Premio FINAL
        premio_vigente_con_iva = premio_vigente_sin_iva + premio_vigente_por_iibb + premio_vigente_por_iva
       
        # Sumar valores para el total del movimiento
        prima_tec_total += prima_tecnica_vigente
        prima_pza_total += prima_pza_vigente
        premio_sin_iva_total += premio_vigente_sin_iva
        premio_con_iva_total += premio_vigente_con_iva
        
        # Redondear valores
        prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
        prima_pza_vigente = round(prima_pza_vigente, 2)
        premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
        premio_vigente_con_iva = round(premio_vigente_con_iva, 2)
        
        print("Prima tecnica: ", prima_tecnica_vigente)
        
        print("Prima vigente: ", prima_pza_vigente)
        
        print("Premio sin iva: ", premio_vigente_sin_iva)
        
        print("Premio con iva: ", premio_vigente_con_iva)
        # Actualizar los valores en las columnas existentes
        """"
        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
        """    
        
        # Crear un diccionario para mapear los motivos de endoso a las funciones correspondientes
        motivo_endoso_handlers = {
            'MODIFIC. DATOS DEL VEHICULO AÑO  MODELO': handle_modificacion_datos,
            'MODIFICACION DE DATOS DEL ASEGURADO': handle_modificacion_datos,
            'MODIFICACION DE ITEMS': handle_modificacion_datos,
            'AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            ' AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
            'CAMBIO DE COBERTURA': handle_cambio_cobertura,
            'BAJA DE ITEMS': handle_baja_items,
        }
        # Verificar si el vehículo ya existe
        existing_vehicle = VehiculoFlota.objects.filter(cod=codia, patente=patente, localidad=localidad_vehiculo).first()

        # Si existe, obtener el handler correspondiente al motivo de endoso y ejecutarlo
        if existing_vehicle and motivo_endoso in motivo_endoso_handlers:
            data = {
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'precio': precio,
                'usuario_item': usuario_item,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'suma_aseg': suma_aseg,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'observacion': observacion,
                'created': created,
                'codia': codia,
                'nuevo_movimiento': nuevo_movimiento,
                'tipo_vehiculo': vehiculo_info,
                'motor': motor,
                'chasis': chasis,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
            }
            motivo_endoso_handlers[motivo_endoso](existing_vehicle, data, nuevo_movimiento)
        
        elif not existing_vehicle and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
            # Si no existe, crear un nuevo vehículo
            print(type(flota), flota)
            handle_renovacion_alta_items({
                'created': created,
                'codia': codia,
                'flota': flota,
                'nuevo_movimiento': nuevo_movimiento,
                'marca': marca,
                'modelo': modelo,
                'descripcion': descripcion,
                'tipo_vehiculo': vehiculo_info,
                'usuario_item': usuario_item,
                'patente': patente,
                'anio': anio,
                'okm': okm,
                'motor': motor,
                'chasis': chasis,
                'localidad_vehiculo': localidad_vehiculo,
                'localidad': localidad,
                'fecha_operacion': fecha_operacion,
                'fecha_vigencia': fecha_vigencia,
                'estado': estado,
                'uso_vehiculo': uso_vehiculo,
                'precio': suma_aseg,
                'valor_actual': valor_actual,
                'tipo_de_cobertura': tipo_cobertura,
                'tasa': tasa,
                'prima_rc_anual': prima_rc_anual,
                'accesorios': accesorios,
                'suma_aseg_acc': suma_aseg_acc,
                'observacion': observacion,
                'prima_tecnica_vigente': prima_tecnica_vigente,
                'prima_pza_vigente': prima_pza_vigente,
                'premio_vigente_sin_iva': premio_vigente_sin_iva,
                'premio_vigente_con_iva': premio_vigente_con_iva,
            }, nuevo_movimiento)
    # Guardar la hoja de cálculo actualizada
    # output = BytesIO()
    # workbook.save(output)
    # output.seek(0)
    # Guardar el último movimiento después de salir del bucle
    if nuevo_movimiento:
        nuevo_movimiento.prima_tec_total = prima_tec_total
        nuevo_movimiento.prima_pza_total = prima_pza_total
        nuevo_movimiento.premio_sin_iva_total = premio_sin_iva_total
        nuevo_movimiento.premio_con_iva_total = premio_con_iva_total
        nuevo_movimiento.save()
    # Crear una respuesta HTTP con el archivo adjunto
    #response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'
    
    