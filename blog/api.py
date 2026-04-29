from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import BlogPost, Category
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_blog_posts(request):
    """
    API WordPress: lista articoli recenti per homepage WP.
    Cacheata 1 ora per performance.
    """
    cache_key = 'wp_blog_posts_recent'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    posts = BlogPost.objects.filter(
        is_published=True
    ).select_related('category').order_by('-publish_date')[:10]
    
    data = [{
        'slug': p.slug,
        'title': p.get_title,
        'excerpt': (p.get_content[:150] + '...') if len(p.get_content) > 150 else p.get_content,
        'date': p.publish_date.strftime('%d %B %Y'),
        'category': p.category.get_name if p.category else 'Generale',
        'url': request.build_absolute_uri(f'/blog/{p.slug}/'),
        'image': request.build_absolute_uri('/static/images/dog-training.jpg'),
    } for p in posts]
    
    cache.set(cache_key, data, 3600)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_blog_categories(request):
    """API WordPress: categorie per menu"""
    categories = Category.objects.all()
    data = [{
        'name': c.get_name,
        'slug': c.slug,
        'count': c.blogpost_set.filter(is_published=True).count(),
    } for c in categories]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_blog_stats(request):
    """API WordPress: statistiche per sidebar"""
    total = BlogPost.objects.filter(is_published=True).count()
    recent = BlogPost.objects.filter(
        is_published=True
    ).order_by('-publish_date').first()
    
    return Response({
        'total_posts': total,
        'latest_post': recent.get_title if recent else None,
        'latest_slug': recent.slug if recent else None,
        'latest_date': recent.publish_date.strftime('%d %B %Y') if recent else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_blog_recent(request):
    """API WordPress: 5 articoli recenti per sidebar"""
    posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-publish_date')[:5]
    
    data = [{
        'title': p.get_title,
        'slug': p.slug,
        'date': p.publish_date.strftime('%d %B %Y'),
    } for p in posts]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_dog_tools(request):
    """API WordPress: strumenti per homepage"""
    tools = [
        {
            'slug': 'food-calculator',
            'name': 'Calcolatore Cibo',
            'icon': '🍖',
            'desc': 'Quanto deve mangiare il tuo cane? Calcola la porzione giusta.',
            'url': '/app/tool/food-calculator/',
        },
        {
            'slug': 'age-calculator',
            'name': 'Età in Anni Umani',
            'icon': '🎂',
            'desc': 'Scopri quanti anni ha il tuo cane in anni umani.',
            'url': '/app/tool/age-calculator/',
        },
        {
            'slug': 'dog-quiz',
            'name': 'Quiz Linguaggio',
            'icon': '🧠',
            'desc': 'Quanto conosci il linguaggio del tuo cane? Mettiti alla prova.',
            'url': '/app/tool/dog-quiz/',
        },
        {
            'slug': 'heart-recorder',
            'name': 'Registratore Cardiaco',
            'icon': '❤️',
            'desc': 'Registra e analizza i battiti del cuore del tuo cane',
            'url': '/app/tool/heart-recorder/',
        },
    ]
    return Response(tools)


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_problems(request):
    """API WordPress: problemi comuni"""
    from knowledge.models import Problem
    problems = Problem.objects.all()[:6]
    data = [{
        'title': p.get_title(),
        'slug': p.slug,
        'icon': p.get_icon(),
        'severity': p.get_severity_display(),
        'url': request.build_absolute_uri(f'/problemi/{p.slug}/'),
    } for p in problems]
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def wp_newsletter_subscribe(request):
    """
    API WordPress: sottoscrizione newsletter.
    Delega a Django per processare.
    """
    email = request.data.get('email', '')
    source = request.data.get('source', 'wordpress')
    
    if not email or '@' not in email:
        return Response({
            'success': False,
            'message': 'Email non valida'
        }, status=400)
    
    # Usa la logica Django esistente
    from marketing.models import NewsletterSubscriber
    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'source': source}
        )
        if not created:
            return Response({
                'success': True,
                'message': 'Sei già iscritto alla newsletter!'
            })
        
        return Response({
            'success': True,
            'message': 'Iscrizione completata! Riceverai le nostre guide.'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Errore: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_api_health(request):
    """API WordPress: health check"""
    return Response({
        'status': 'ok',
        'service': 'blog-api',
        'version': '1.0.0',
    })


# ---- Blog Detail rimane su Django (non redirect) ----
@api_view(['GET'])
@permission_classes([AllowAny])
def wp_blog_detail_meta(request, slug):
    """
    API WordPress: metadata articolo per SEO condiviso.
    Usato da WP per canonical/alternate links.
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return Response({
        'title': post.get_title,
        'meta_description': post.meta_description or post.get_content[:155],
        'image': request.build_absolute_uri(post.get_image_url()),
        'url': request.build_absolute_uri(f'/blog/{post.slug}/'),
        'publish_date': post.publish_date.isoformat(),
        'modified_date': post.updated_at.isoformat(),
        'author': 'Alessio',
        'category': post.category.get_name if post.category else None,
    })
