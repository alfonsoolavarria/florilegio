import json
import re
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class VineConcord(models.Model):
    topic = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField(blank=True, null=True)
    is_strong = models.BooleanField(default=False)
    is_concord = models.BooleanField(default=False)
    strong_numbers = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'vine_concord'
        verbose_name = 'Vine/Concord'
        verbose_name_plural = 'Vine/Concord'

    def __str__(self):
        return self.topic


class StrongConcord(models.Model):
    topic = models.CharField(max_length=255, primary_key=True)
    definition = models.TextField(blank=True, null=True)
    is_strong = models.BooleanField(default=False)
    is_concord = models.BooleanField(default=False)
    strong_numbers = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'strong_concord'
        verbose_name = 'Strong'
        verbose_name_plural = 'Strong'

    def __str__(self):
        return self.topic


class Category(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la categoría (ej. Teología)
    icon = models.CharField(max_length=100, default="unicon-book")  # Clase del icono para mostrar en la web

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='author_profile')
    name = models.CharField(max_length=150)
    bio = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    social_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: @JohnPiper")

    def __str__(self):
        return self.name

    def clean(self):
        if self.user and Author.objects.filter(user=self.user).exclude(pk=self.pk).exists():
            raise ValidationError(f"El usuario {self.user.email} ya tiene un perfil de autor.")

class Article(models.Model):
    STATUS_CHOICES = [
        ('revision', 'En Revisión'),
        ('liberado', 'Liberado'),
    ]

    title = models.CharField(max_length=255)  # Título principal del artículo
    slug = models.SlugField(unique=True)  # URL amigable basada en el título
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="articles") # Enlace al autor
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="articles")  # Enlace a la categoría
    image_url = models.URLField(max_length=500)  # Link a la imagen de portada
    content = models.TextField()  # Contenido completo del artículo (soporta HTML)
    tags = models.JSONField(default=list)  # Lista de etiquetas/temas relacionados
    meta_description = models.TextField(blank=True, null=True, help_text="Descripción para SEO y redes sociales. Máximo 160 caracteres.")
    is_featured = models.BooleanField(default=False)  # Si está marcado, aparece en el carrusel de arriba
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='revision')  # Estado de publicación
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de publicación automática
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última edición automática

    def __str__(self):
        return self.title

    @property
    def image(self):
        return {'url': self.image_url}

    @property
    def seo_description(self):
        if self.meta_description:
            return self.meta_description
        clean = re.sub(r'<[^>]+>', '', self.content)[:160].strip() if self.content else self.title
        return clean

class Essay(models.Model):
    STATUS_CHOICES = [
        ('revision', 'En Revisión'),
        ('liberado', 'Liberado'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="essays")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="essays")
    image_url = models.URLField(max_length=500)
    content = models.TextField()
    tags = models.JSONField(default=list)
    meta_description = models.TextField(blank=True, null=True, help_text="Descripción para SEO y redes sociales. Máximo 160 caracteres.")
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='revision')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def image(self):
        return {'url': self.image_url}

    @property
    def seo_description(self):
        if self.meta_description:
            return self.meta_description
        clean = re.sub(r'<[^>]+>', '', self.content)[:160].strip() if self.content else self.title
        return clean

class PalabraBiblia(models.Model):
    ognt_sort = models.CharField(max_length=50, primary_key=True)
    libro = models.IntegerField()
    capitulo = models.IntegerField()
    versiculo = models.IntegerField()

    def __str__(self):
        return f"{self.libro}:{self.capitulo}:{self.versiculo} - {self.ognt_sort}"

class TraduccionLiteral(models.Model):
    palabra = models.OneToOneField(PalabraBiblia, on_delete=models.CASCADE, related_name='traduccion')
    espanol = models.CharField(max_length=255, null=True, blank=True)
    griego = models.CharField(max_length=255, null=True, blank=True)
    raiz_griega = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.palabra.ognt_sort} -> {self.espanol}"

class Morfologia(models.Model):
    palabra = models.OneToOneField(PalabraBiblia, on_delete=models.CASCADE, related_name='morfologia')
    rmac = models.CharField(max_length=50, null=True, blank=True)
    descripcion_rmac = models.CharField(max_length=255, null=True, blank=True)
    low_nida_number = models.CharField(max_length=150, null=True, blank=True)
    strong = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.palabra.ognt_sort} -> {self.rmac}"

