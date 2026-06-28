import bleach


class HTMLSanitizer:
    ALLOWED_TAGS = [
        'p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'br',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'
    ]
    ALLOWED_ATTRIBUTES = {
        'a': ['href'],
        '*': ['class', 'id']
    }

    @classmethod
    def sanitize(cls, html_string: str) -> str:
        if not html_string:
            return ''
        cleaned = bleach.clean(
            html_string,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            protocols=['http', 'https', 'mailto'],
            strip=True
        )
        cleaned = bleach.linkify(cleaned, skip_tags=['pre', 'code'])
        return cleaned
