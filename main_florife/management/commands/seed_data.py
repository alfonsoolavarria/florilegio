from django.core.management.base import BaseCommand
from main_florife.models import Category, Article

class Command(BaseCommand):
    help = 'Seeds the database with initial mock data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Categories mapping
        categories_data = [
            {"name": "Teología", "icon": "unicon-捧げ物"},
            {"name": "Historia", "icon": "unicon-historical-monument"},
            {"name": "Biografías", "icon": "unicon-users"},
            {"name": "Espiritualidad", "icon": "unicon-heart-filled"},
            {"name": "Contemporáneo", "icon": "unicon-book"},
        ]

        categories = {}
        for cat in categories_data:
            obj, created = Category.objects.get_or_create(
                name=cat["name"],
                defaults={"icon": cat["icon"]}
            )
            categories[cat["name"]] = obj
            if created:
                self.stdout.write(f"Created category: {cat['name']}")

        # Normalizing Biografía vs Biografías
        categories["Biografía"] = categories["Biografías"]

        # Articles data from mock
        articles_data = [
            {
                "title": "La Importancia de la Oración",
                "slug": "importancia-oracion",
                "category": "Espiritualidad",
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Contenido de prueba sobre la oración...</p>",
                "tags": ["Oración", "Fe"],
                "is_featured": True
            },
            {
                "title": "Historia de la Reforma",
                "slug": "historia-reforma",
                "category": "Historia",
                "image_url": "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Contenido de prueba sobre la reforma...</p>",
                "tags": ["Reforma", "Biblia"],
                "is_featured": True
            },
            {
                "title": "Biografía de San Agustín",
                "slug": "biografia-agustin",
                "category": "Biografía",
                "image_url": "https://images.unsplash.com/photo-1519794206461-fcd5dc32c0a8?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Contenido de prueba sobre San Agustín...</p>",
                "tags": ["Teología", "Historia"],
                "is_featured": True
            },
            {
                "title": "La Gracia Irresistible",
                "slug": "gracia-irresistible",
                "category": "Teología",
                "image_url": "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Un estudio sobre la doctrina de la gracia...</p>",
                "tags": ["Gracia", "Soteriología"],
                "is_featured": True
            },
            {
                "title": "Juan Calvino: El Reformador de Ginebra",
                "slug": "juan-calvino",
                "category": "Biografía",
                "image_url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Vida y obra de uno de los pilares de la reforma...</p>",
                "tags": ["Reforma", "Teología"],
                "is_featured": True
            },
            {
                "title": "Los Concilios Ecuménicos",
                "slug": "concilios-ecumenicos",
                "category": "Historia",
                "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Un repaso por los grandes acuerdos de la iglesia primitiva...</p>",
                "tags": ["Historia", "Iglesia"],
                "is_featured": True
            },
            {
                "title": "La Soberanía de Dios",
                "slug": "soberania-dios",
                "category": "Teología",
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Explorando el control absoluto de Dios sobre la creación...</p>",
                "tags": ["Teología", "Atributos"],
                "is_featured": False
            },
            {
                "title": "Viviendo la fe en el siglo XXI",
                "slug": "fe-siglo-21",
                "category": "Contemporáneo",
                "image_url": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Cómo aplicar los principios bíblicos en la cultura actual...</p>",
                "tags": ["Cultura", "Fe"],
                "is_featured": False
            },
            {
                "title": "Los Puritanos y su Legado",
                "slug": "puritanos-legado",
                "category": "Historia",
                "image_url": "https://images.unsplash.com/photo-1512418490979-92798ccc1380?q=80&w=600&auto=format&fit=crop",
                "content": "<p>El impacto de los puritanos en la espiritualidad protestante...</p>",
                "tags": ["Historia", "Puritanos"],
                "is_featured": False
            }
        ]

        for art in articles_data:
            obj, created = Article.objects.get_or_create(
                slug=art["slug"],
                defaults={
                    "title": art["title"],
                    "category": categories[art["category"]],
                    "image_url": art["image_url"],
                    "content": art["content"],
                    "tags": art["tags"],
                    "is_featured": art["is_featured"]
                }
            )
            if created:
                self.stdout.write(f"Created article: {art['title']}")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
