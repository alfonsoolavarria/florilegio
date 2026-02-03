from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la categoría (ej. Teología)
    icon = models.CharField(max_length=100, default="unicon-book")  # Clase del icono para mostrar en la web

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Article(models.Model):
    title = models.CharField(max_length=255)  # Título principal del artículo
    slug = models.SlugField(unique=True)  # URL amigable basada en el título
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="articles")  # Enlace a la categoría
    image_url = models.URLField(max_length=500)  # Link a la imagen de portada
    content = models.TextField()  # Contenido completo del artículo (soporta HTML)
    tags = models.JSONField(default=list)  # Lista de etiquetas/temas relacionados
    is_featured = models.BooleanField(default=False)  # Si está marcado, aparece en el carrusel de arriba
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de publicación automática
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última edición automática

    def __str__(self):
        return self.title

    @property
    def image(self):
        return {'url': self.image_url}
