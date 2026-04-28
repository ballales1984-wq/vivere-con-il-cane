from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='reputation_badge')
def reputation_badge(reputation):
    points = reputation.points if hasattr(reputation, 'points') else 0
    
    if points >= 1000:
        level = 'Leggenda'
        badge = '👑'
        color = '#b8860b'
    elif points >= 500:
        level = 'Esperto'
        badge = '⭐'
        color = '#dc2626'
    elif points >= 200:
        level = 'Veterano'
        badge = '🏅'
        color = '#059669'
    elif points >= 100:
        level = 'Appassionato'
        badge = '🥇'
        color = '#7c3aed'
    elif points >= 50:
        level = 'Contributore'
        badge = '🏅'
        color = '#2563eb'
    else:
        level = 'Membro'
        badge = '🌟'
        color = '#475569'
    
    html = f'<span style="color: {color};">{badge}</span> <strong>{level}</strong> ({points} pts)'
    return mark_safe(html)