class PalabraHebreo(models.Model):
    oshb_id = models.CharField(max_length=50, primary_key=True)
    libro = models.IntegerField()
    capitulo = models.IntegerField()
    versiculo = models.IntegerField()
    orden = models.IntegerField()

class TraduccionHebreo(models.Model):
    palabra = models.OneToOneField(PalabraHebreo, on_delete=models.CASCADE, related_name='traduccion_hebreo')
    hebreo = models.CharField(max_length=255)
    raiz_hebrea = models.CharField(max_length=255, null=True, blank=True)
    espanol = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.palabra.oshb_id} -> {self.hebreo}"

class MorfologiaHebreo(models.Model):
    palabra = models.OneToOneField(PalabraHebreo, on_delete=models.CASCADE, related_name='morfologia_hebreo')
    morph_code = models.CharField(max_length=50)
    strong = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.palabra.oshb_id} -> {self.morph_code}"

class LibroBiblia(models.Model):
    numero = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=50)
    testamento = models.CharField(max_length=50, default="Nuevo Testamento")
    estructura_capitulos = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.numero} - {self.nombre}"

class VersiculoBiblia(models.Model):
    version = models.CharField(max_length=20) # e.g. 'rv1960', 'rva2015'
    libro = models.IntegerField()
    capitulo = models.IntegerField()
    versiculo = models.IntegerField()
    texto = models.TextField()

    class Meta:
        unique_together = ('version', 'libro', 'capitulo', 'versiculo')

    def __str__(self):
        return f"[{self.version.upper()}] {self.libro} {self.capitulo}:{self.versiculo}"

class ContextoLibro(models.Model):
    libro = models.ForeignKey(LibroBiblia, on_delete=models.CASCADE, related_name='contextos')
    contenido = models.TextField()

    class Meta:
        db_table = 'contexto_libro'
        verbose_name = 'Contexto de Libro'
        verbose_name_plural = 'Contextos de Libros'

    def __str__(self):
        return f'Contexto de {self.libro.nombre}'

    def get_contenido(self):
        return json.loads(self.contenido)


class ApiBibleSyncStatus(models.Model):
    VERSION_CHOICES = [
        ('nbla', 'Nueva Biblia de las Américas'),
        ('ntv', 'Nueva Traducción Viviente'),
        ('rvr09', 'Reina Valera 1909'),
    ]
    version = models.CharField(max_length=20, choices=VERSION_CHOICES, unique=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "API Bible Sync Statuses"

    def __str__(self):
        return f"{self.get_version_display()} (Last synced: {self.last_synced_at.strftime('%Y-%m-%d %H:%M')})"


class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Gratis'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, verbose_name="Biografía")
    avatar_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL del avatar")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free', verbose_name="Plan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    def study_limit(self):
        limits = {'free': 3, 'premium': 100, 'pro': None}
        return limits.get(self.plan, 3)

    @property
    def is_author(self):
        return hasattr(self.user, 'author_profile')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"


class UserStudy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studies')
    title = models.CharField(max_length=255, blank=True, default='')
    reference = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title or self.reference or 'Sin título'}"

    class Meta:
        verbose_name = "Estudio de usuario"
        verbose_name_plural = "Estudios de usuarios"
        ordering = ['-updated_at']


class AgeCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, default="unicon-users")
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Categoría de edad"
        verbose_name_plural = "Categorías de edad"
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class MadreMaestraResource(models.Model):
    STATUS_CHOICES = [
        ('revision', 'En Revisión'),
        ('liberado', 'Liberado'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, related_name="resources")
    image_url = models.URLField(max_length=500, blank=True, null=True)
    bible_passage = models.CharField(max_length=200, blank=True, null=True, help_text="Pasaje bíblico (ej. Juan 3:16)")
    key_verse = models.CharField(max_length=300, blank=True, null=True, help_text="Versículo clave")
    objective = models.TextField(blank=True, null=True, help_text="Objetivo de la enseñanza")
    materials = models.TextField(blank=True, null=True, help_text="Materiales necesarios")
    time_minutes = models.IntegerField(blank=True, null=True, help_text="Tiempo estimado en minutos")
    content = models.TextField(blank=True, null=True, help_text="Desarrollo completo de la lección (soporta HTML)")
    summary = models.TextField(blank=True, null=True, help_text="Resumen corto para la tarjeta")
    tags = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='revision')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recurso MM"
        verbose_name_plural = "Recursos MM"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def image(self):
        return {'url': self.image_url} if self.image_url else {'url': ''}


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)

