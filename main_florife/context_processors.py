from django.conf import settings


def seo(request):
    return {
        'seo_title': 'Florilegio de la Fe - Teología, Historia y Biografías Cristianas',
        'seo_description': 'Profundiza en la intimidad con Dios a través de artículos de teología, historia de la iglesia, biografías cristianas y estudio bíblico.',
        'seo_image': 'images/ff.jpg',
    }
