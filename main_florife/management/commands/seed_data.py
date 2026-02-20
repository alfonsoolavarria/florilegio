from django.core.management.base import BaseCommand
from main_florife.models import Category, Article, Author

class Command(BaseCommand):
    help = 'Seeds the database with initial mock data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Categories mapping
        categories_data = [
            {"name": "Teología", "icon": "unicon-捧げ物"},
            {"name": "Historia", "icon": "unicon-historical-monument"},
            {"name": "Biografías", "icon": "unicon-users"},
            {"name": "Interpretación", "icon": "unicon-book-open"},
            {"name": "Familia", "icon": "unicon-home-alt"},
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

        # Create Default Author
        author_obj, _ = Author.objects.get_or_create(
            name="John Piper",
            defaults={
                "bio": "John Piper (@JohnPiper) es fundador y maestro de desiringGod.org y ministro del Colegio y Seminario Belén. Durante 33 años, trabajó como pastor de la Iglesia Bautista Belén en Minneapolis, Minnesota. Es autor de más de 50 libros.",
                "image_url": "https://www.desiringgod.org/system/authors/portraits/000/000/001/original/john-piper-2023.jpg", # Placeholder image
                "social_handle": "@JohnPiper"
            }
        )

        # Articles data from mock
        articles_data = [
            {
                "title": "La Importancia de la Oración",
                "slug": "importancia-oracion",
                "category": "Interpretación",
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600&auto=format&fit=crop",
                "content": "<p>Contenido de prueba sobre la oración...</p><span class='quote-tag'>Cita</span><blockquote>'La oración no es para vencer la reticencia de Dios, sino para echar mano de Su disposición.'</blockquote>",
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
                "category": "Familia",
                "image_url": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=600&auto=format&fit=crop",
                "content": """
<h2>Desafíos y Oportunidades de la Fe en la Era Digital</h2>
<p>En el umbral del siglo XXI, la fe se encuentra en una encrucijada sin precedentes. La rapidez de los cambios tecnológicos y sociales ha transformado no solo nuestra manera de comunicarnos, sino también nuestra forma de percibir lo sagrado y lo cotidiano. En este contexto, vivir una fe auténtica requiere un discernimiento constante y una vuelta a las raíces fundamentales que sostienen nuestra identidad.</p>

<p><span class="phrase-highlight">La tecnología no es un enemigo de la espiritualidad</span>, pero sí un entorno que demanda una nueva forma de presencia. La saturación de información puede llevar a una superficialidad que ahoga la meditación y el silencio, elementos vitales para el crecimiento del espíritu. Es necesario reaprender el arte de la quietud en un mundo que nunca descansa.</p>

<div class="keyword-highlight-box">
    <strong>Palabra Clave: Discernimiento</strong><br>
    El proceso de distinguir la verdad del error, y lo esencial de lo accesorio, en un mundo saturado de voces que compiten por nuestra atención.
</div>

<h3>El Papel de la Familia en la Transmisión de la Fe</h3>
<p>La familia sigue siendo el núcleo fundamental donde se gesta y se nutre la experiencia de Dios. Sin embargo, las dinámicas familiares han cambiado. La mesa de comedor, antaño lugar de encuentro y diálogo, hoy compite con las pantallas individuales. Recuperar los espacios de comunión familiar es uno de los mayores actos de resistencia espiritual en nuestra época.</p>

<blockquote>
    "La fe no es algo que se posee de una vez por todas, sino un camino que se recorre cada día en la presencia de los demás."
</blockquote>

<p>Es en la cotidianidad de las relaciones familiares donde la fe cobra vida. El perdón, la paciencia y el servicio mutuo son las expresiones más concretas de un Evangelio vivido. No basta con enseñar doctrinas; es necesario modelar una vida que sea atractiva por su coherencia y su amor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

<p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. <span class="phrase-highlight">La constancia en la oración es el pilar que sostiene la estructura de la familia cristiana</span>. Sin este contacto vital con la Fuente, corremos el riesgo de convertir nuestra fe en una simple tradición cultural sin poder transformador.</p>

<h3>Integridad y Ética en el Siglo XXI</h3>
<p>Vivir la fe en el ámbito público presenta desafíos éticos complejos. La integridad se pone a prueba en el trabajo, en la política y en las redes sociales. A menudo, existe una presión sutil para compartimentar nuestra fe, dejándola recluida en el ámbito de lo privado. No obstante, una fe que no informa nuestras decisiones públicas es una fe incompleta.</p>

<p>Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida. Duis ac tellus et risus vulputate vehicula. Donec lobortis risus a elit. Etiam tempor. Ut ullamcorper, ligula eu tempor congue, eros est euismod turpis, id tincidunt sapien risus a quam. Maecenas fermentum consequat mi. Donec fermentum. Pellentesque malesuada nulla a mi. Duis sapien sem, aliquet nec, commodo eget, consequat quis, neque. Aliquam faucibus, elit ut dictum aliquet, felis nisl adipiscing sapien, sed rhoncus lacus sem vitae quam.</p>

<p>Sed convallis magna eu sem. <span class="phrase-highlight">La integridad consiste en ser la misma persona en la luz y en la sombra</span>. Este es el testimonio más poderoso que un creyente puede ofrecer al mundo actual: una vida que no está fragmentada, sino unificada por un propósito superior. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

<h3>Conclusión: Un Llamado a la Esperanza</h3>
<p>A pesar de las dificultades, el siglo XXI ofrece oportunidades únicas para la expresión de la fe. La globalización permite conexiones que antes eran impensables, y el hambre de autenticidad en una cultura a menudo vacía abre puertas para un diálogo profundo. Nuestra tarea es habitar este tiempo con esperanza, no con miedo, confiando en que la Verdad sigue teniendo el poder de liberar y renovar todas las cosas.</p>

<p>Vivamos, pues, con valentía, siendo conscientes de que cada acto pequeño de amor y fidelidad resuena en la eternidad. Que nuestra fe sea el faro que guía no solo nuestros pasos, sino también los de aquellos que caminan junto a nosotros en la penumbra de la incertidumbre. Finalizamos este recorrido reconociendo que la fe, aunque antigua en sus fundamentos, es siempre nueva en su aplicación y capacidad de asombrar al corazón humano.</p>
""",
                "tags": ["Cultura", "Fe", "Familia", "Integridad"],
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
                    "author": author_obj,
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
