from django.db import migrations

def create_dummy_essays(apps, schema_editor):
    Essay = apps.get_model('main_florife', 'Essay')
    Category = apps.get_model('main_florife', 'Category')
    Author = apps.get_model('main_florife', 'Author')

    author, _ = Author.objects.get_or_create(
        name='Dr. Alberto Magno',
        defaults={
            'bio': 'Teólogo y filósofo escolástico.',
            'social_handle': '@albertomagno'
        }
    )

    author2, _ = Author.objects.get_or_create(
        name='Prof. Catherine de Sienne',
        defaults={
            'bio': 'Profesora de teología moral.',
            'social_handle': '@catherinesienne'
        }
    )

    cat, _ = Category.objects.get_or_create(name='Teología')
    cat2, _ = Category.objects.get_or_create(name='Contemporáneo')
    cat3, _ = Category.objects.get_or_create(name='Historia')

    Essay.objects.get_or_create(
        slug='analogia-del-ser-tradicion-tomista',
        defaults={
            'title': 'La Analogía del Ser en la tradición Tomista',
            'author': author,
            'category': cat,
            'image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800',
            'content': 'Un análisis exhaustivo sobre cómo la distinción entre esencia y existencia fundamenta la posibilidad de un conocimiento racional de lo divino, rescatando las fuentes originales del siglo XIII para el diálogo filosófico actual. Este ensayo explora las implicaciones metafísicas del pensamiento de Santo Tomás de Aquino y su relevancia en el debate contemporáneo sobre la naturaleza del ser.',
            'is_featured': True,
            'status': 'liberado',
            'tags': ['tomismo', 'metafísica', 'analogía']
        }
    )

    Essay.objects.get_or_create(
        slug='virtud-bien-comun-secunda-secundae',
        defaults={
            'title': 'Virtud y Bien Común: Una relectura de la Secunda Secundae',
            'author': author2,
            'category': cat2,
            'image_url': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800',
            'content': 'Explorando la relevancia de la justicia distributiva en el pensamiento de Aquino y su aplicación práctica en las estructuras sociales contemporáneas. El ensayo profundiza en el concepto de "Habitus" como motor de cambio social y analiza cómo las virtudes cardinales pueden transformar las instituciones modernas.',
            'is_featured': False,
            'status': 'liberado',
            'tags': ['ética', 'virtud', 'bien común']
        }
    )

    Essay.objects.get_or_create(
        slug='intelecto-agente-iluminacion-divina',
        defaults={
            'title': 'El Intelecto Agente y la Iluminación Divina',
            'author': author,
            'category': cat3,
            'image_url': 'https://images.unsplash.com/photo-1456513080510-7bf3a7f531ad?w=800',
            'content': 'Debates sobre la gnoseología medieval: una comparación crítica entre las posturas agustinianas y el aristotelismo cristiano. ¿Cómo interactúa la luz natural de la razón con la revelación en el acto del entendimiento? Este ensayo examina las tensiones entre fe y razón en la teoría del conocimiento medieval.',
            'is_featured': True,
            'status': 'liberado',
            'tags': ['epistemología', 'intelecto', 'iluminación']
        }
    )

def remove_dummy_essays(apps, schema_editor):
    Essay = apps.get_model('main_florife', 'Essay')
    Essay.objects.filter(slug__in=[
        'analogia-del-ser-tradicion-tomista',
        'virtud-bien-comun-secunda-secundae',
        'intelecto-agente-iluminacion-divina'
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('main_florife', '0014_essay_model'),
    ]

    operations = [
        migrations.RunPython(create_dummy_essays, remove_dummy_essays),
    ]
