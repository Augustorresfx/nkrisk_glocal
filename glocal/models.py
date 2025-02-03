from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}" if self.nombre and self.apellido else self.username

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)  # Código ISO 3166-1 alpha-3

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
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(null=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='edit')  # Campo adicional

    def __str__(self):
        return f"{self.model_name} - {self.object_id}"
    
class Siniestro(models.Model):
    nombre = models.CharField(max_length=200)
    vigencia_hasta = models.DateField(null=True, blank=True)
    monto = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

class Nomina(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni_cuil = models.CharField(max_length=100)
    suma_asegurada = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=25, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contactos_modificados')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contactos')  # Opcional, vincula con un User

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Para habilitar el rastreo de cambios (puedes controlar este comportamiento al llamar a save())
        track_changes = kwargs.pop("track_changes", True)

        # Solo se registran cambios si el objeto ya existe y track_changes está activado
        if self.pk and track_changes:
            original = self.__class__.objects.get(pk=self.pk)
            changes = {}

            # Comparar todos los campos del modelo
            for field in self._meta.fields:
                field_name = field.name
                original_value = getattr(original, field_name)
                new_value = getattr(self, field_name)

                # Manejar ForeignKey (relaciones) dinámicamente
                if isinstance(field, models.ForeignKey):
                    original_value = {
                        "id": original_value.pk if original_value else None,
                        "name": str(original_value) if original_value else None,
                    }
                    new_value = {
                        "id": new_value.pk if new_value else None,
                        "name": str(new_value) if new_value else None,
                    }

                # Comparar los valores para detectar cambios
                if original_value != new_value:
                    changes[field_name] = {"old": original_value, "new": new_value}

            # Si hay cambios, se crea un registro de PendingChange
            if changes:
                from .models import PendingChange
                
                # Verificar si 'modified_by' está correctamente asignado
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,  # El usuario que hizo los cambios
                    )
                else:
                    # Si modified_by no es una instancia válida de User, lanzamos un error
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de CustomUser")

        # Llamada al método save() original para guardar el objeto
        super().save(*args, **kwargs)

class Matriz(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
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
    logo = models.ImageField(upload_to='logos/')
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    domicilio_oficina = models.CharField(max_length=100)
    url_web = models.CharField(max_length=100)
    matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    contactos = models.ManyToManyField(Contacto, related_name='broker')

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

class Aseguradora(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/') 
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    ruc_nit = models.CharField(max_length=100)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    contactos = models.ManyToManyField(Contacto, related_name='aseguradora')

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    ruc_nit = models.CharField(max_length=100)
    activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    contactos = models.ManyToManyField(Contacto, related_name='empresa')

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

class Seguro(models.Model):
    TIPO_CHOICES = [
        ('casualty-3b', 'CASUALTY - 3B'),
        ('casualty-dyo', 'CASUALTY - D&O'),
        ('casualty-rc_l', 'CASUALTY - RESPONSABILIDAD CIVIL / LIABILITY'),
        ('casualty-rc_p', 'CASUALTY - RESPONSABILIDAD CIVIL DE PRODUCTOS'),
        ('casualty-rc_r', 'CASUALTY - RESPONSABILIDAD CIVIL DE RECALL'),
        ('casualty-rc_p_eyo', 'CASUALTY - RESPONSABILIDAD CIVIL DE PROFESIONAL (E&O)'),
        ('casualty-r_f', 'CASUALTY - ROBO / FIDELITY'),
        ('otros-cyber-risk', 'OTROS - CYBER RISK'),
        ('otros-vehiculos', 'OTROS - VEHICULOS'),
        ('property-cascos_hull', 'PROPOERTY - CASCOS / HULL'),
        ('property-multiriesgo_prop', 'PROPERTY - MULTIRIESGO / PROPERTY'),
        ('transporte-expo', 'TRANSPORTE (EXPO)'),
        ('transporte-impo', 'TRANSPORTE (IMPO)'),
        ('accidentes-personales', 'ACCIDENTES PERSONALES')
    ]
    MONEDA_CHOICES = [
        ('ars', 'ARS'),
        ('usd', 'USD'),
        ('eur', 'EUR'),

    ]
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    moneda = models.CharField(max_length=25, choices=MONEDA_CHOICES)
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE)
    tipo_seguro = models.CharField(max_length=25, choices=TIPO_CHOICES)
    nro_poliza = models.IntegerField()
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField(null=True, blank=True)
    #prima_neta_emitida = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    #limite_asegurado = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    #activo = models.BooleanField(default=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente
    
    def __str__(self):
        return f"{self.empresa.nombre} ({self.get_tipo_seguro_display()})"
    
class SeguroAccidentePersonal(Seguro):
    COBERTURA_CHOICES =  {
        ('muerte-incapacidad', 'Muerte e incapacidad'),
        ('asistencia-medica-farmaceutica', 'Asistencia médica / farmacéutica'),
    }

    created = models.DateTimeField(auto_now_add=True)
    cobertura = models.CharField(max_length=55, choices=COBERTURA_CHOICES)
    clausula_de_no_repeticion = models.CharField(max_length=255)
    a_favor_de = models.CharField(max_length=100)
    beneficiario_preferente = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

class SeguroResponsabilidadCivil(Seguro):
    cobertura = models.CharField(max_length=100)
    limite = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    adicionales = models.BooleanField(default=False)
    

class SeguroVehiculo(Seguro):
    created = models.DateTimeField(auto_now_add=True)
    numero_flota = models.IntegerField(null=True, blank=True)
    
class Movimiento(models.Model):
    created = models.DateTimeField(auto_now_add=True,)
    numero_endoso = models.CharField(max_length=100, blank=True, null=True)
    motivo_endoso = models.CharField(max_length=140, blank=True, null=True)
    seguro_vehiculo = models.ForeignKey(SeguroVehiculo, related_name='movimientos', on_delete=models.CASCADE)
    numero_orden = models.CharField(max_length=100, blank=True, null=True)
    vigencia_desde = models.DateField(blank=True, null=True)
    vigencia_hasta = models.DateField(blank=True, null=True)
    fecha_alta_op = models.DateField(blank=True, null=True)
    prima_tec_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_sin_iva_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_con_iva_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza_porcentaje_diferencia = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    premio_con_iva_porcentaje_diferencia = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)

