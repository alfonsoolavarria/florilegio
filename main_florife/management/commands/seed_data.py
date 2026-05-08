from django.core.management.base import BaseCommand
from main_florife.models import Category, Article, Author, Essay


MODES = {
    1: "all",
    2: "articles",
    3: "categories",
    4: "author",
    5: "essays",
}


class Command(BaseCommand):
    help = 'Seeds the database with initial data. Usage: seed_data [mode]  (1=all, 2=articles, 3=categories, 4=author, 5=essays)'

    def add_arguments(self, parser):
        parser.add_argument(
            'mode',
            nargs='?',
            type=int,
            default=1,
            choices=list(MODES.keys()),
            help='1=all, 2=articles, 3=categories, 4=author, 5=essays'
        )

    def handle(self, *args, **kwargs):
        mode = kwargs['mode']
        label = MODES[mode]
        self.stdout.write(f"Seed mode: {mode} ({label})")

        if mode == 1 or mode == 3:
            self._seed_categories()
        if mode == 1 or mode == 4:
            self._seed_author()
        if mode == 1 or mode == 5:
            self._seed_essays()
        if mode == 1 or mode == 2:
            self._seed_articles()

        self.stdout.write(self.style.SUCCESS("Done!"))

    # ─── Categories ────────────────────────────────────────────────────

    def _seed_categories(self):
        categories_data = [
            {"name": "Teología", "icon": "unicon-book"},
            {"name": "Historia", "icon": "unicon-historical-monument"},
            {"name": "Biografías", "icon": "unicon-users"},
            {"name": "Interpretación", "icon": "unicon-book-open"},
            {"name": "Familia", "icon": "unicon-home-alt"},
            {"name": "Contemporáneo", "icon": "unicon-archive"},
        ]
        for cat in categories_data:
            obj, created = Category.objects.get_or_create(
                name=cat["name"],
                defaults={"icon": cat["icon"]}
            )
            if created:
                self.stdout.write(f"  Created category: {cat['name']}")
        # Normalize alias
        cat_biografias = Category.objects.get(name="Biografías")
        Category.objects.get_or_create(name="Biografía", defaults={"icon": cat_biografias.icon})

    # ─── Author ────────────────────────────────────────────────────────

    def _seed_author(self):
        author_obj, created = Author.objects.get_or_create(
            name="John Piper",
            defaults={
                "bio": "John Piper (@JohnPiper) es fundador y maestro de desiringGod.org y ministro del Colegio y Seminario Belén.",
                "image_url": "https://www.desiringgod.org/system/authors/portraits/000/000/001/original/john-piper-2023.jpg",
                "social_handle": "@JohnPiper"
            }
        )
        if created:
            self.stdout.write(f"  Created author: {author_obj.name}")

    # ─── Essays ────────────────────────────────────────────────────────

    def _seed_essays(self):
        author = Author.objects.first()
        if not author:
            self.stdout.write(self.style.WARNING("  No author found. Run mode 4 first."))
            return

        def cat(name):
            return Category.objects.get(name=name)

        essays_data = [
            {
                "title": "La Analogía del Ser en la tradición Tomista",
                "slug": "analogia-del-ser-tradicion-tomista",
                "category": "Teología",
                "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800",
                "content": "<h2>Introducción al concepto</h2><p>Un análisis exhaustivo sobre cómo la distinción entre esencia y existencia fundamenta la posibilidad de un conocimiento racional de lo divino.</p><h3>La distinción esencia-existencia</h3><p>Este ensayo explora las implicaciones metafísicas del pensamiento de Santo Tomás de Aquino.</p><h3>El concepto de analogía</h3><p>La distinción real entre esencia y existencia constituye el pilar fundamental de la metafísica tomista.</p><h2>REFERENCIAS BIBLIOGRÁFICAS</h2><p>Aquino, T. <span class='not-italic font-medium text-on-surface'>Summa Theologiae</span>. Traducido por la Provincia Dominicana. New York: Benziger Bros, 1947.</p><p>McGrath, A. <span class='not-italic font-medium text-on-surface'>Iustitia Dei: A History of the Christian Doctrine of Justification</span>. Cambridge: Cambridge University Press, 2005.</p>",
                "tags": ["tomismo", "metafísica", "analogía"],
                "is_featured": True,
                "status": "liberado"
            },
            {
                "title": "Virtud y Bien Común: Una relectura",
                "slug": "virtud-bien-comun-secunda-secundae",
                "category": "Contemporáneo",
                "image_url": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800",
                "content": "<h2>Justicia distributiva</h2><p>Explorando la relevancia de la justicia distributiva en el pensamiento de Aquino y su aplicación práctica.</p><h3>El concepto de Habitus</h3><p>El ensayo profundiza en el concepto de 'Habitus' como motor de cambio social.</p><h3>Aplicación actual</h3><p>El bien común no es una suma de bienes individuales, sino la condición social que permite alcanzar la plenitud.</p><h2>REFERENCIAS BIBLIOGRÁFICAS</h2><p>Aquino, T. <span class='not-italic font-medium text-on-surface'>Summa Theologiae, Secunda Secundae</span>. Roma: Commissio Leonina, 1892.</p><p>Pesch, O. H. <span class='not-italic font-medium text-on-surface'>The Theology of Justification according to Saint Thomas Aquinas and Martin Luther</span>. Berlin: Akademie Verlag, 1985.</p>",
                "tags": ["ética", "virtud", "bien común"],
                "is_featured": False,
                "status": "liberado"
            },
            {
                "title": "El Intelecto Agente y la Iluminación Divina",
                "slug": "intelecto-agente-iluminacion-divina",
                "category": "Historia",
                "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a7f531ad?w=800",
                "content": "<h2>Gnoseología medieval</h2><p>Debates sobre la gnoseología medieval: una comparación crítica entre las posturas agustinianas y el aristotelismo cristiano.</p><h3>Fe y razón</h3><p>¿Cómo interactúa la luz natural de la razón con la revelación en el acto del entendimiento?</p><h3>Iluminación vs Intelecto</h3><p>La iluminación divina no anula la capacidad natural del intelecto, sino que la eleva y perfecciona.</p><h2>REFERENCIAS BIBLIOGRÁFICAS</h2><p>Agustín de Hipona. <span class='not-italic font-medium text-on-surface'>De Genesi ad Litteram</span>. Traducido por J. H. Taylor. New York: Newman Press, 1982.</p><p>Oberman, H. <span class='not-italic font-medium text-on-surface'>The Harvest of Medieval Theology: Gabriel Biel and Late Medieval Nominalism</span>. Cambridge, MA: Harvard University Press, 1963.</p>",
                "tags": ["epistemología", "intelecto", "iluminación"],
                "is_featured": True,
                "status": "liberado"
            },
            {
                "title": "Juan: Teología del Cuarto Evangelio",
                "slug": "juan-ensayo",
                "category": "Teología",
                "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                "content": "<h2>Introducción</h2><p>El Evangelio de Juan presenta una teología única centrada en la divinidad de Cristo y la vida eterna mediante la fe.</p><h3>El Logos divino</h3><p>En el prólogo (Jn 1,1-18) se presenta a Jesucristo como el Logos eterno, la Palabra que estaba con Dios y era Dios.</p><h3>Signos y discursos</h3><p>Los 'signos' en Juan no son meros milagros, sino revelaciones de la gloria de Dios que invitan a una respuesta de fe.</p><h3>Soteriología juanica</h3><p>La salvación en Juan se entiende como pasar de la muerte a la vida, con énfasis en el conocimiento salvífico.</p><h2>REFERENCIAS BIBLIOGRÁFICAS</h2><p>Brown, R. E. <span class='not-italic font-medium text-on-surface'>The Gospel According to John</span>. New York: Doubleday, 1966.</p><p>Köstenberger, A. J. <span class='not-italic font-medium text-on-surface'>John</span>. Grand Rapids: Baker Academic, 2004.</p>",
                "tags": ["juan", "evangelio", "teología"],
                "is_featured": False,
                "status": "liberado"
            }
        ]

        for essay in essays_data:
            obj, created = Essay.objects.get_or_create(
                slug=essay["slug"],
                defaults={
                    "title": essay["title"],
                    "author": author,
                    "category": cat(essay["category"]),
                    "image_url": essay["image_url"],
                    "content": essay["content"],
                    "tags": essay["tags"],
                    "is_featured": essay["is_featured"],
                    "status": essay["status"]
                }
            )
            if created:
                self.stdout.write(f"  Created essay: {essay['title']}")

    # ─── Articles ──────────────────────────────────────────────────────

    def _seed_articles(self):
        author = Author.objects.first()
        if not author:
            self.stdout.write(self.style.WARNING("  No author found. Run mode 4 first."))
            return

        def cat(name):
            return Category.objects.get(name=name)

        articles_data = [
            {
                "title": "La Justificación por la Fe: Una Perspectiva Reformada",
                "slug": "justificacion-por-la-fe",
                "category": "Teología",
                "image_url": "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?w=800",
                "content": "<h2>Introducción</h2><p>La doctrina de la justificación por la fe es central para la teología reformada y fue redescubierta durante la Reforma Protestante.</p><h3>El testimonio de las Escrituras</h3><p>Pablo en Romanos 3:28 nos dice que el hombre es justificado por la fe sin las obras de la ley.</p><h3>Imputación vs Infusión</h3><p>La perspectiva reformada sostiene que la justicia de Cristo nos es imputada, no infundida.</p><h2>Conclusión</h2><p>La justificación por la fe sola (sola fide) sigue siendo el artículo por el cual la iglesia se mantiene en pie.</p>",
                "tags": ["justificación", "fe", "reforma"],
                "is_featured": True,
                "status": "liberado"
            },
            {
                "title": "San Agustín: Una Vida de Gracia",
                "slug": "san-agustin-vida-de-gracia",
                "category": "Biografías",
                "image_url": "https://images.unsplash.com/photo-1528900921957-64b4725a2b71?w=800",
                "content": "<h2>Primeros años</h2><p>Agustín de Hipona nació en Tagaste en el año 354 d.C. y su vida temprana estuvo marcada por la búsqueda de la verdad.</p><h3>Conversión</h3><p>En el año 386, Agustín experimentó una conversión radical en un jardín en Milán.</p><h3>Legado</h3><p>Sus obras, especialmente las Confesiones y La Ciudad de Dios, han moldeado el pensamiento occidental.</p>",
                "tags": ["agustín", "patrística", "gracia"],
                "is_featured": True,
                "status": "liberado"
            },
            {
                "title": "El Canon del Nuevo Testamento: Formación y Criterios",
                "slug": "canon-nuevo-testamento",
                "category": "Historia",
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800",
                "content": "<h2>Los primeros siglos</h2><p>La formación del canon del Nuevo Testamento fue un proceso gradual que tomó varios siglos.</p><h3>Criterios de canonicidad</h3><p>Los padres de la iglesia utilizaron tres criterios principales: apostolicidad, ortodoxia y uso litúrgico.</p><h3>Listas canónicas</h3><p>El fragmento Muratoriano (ca. 170 d.C.) es una de las listas más antiguas de libros del Nuevo Testamento.</p>",
                "tags": ["canon", "nuevo testamento", "historia"],
                "is_featured": False,
                "status": "liberado"
            },
            {
                "title": "Matrimonio y Gracia: Una Visión Sacramental",
                "slug": "matrimonio-y-gracia",
                "category": "Familia",
                "image_url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800",
                "content": "<h2>El diseño original</h2><p>Desde el Génesis, el matrimonio es presentado como una institución divina donde dos se convierten en una sola carne.</p><h3>Gracia para el matrimonio</h3><p>La gracia de Dios capacita a las parejas para vivir el amor sacrificial que Cristo modeló.</p><h3>Desafíos contemporáneos</h3><p>En un mundo que redefine el matrimonio, la iglesia está llamada a proclamar y encarnar el diseño de Dios.</p>",
                "tags": ["matrimonio", "familia", "gracia"],
                "is_featured": False,
                "status": "liberado"
            },
        ]

        for article in articles_data:
            obj, created = Article.objects.get_or_create(
                slug=article["slug"],
                defaults={
                    "title": article["title"],
                    "author": author,
                    "category": cat(article["category"]),
                    "image_url": article["image_url"],
                    "content": article["content"],
                    "tags": article["tags"],
                    "is_featured": article["is_featured"],
                    "status": article["status"]
                }
            )
            if created:
                self.stdout.write(f"  Created article: {article['title']}")
