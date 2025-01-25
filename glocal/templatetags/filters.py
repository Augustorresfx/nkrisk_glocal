from django import template
from django.apps import apps
import datetime
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def is_boolean(value):
    return isinstance(value, bool)

@register.filter
def boolean_to_text(value):
    if value is True:
        return "Sí"
    elif value is False:
        return "No"
    return value

@register.filter
def contains(value, substring):
    """Devuelve True si el substring está en value"""
    return substring in value

@register.filter
def get_foreign_key_name(value, field_name):
    """
    Dado un valor de clave foránea (ID) y el nombre del campo,
    intenta obtener el nombre del objeto relacionado.
    """
    print(f"Valor recibido: {value}, campo: {field_name}")
    
    if not value:
        return "N/A"  # Devuelve un valor por defecto si es None
    
    # Eliminar el sufijo '_id' del campo (si existe)
    field_name = field_name.rstrip('_id')
    print("nombre del campo:", field_name)

    try:
        # Verificar si el campo es 'user', y en ese caso usar el modelo User
        if field_name == 'user':
            related_object = User.objects.filter(pk=value).first()
            model = User  # No necesitamos acceder a `model` más tarde
        else:
            # Si no es el campo 'user', obtener el modelo dinámicamente
            model = apps.get_model('glocal', field_name)  # 'glocal' debe ser el nombre correcto de la app
            related_object = model.objects.filter(pk=value).first()

        print("Objeto encontrado:", related_object)
        
        # Devolver el nombre del objeto relacionado si se encuentra, o "N/A"
        return str(related_object) if related_object else "N/A"
    
    except Exception as e:
        print(f"Error al obtener el objeto: {e}")
        return "N/A"  # Si hay un error, retornar "N/A"


@register.filter
def get_years_to_current(value):
    return range(2020, datetime.datetime.now().year + 1)

@register.filter
def get_months(value):
    return range(1, 13)

@register.filter
def get_month_name(value):
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    try:
        return months[int(value) - 1]
    except (ValueError, IndexError):
        return value  # O manejar el error de alguna otra forma


@register.filter
def format_number(value):
    print(f"Valor recibido en el filtro: {value} (tipo: {type(value)})")  # Para depurar
    try:
        # Si el valor es una cadena, intenta convertirlo a float
        if isinstance(value, str):
            value = value.replace(',', '')  # Elimina comas si las hay
        value = float(value)
        return f"{value:,.2f}"  # Formatea el número
    except (ValueError, TypeError) as e:
        print(f"Error al formatear: {e}")  # Para depurar
        return value  # Retorna el valor original si hay un error

@register.filter
def format_date(value):
    try:
        value = value.strftime("%d/%m/%Y")
        return value
    except (ValueError, TypeError) as e:
        print("Error al formatear fecha: {e}")
        return value