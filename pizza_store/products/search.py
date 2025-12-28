"""
Fuzzy Search Module for Pizza Store
Provides intelligent search with suggestions, fuzzy matching, and relevance scoring.
"""

from difflib import SequenceMatcher
from django.db.models import Q, Value, IntegerField, Case, When, F
from django.db.models.functions import Lower
import re


def similarity_ratio(str1, str2):
    """Calculate similarity ratio between two strings (0.0 to 1.0)"""
    if not str1 or not str2:
        return 0.0
    str1_lower = str1.lower()
    str2_lower = str2.lower()
    return SequenceMatcher(None, str1_lower, str2_lower).ratio()


def fuzzy_match(query, text, threshold=0.4):
    """Check if query fuzzy matches text with given threshold"""
    if not query or not text:
        return False
    
    query_lower = query.lower()
    text_lower = text.lower()
    
    # Exact match
    if query_lower in text_lower:
        return True
    
    # Word-level matching
    query_words = query_lower.split()
    text_words = text_lower.split()
    
    for q_word in query_words:
        for t_word in text_words:
            if similarity_ratio(q_word, t_word) >= threshold:
                return True
            # Prefix matching
            if t_word.startswith(q_word) or q_word.startswith(t_word):
                return True
    
    # Overall similarity
    return similarity_ratio(query_lower, text_lower) >= threshold


def calculate_relevance_score(query, product):
    """Calculate relevance score for a product based on query"""
    query_lower = query.lower()
    score = 0
    
    # Exact name match (highest priority)
    if query_lower == product.name.lower():
        score += 100
    # Name contains query
    elif query_lower in product.name.lower():
        score += 80
    # Query contains name
    elif product.name.lower() in query_lower:
        score += 70
    # Fuzzy name match
    else:
        name_similarity = similarity_ratio(query_lower, product.name.lower())
        score += int(name_similarity * 60)
    
    # Word matching in name
    query_words = query_lower.split()
    name_words = product.name.lower().split()
    for q_word in query_words:
        for n_word in name_words:
            if q_word == n_word:
                score += 20
            elif n_word.startswith(q_word):
                score += 15
            elif similarity_ratio(q_word, n_word) >= 0.8:
                score += 10
    
    # Description match
    if product.description:
        desc_lower = product.description.lower()
        if query_lower in desc_lower:
            score += 30
        else:
            desc_similarity = similarity_ratio(query_lower, desc_lower[:100])
            score += int(desc_similarity * 20)
    
    # Category match
    if product.category and query_lower in product.category.name.lower():
        score += 25
    
    # Tag match
    for tag in product.tags.all():
        if query_lower in tag.name.lower():
            score += 20
            break
    
    # Boost for featured products
    if product.is_featured:
        score += 10
    
    # Boost for highly rated products
    if product.average_rating >= 4.5:
        score += 5
    elif product.average_rating >= 4.0:
        score += 3
    
    return score


def search_products(query, limit=20, include_unavailable=False):
    """
    Advanced fuzzy search for products.
    Returns products sorted by relevance score.
    """
    from .models import Product
    
    if not query or len(query.strip()) == 0:
        return []
    
    query = query.strip()
    query_lower = query.lower()
    
    # Base queryset
    queryset = Product.objects.all()
    if not include_unavailable:
        queryset = queryset.filter(is_available=True)
    
    # Prefetch related for performance
    queryset = queryset.select_related('category').prefetch_related('tags')
    
    # Build search filters
    # Direct matches using Django ORM
    direct_matches = queryset.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(tags__name__icontains=query)
    ).distinct()
    
    # Get all products for fuzzy matching (only if direct matches are few)
    results = list(direct_matches)
    result_ids = {p.id for p in results}
    
    if len(results) < limit:
        # Perform fuzzy matching on remaining products
        remaining = queryset.exclude(id__in=result_ids)
        
        for product in remaining:
            # Check fuzzy match
            if fuzzy_match(query, product.name, 0.5):
                results.append(product)
            elif product.description and fuzzy_match(query, product.description[:200], 0.4):
                results.append(product)
            elif product.category and fuzzy_match(query, product.category.name, 0.6):
                results.append(product)
            else:
                # Check tags
                for tag in product.tags.all():
                    if fuzzy_match(query, tag.name, 0.6):
                        results.append(product)
                        break
            
            if len(results) >= limit * 2:  # Get extra for better sorting
                break
    
    # Calculate relevance scores and sort
    scored_results = [(product, calculate_relevance_score(query, product)) for product in results]
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    return [product for product, score in scored_results[:limit]]


