"""
WordPress Redirect Middleware
Smista il traffico tra WordPress (marketing) e Django (app).

Pattern:
- WordPress: Home, About, Blog List, Legal Pages (marketing)
- Django: AI Analyzer, Blog Detail, Tools, Community (app)
"""

import re
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class WordPressRedirectMiddleware(MiddlewareMixin):
    """
    Reindirizza le pagine marketing su WordPress,
    mantiene l'app Django per le funzionalità core.
    """
    
    # Pattern URL da MANTENERE su Django
    DJANGO_KEEP = [
        r'^api/',                    # API endpoints
        r'^admin/',                  # Admin Django
        r'^i18n/',                   # Internazionalizzazione
        r'^static/',                 # Static files
        r'^media/',                  # Media files
        r'^accounts/',               # Auth Django/allauth
        r'^cane/',                   # Dog profile
        r'^knowledge/',              # Learning hub
        r'^community/',              # Community/forum
        r'^tool/',                   # Tools interattivi
        r'^analizza/',               # AI analyzer
        r'^ping/',                   # Health check
        r'^health/',                 # Health check
        r'^sitemap\.xml$',          # Sitemap
        r'^robots\.txt$',           # Robots
        r'^manifest\.json$',        # PWA manifest
        r'^service-worker\.js$',    # Service worker
        r'^unsubscribe/',            # Unsubscribe newsletter
    ]
    
    # Redirect permanenti: vecchio URL Django → nuovo URL WordPress
    # Formato: {vecchio_path: nuovo_path_wordpress}
    WP_REDIRECTS = {
        '/chi-sono/': '/about/',
        '/privacy/': '/privacy-policy/',
        '/terms/': '/termini-servizio/',
        '/cookie/': '/cookie-policy/',
    }
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.django_patterns = [re.compile(p) for p in self.DJANGO_KEEP]
    
    def should_keep_on_django(self, path):
        """Verifica se il path deve rimanere su Django"""
        return any(p.match(path) for p in self.django_patterns)
    
    def __call__(self, request):
        path = request.path
        
        # 1. DEBUG: salta middleware in sviluppo
        if settings.DEBUG:
            return self.get_response(request)
        
        # 2. Verifica se deve rimanere su Django
        if self.should_keep_on_django(path):
            return self.get_response(request)
        
        # 3. Redirect permanenti verso WordPress
        if path in self.WP_REDIRECTS:
            wp_base = getattr(settings, 'WP_BASE_URL', '')
            if wp_base:
                new_url = wp_base.rstrip('/') + self.WP_REDIRECTS[path]
                return HttpResponsePermanentRedirect(new_url)
        
        # 4. Homepage → WordPress
        if path in ['/', '/it/', '/en/', '/it', '/en']:
            wp_base = getattr(settings, 'WP_BASE_URL', '')
            if wp_base:
                return HttpResponsePermanentRedirect(wp_base)
        
        # 5. Blog LIST → WordPress (ma DETAIL resta su Django)
        if path == '/blog/' or path.startswith('/blog?'):
            wp_base = getattr(settings, 'WP_BASE_URL', '')
            if wp_base:
                return HttpResponsePermanentRedirect(wp_base + '/blog/')
        
        # 6. Pagina "Termini" vecchia → nuova WP
        if path == '/termini/' or path == '/termini-servizio/':
            wp_base = getattr(settings, 'WP_BASE_URL', '')
            if wp_base:
                return HttpResponsePermanentRedirect(wp_base + '/termini/')
        
        # 7. Tutto il resto resta su Django
        return self.get_response(request)


class WordPressHeaderInjector(MiddlewareMixin):
    """
    Inject header/footer coerenti tra WordPress e Django.
    Legge configurazione comune da API/cache.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.wp_base = getattr(settings, 'WP_BASE_URL', '')
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Aggiunge header solo per pagine HTML
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            # Aggiunge link preload per risorse condivise
            response['Link'] = '<' + self.wp_base + '/wp-content/themes/vivere-child/fonts.css>; rel=preload; as=style; crossorigin'
        
        return response
