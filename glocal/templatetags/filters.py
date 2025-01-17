from django import template
from django.apps import apps

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
    
    # Buscar el modelo que contiene este campo
    try:
        model = apps.get_model('glocal', field_name)  # Asegúrate de que 'glocal' es el nombre correcto de la app
        related_object = model.objects.filter(pk=value).first()
        return str(related_object) if related_object else "N/A"
    except Exception as e:
        return "N/A"  # Si hay un error, retorna N/A

