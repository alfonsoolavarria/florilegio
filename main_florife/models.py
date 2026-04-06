from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la categoría (ej. Teología)
    icon = models.CharField(max_length=100, default="unicon-book")  # Clase del icono para mostrar en la web

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Author(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    social_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: @JohnPiper")

    def __str__(self):
        return self.name

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
    is_featured = models.BooleanField(default=False)  # Si está marcado, aparece en el carrusel de arriba
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='revision')  # Estado de publicación
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de publicación automática
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última edición automática

    def __str__(self):
        return self.title

    @property
    def image(self):
        return {'url': self.image_url}

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

class LibroBiblia(models.Model):
    numero = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=50)
    testamento = models.CharField(max_length=50, default="Nuevo Testamento")
    estructura_capitulos = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.numero} - {self.nombre}"