def get_search_suggestions(query, limit=10):
    """
    Get search suggestions/autocomplete for a query.
    Returns a list of suggestion dictionaries.
    """
    from .models import Product, Category, Tag
    
    if not query or len(query.strip()) < 2:
        return []
    
    query = query.strip()
    query_lower = query.lower()
    suggestions = []
    
    # Product name suggestions
    products = Product.objects.filter(
        Q(name__istartswith=query) | Q(name__icontains=query),
        is_available=True
    ).values('id', 'name', 'category__name')[:limit]
    
    for p in products:
        suggestions.append({
            'type': 'product',
            'id': str(p['id']),
            'text': p['name'],
            'category': p['category__name'],
            'score': 100 if p['name'].lower().startswith(query_lower) else 80
        })
    
    # Category suggestions
    categories = Category.objects.filter(
        Q(name__istartswith=query) | Q(name__icontains=query)
    ).values('id', 'name', 'slug')[:5]
    
    for c in categories:
        suggestions.append({
            'type': 'category',
            'id': str(c['id']),
            'text': c['name'],
            'slug': c['slug'],
            'score': 90 if c['name'].lower().startswith(query_lower) else 70
        })
    
    # Tag suggestions
    tags = Tag.objects.filter(
        Q(name__istartswith=query) | Q(name__icontains=query)
    ).values('id', 'name', 'slug')[:5]
    
    for t in tags:
        suggestions.append({
            'type': 'tag',
            'id': str(t['id']),
            'text': t['name'],
            'slug': t['slug'],
            'score': 85 if t['name'].lower().startswith(query_lower) else 65
        })
    
    # Fuzzy suggestions for products (if few direct matches)
    if len([s for s in suggestions if s['type'] == 'product']) < 5:
        all_products = Product.objects.filter(is_available=True).values('id', 'name', 'category__name')[:100]
        for p in all_products:
            if any(s['id'] == str(p['id']) and s['type'] == 'product' for s in suggestions):
                continue
            
            similarity = similarity_ratio(query_lower, p['name'].lower())
            if similarity >= 0.5:
                suggestions.append({
                    'type': 'product',
                    'id': str(p['id']),
                    'text': p['name'],
                    'category': p['category__name'],
                    'score': int(similarity * 60)
                })
    
    # Sort by score and limit
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    # Remove duplicates and limit
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        key = (s['type'], s['id'])
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)
            if len(unique_suggestions) >= limit:
                break
    
    return unique_suggestions


def search_orders(query, user=None, limit=20):
    """
    Search orders by order number, customer name, email, or phone.
    """
    from orders.models import Order
    
    if not query or len(query.strip()) == 0:
        return []
    
    query = query.strip()
    
    # Base queryset
    queryset = Order.objects.all()
    
    # Build filters
    filters = (
        Q(order_number__icontains=query) |
        Q(customer_name__icontains=query) |
        Q(customer_email__icontains=query) |
        Q(customer_phone__icontains=query) |
        Q(delivery_address__icontains=query)
    )
    
    results = list(queryset.filter(filters).order_by('-created_at')[:limit])
    
    # Fuzzy matching if few results
    if len(results) < limit // 2:
        result_ids = {o.id for o in results}
        remaining = queryset.exclude(id__in=result_ids).order_by('-created_at')[:200]
        
        for order in remaining:
            if (fuzzy_match(query, order.customer_name, 0.6) or
                fuzzy_match(query, order.order_number, 0.7) or
                (order.customer_email and fuzzy_match(query, order.customer_email.split('@')[0], 0.6))):
                results.append(order)
                if len(results) >= limit:
                    break
    
    return results[:limit]


def get_popular_searches():
    """
    Get popular/trending search terms.
    This could be enhanced with actual search tracking.
    """
    from .models import Category, Tag
    
    popular = []
    
    # Categories as popular searches
    categories = Category.objects.all()[:6]
    for c in categories:
        popular.append({
            'text': c.name,
            'type': 'category',
            'slug': c.slug
        })
    
    # Tags as popular searches
    tags = Tag.objects.all()[:6]
    for t in tags:
        popular.append({
            'text': t.name,
            'type': 'tag',
            'slug': t.slug
        })
    
    return popular

