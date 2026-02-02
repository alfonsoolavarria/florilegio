from django.shortcuts import render

# Mock data for articles
MOCK_ARTICLES = [
    {
        "id": 1,
        "title": "La Importancia de la Oración",
        "slug": "importancia-oracion",
        "category": "Espiritualidad",
        "image": {"url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Contenido de prueba sobre la oración...</p>",
        "tags": ["Oración", "Fe"]
    },
    {
        "id": 2,
        "title": "Historia de la Reforma",
        "slug": "historia-reforma",
        "category": "Historia",
        "image": {"url": "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Contenido de prueba sobre la reforma...</p>",
        "tags": ["Reforma", "Biblia"]
    },
    {
        "id": 3,
        "title": "Biografía de San Agustín",
        "slug": "biografia-agustin",
        "category": "Biografía",
        "image": {"url": "https://images.unsplash.com/photo-1519794206461-fcd5dc32c0a8?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Contenido de prueba sobre San Agustín...</p>",
        "tags": ["Teología", "Historia"]
    },
    {
        "id": 4,
        "title": "La Gracia Irresistible",
        "slug": "gracia-irresistible",
        "category": "Teología",
        "image": {"url": "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Un estudio sobre la doctrina de la gracia...</p>",
        "tags": ["Gracia", "Soteriología"]
    },
    {
        "id": 5,
        "title": "Juan Calvino: El Reformador de Ginebra",
        "slug": "juan-calvino",
        "category": "Biografía",
        "image": {"url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Vida y obra de uno de los pilares de la reforma...</p>",
        "tags": ["Reforma", "Teología"]
    },
    {
        "id": 6,
        "title": "Los Concilios Ecuménicos",
        "slug": "concilios-ecumenicos",
        "category": "Historia",
        "image": {"url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Un repaso por los grandes acuerdos de la iglesia primitiva...</p>",
        "tags": ["Historia", "Iglesia"]
    },
    {
        "id": 7,
        "title": "La Soberanía de Dios",
        "slug": "soberania-dios",
        "category": "Teología",
        "image": {"url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Explorando el control absoluto de Dios sobre la creación...</p>",
        "tags": ["Teología", "Atributos"]
    },
    {
        "id": 8,
        "title": "Viviendo la fe en el siglo XXI",
        "slug": "fe-siglo-21",
        "category": "Contemporáneo",
        "image": {"url": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>Cómo aplicar los principios bíblicos en la cultura actual...</p>",
        "tags": ["Cultura", "Fe"]
    },
    {
        "id": 9,
        "title": "Los Puritanos y su Legado",
        "slug": "puritanos-legado",
        "category": "Historia",
        "image": {"url": "https://images.unsplash.com/photo-1512418490979-92798ccc1380?q=80&w=600&auto=format&fit=crop"},
        "content": "<p>El impacto de los puritanos en la espiritualidad protestante...</p>",
        "tags": ["Historia", "Puritanos"]
    }
]

# Additional Categories for the Grid
CATEGORIES = [
    {"name": "Teología", "icon": "unicon-捧げ物", "count": 12},
    {"name": "Historia", "icon": "unicon-historical-monument", "count": 8},
    {"name": "Biografías", "icon": "unicon-users", "count": 15},
    {"name": "Espiritualidad", "icon": "unicon-heart-filled", "count": 20},
]

def dashboard(request):
    return render(request, 'index.html', {
        "featured_articles": MOCK_ARTICLES[:6],
        "latest_articles": MOCK_ARTICLES[6:],
        "categories": CATEGORIES
    })

def article_detail(request, slug):
    article = next((a for a in MOCK_ARTICLES if a["slug"] == slug), MOCK_ARTICLES[0])
    return render(request, 'blog-details.html', {"article": article})