class VehiculoFlota(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cod = models.IntegerField(null=True, blank=True)
    seguro_vehiculo = models.ForeignKey(SeguroVehiculo, related_name='vehiculos', on_delete=models.CASCADE)
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    usuario_item = models.CharField(max_length=255, blank=True, null=True)
    patente = models.CharField(max_length=100, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    okm = models.CharField(max_length=100, blank=True, null=True)
    motor = models.CharField(max_length=100, blank=True, null=True)
    chasis = models.CharField(max_length=100, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    vigencia_desde = models.DateField(null=True, blank=True)
    vigencia_hasta = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    uso_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    valor_actual = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    tasa = models.DecimalField(decimal_places=3, max_digits=100, null=True, blank=True)
    prima_rc = models.DecimalField(decimal_places=3, max_digits=100, null=True, blank=True)
    tiene_accesorios = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada_accesorios = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    observacion = models.CharField(max_length=100, blank=True, null=True)
    prima_tecnica = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_sin_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_con_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    history = HistoricalRecords()
    
class MarcaInfoAuto(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
class VehiculoInfoAuto(models.Model):
    codigo = models.CharField(max_length=100, blank=True, null=True)
    marca = models.ForeignKey(MarcaInfoAuto, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    precio_okm = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.descripcion}"
    
class PrecioAnual(models.Model):
    vehiculo = models.ForeignKey(VehiculoInfoAuto, on_delete=models.CASCADE)
    anio = models.IntegerField()
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    
    def __str__(self):
        return f"{self.precio}"
    
class Archivo(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usuario',)
    activo = models.BooleanField(default=False)
    archivo = models.FileField(upload_to="archivos/")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario_modificado',)

    def save(self, *args, **kwargs):
        # Verificar si se deben registrar cambios
        track_changes = kwargs.pop("track_changes", True)

        if self.pk and track_changes:  # Solo registrar cambios si es un objeto existente y se permite rastrear
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
                if self.modified_by and isinstance(self.modified_by, settings.AUTH_USER_MODEL):
                    PendingChange.objects.create(
                        model_name=self._meta.model_name,
                        object_id=self.pk,
                        changes=changes,
                        submitted_by=self.modified_by,
                    )
                else:
                    raise ValueError("El campo 'modified_by' debe ser una instancia válida de User")

        super().save(*args, **kwargs)  # Guardar el objeto normalmente

    def __str__(self):
        return self.nombre