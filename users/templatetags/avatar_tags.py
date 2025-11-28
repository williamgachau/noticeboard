from django import template
from django.utils.safestring import mark_safe
from urllib.parse import quote

register = template.Library()


def _initials_for(user):
    parts = []
    if getattr(user, 'first_name', None):
        parts.append(user.first_name[0].upper())
    if getattr(user, 'last_name', None):
        parts.append(user.last_name[0].upper())
    if not parts and getattr(user, 'username', None):
        # fallback to first two letters of username
        u = user.username or ''
        parts = [c.upper() for c in u[:2]]
    return ''.join(parts) or 'U'


def _pick_bg_color(name):
    # Choose a background color deterministically from username
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    if not name:
        return colors[0]
    return colors[hash(name) % len(colors)]


@register.filter(name='avatar_url')
def avatar_url(user, size=48):
    """Return a URL for the user's avatar.

    - If the user has a related Student with a `photo` file, return its URL.
    - Otherwise, return a data:image/svg+xml URL containing the user's initials.

    Usage in templates: {{ user|avatar_url:40 }}
    """
    if user is None:
        return ''

    # Prefer an uploaded user photo (CustomUser.photo) if present
    try:
        if getattr(user, 'photo', None) and getattr(user.photo, 'url', None):
            return user.photo.url
    except Exception:
        pass

    # Fallback to Student.photo if present
    try:
        student = getattr(user, 'student', None)
        if student and getattr(student, 'photo', None) and getattr(student.photo, 'url', None):
            return student.photo.url
    except Exception:
        # Defensive: if relation is missing or broken, fall back
        pass

    # Build SVG with initials
    try:
        initials = _initials_for(user)
        bg = _pick_bg_color(user.username if getattr(user, 'username', None) else initials)
        s = int(size)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">'
            f'<rect width="100%" height="100%" fill="{bg}" rx="{s//6}"/>'
            f'<text x="50%" y="50%" dy="0.35em" text-anchor="middle"'
            f' font-family="Helvetica, Arial, sans-serif" font-size="{int(s*0.45)}" fill="#ffffff">{initials}</text>'
            '</svg>'
        )
        data = 'data:image/svg+xml;utf8,' + quote(svg)
        return data
    except Exception:
        from django.templatetags.static import static
        return static('images/default-avatar.svg')
