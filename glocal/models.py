from django.db import models
from django.contrib.auth.models import User

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)  # Código ISO 3166-1 alpha-3

    def __str__(self):
        return self.nombre
    
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)  # Opcional, vincula con un User

    def __str__(self):
        return self.nombre


class PendingChange(models.Model):
    ACTION_CHOICES = [
        ('edit', 'Edición'),
        ('delete', 'Eliminación'),
        ('create', 'Creación'),
    ]
    
    model_name = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    changes = models.JSONField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(null=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='edit')  # Campo adicional

    def __str__(self):
        return f"{self.model_name} - {self.object_id}"

class Matriz(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contactos = models.ManyToManyField(Contacto, related_name='matrices')

    def save(self, *args, **kwargs):
        if self.pk:  # Solo para objetos existentes
            original = self.__class__.objects.get(pk=self.pk)
            changes = {}

            for field in self._meta.fields:
                field_name = field.name
                original_value = getattr(original, field_name)
                new_value = getattr(self, field_name)

                # Manejar ForeignKey dinámicamente
                if isinstance(field, models.ForeignKey):
                    original_value = {
                        "id": original_value.pk if original_value else None,
                        "name": str(original_value) if original_value else None,
                    }
                    new_value = {
                        "id": new_value.pk if new_value else None,
                        "name": str(new_value) if new_value else None,
                    }

                # Comparar valores y registrar cambios
                if original_value != new_value:
                    changes[field_name] = {"old": original_value, "new": new_value}

            # Crear un registro de cambios si hay diferencias
            if changes:
                from .models import PendingChange
                if self.modified_by and isinstance(self.modified_by, User):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente


class Broker(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/')  # El logo se almacena en la carpeta 'media/logos/'
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    domicilio_oficina = models.CharField(max_length=100)
    url_web = models.CharField(max_length=100)
    matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    contactos = models.ManyToManyField(Contacto, related_name='broker')

class Aseguradora(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    tax_id = models.CharField(max_length=100)
    activo = models.BooleanField(default=False)
    contactos = models.ManyToManyField(Contacto, related_name='aseguradora')

