# Search System - Frontend Integration Guide

## Overview

Advanced fuzzy search system with autocomplete suggestions, relevance scoring, and order search. Supports typo tolerance and intelligent matching.

---

## 🔍 **Features**

- **Fuzzy matching** — Finds results even with typos
- **Relevance scoring** — Best matches appear first
- **Autocomplete** — Suggestions while typing
- **Multi-field search** — Searches name, description, category, tags
- **Order search** — Search orders by number, customer info
- **Popular searches** — Trending/common search terms

---

## 📋 **GraphQL Types**

### SearchSuggestionItemType

```graphql
type SearchSuggestionItemType {
  type: String!         # 'product', 'category', or 'tag'
  id: ID!              # ID of the item
  text: String!        # Display text
  category: String     # Category name (products only)
  slug: String         # URL slug (categories/tags)
  score: Int!          # Relevance score (0-100)
}
```

### SearchSuggestionsType

```graphql
type SearchSuggestionsType {
  query: String!                              # Original query
  suggestions: [SearchSuggestionItemType!]!   # All suggestions
  products: [SearchSuggestionItemType!]!      # Product suggestions only
  categories: [SearchSuggestionItemType!]!    # Category suggestions only
  tags: [SearchSuggestionItemType!]!          # Tag suggestions only
  totalCount: Int!                            # Total count
}
```

### PopularSearchType

```graphql
type PopularSearchType {
  text: String!     # Search term
  type: String!     # 'category' or 'tag'
  slug: String!     # URL slug
}
```

---

## 🔎 **Product Search Queries**

### 1. Fuzzy Search (Recommended)

Advanced search with typo tolerance and relevance scoring.

```graphql
query FuzzySearch($query: String!, $limit: Int, $includeUnavailable: Boolean) {
  fuzzySearch(query: $query, limit: $limit, includeUnavailable: $includeUnavailable) {
    id
    name
    slug
    basePrice
    currentPrice
    isOnSale
    discountPercentage
    imageUrl
    category {
      id
      name
      slug
    }
    tags {
      id
      name
    }
    averageRating
    ratingCount
  }
}
```

**Variables:**
```json
{
  "query": "margrita",
  "limit": 20,
  "includeUnavailable": false
}
```

**Notes:**
- Handles typos: "margrita" → finds "Margherita"
- Handles partial: "pep" → finds "Pepperoni"
- Sorted by relevance score

---

### 2. Search Suggestions (Autocomplete)

Get suggestions while user types.

```graphql
query SearchSuggestions($query: String!, $limit: Int) {
  searchSuggestions(query: $query, limit: $limit) {
    query
    totalCount
    suggestions {
      type
      id
      text
      category
      slug
      score
    }
    products {
      id
      text
      category
      score
    }
    categories {
      id
      text
      slug
      score
    }
    tags {
      id
      text
      slug
      score
    }
  }
}
```

**Variables:**
```json
{
  "query": "piz",
  "limit": 10
}
```

**Response:**
```json
{
  "data": {
    "searchSuggestions": {
      "query": "piz",
      "totalCount": 8,
      "suggestions": [
        { "type": "category", "id": "1", "text": "Pizza", "slug": "pizza", "score": 90 },
        { "type": "product", "id": "5", "text": "Pepperoni Pizza", "category": "Pizza", "score": 80 },
        { "type": "tag", "id": "2", "text": "Meat Pizzas", "slug": "meat-pizzas", "score": 65 }
      ],
      "products": [...],
      "categories": [...],
      "tags": [...]
    }
  }
}
```

---

### 3. Popular Searches

Get trending/popular search terms for search page.

```graphql
query PopularSearches {
  popularSearches {
    text
    type
    slug
  }
}
```

**Response:**
```json
{
  "data": {
    "popularSearches": [
      { "text": "Pizza", "type": "category", "slug": "pizza" },
      { "text": "Pasta", "type": "category", "slug": "pasta" },
      { "text": "Meat Pizzas", "type": "tag", "slug": "meat-pizzas" },
      { "text": "Vegetarian", "type": "tag", "slug": "vegetarian" }
    ]
  }
}
```

---

### 4. Basic Search (Simple)

Simple contains-based search (use `fuzzySearch` for better results).

```graphql
query BasicSearch($search: String!) {
  searchProducts(search: $search) {
    id
    name
    basePrice
    imageUrl
  }
}
```

---

## 📦 **Order Search Query**

Search orders by order number, customer name, email, or phone (staff/admin only).

```graphql
query SearchOrders($query: String!, $limit: Int) {
  searchOrders(query: $query, limit: $limit) {
    id
    orderNumber
    customerName
    customerEmail
    customerPhone
    status
    statusDisplay
    orderType
    orderTypeDisplay
    total
    createdAt
    items {
      productName
      quantity
      subtotal
    }
  }
}
```

**Variables:**
```json
{
  "query": "john",
  "limit": 20
}
```

**Search Examples:**
```json
// Search by order number
{ "query": "ORD-20240115-ABC123" }

// Search by customer name (fuzzy)
{ "query": "john" }

// Search by partial order number
{ "query": "ABC123" }

// Search by email
{ "query": "john@example.com" }

// Search by phone
{ "query": "555-1234" }
```

---

## 💡 **Frontend Implementation**

### React Search Component

```typescript
import { useState, useEffect, useCallback } from 'react';
import { useQuery, useLazyQuery } from '@apollo/client';
import debounce from 'lodash/debounce';

// Queries
const SEARCH_SUGGESTIONS = gql`
  query SearchSuggestions($query: String!, $limit: Int) {
    searchSuggestions(query: $query, limit: $limit) {
      suggestions {
        type
        id
        text
        category
        slug
        score
      }
    }
  }
`;

const FUZZY_SEARCH = gql`
  query FuzzySearch($query: String!, $limit: Int) {
    fuzzySearch(query: $query, limit: $limit) {
      id
      name
      slug
      basePrice
      currentPrice
      isOnSale
      imageUrl
      category {
        name
      }
    }
  }
`;

const POPULAR_SEARCHES = gql`
  query PopularSearches {
    popularSearches {
      text
      type
      slug
    }
  }
`;

// Search Bar Component
const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const [getSuggestions, { data: suggestionsData }] = useLazyQuery(SEARCH_SUGGESTIONS);
  const { data: popularData } = useQuery(POPULAR_SEARCHES);
  
  // Debounced suggestion fetch
  const debouncedFetch = useCallback(
    debounce((searchQuery: string) => {
      if (searchQuery.length >= 2) {
        getSuggestions({ variables: { query: searchQuery, limit: 8 } });
      }
    }, 300),
    []
  );
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setShowSuggestions(true);
    debouncedFetch(value);
  };
  
  const handleSuggestionClick = (suggestion: any) => {
    if (suggestion.type === 'product') {
      // Navigate to product page
      window.location.href = `/product/${suggestion.id}`;
    } else if (suggestion.type === 'category') {
      window.location.href = `/category/${suggestion.slug}`;
    } else if (suggestion.type === 'tag') {
      window.location.href = `/tag/${suggestion.slug}`;
    }
    setShowSuggestions(false);
  };
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(query)}`;
    }
  };
  
  return (
    <div className="search-container">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => setShowSuggestions(true)}
          placeholder="Search pizzas, pasta, drinks..."
          autoComplete="off"
        />
        <button type="submit">Search</button>
      </form>
      
      {showSuggestions && (
        <div className="suggestions-dropdown">
          {query.length < 2 && popularData?.popularSearches && (
            <div className="popular-searches">
              <h4>Popular Searches</h4>
              {popularData.popularSearches.map((item: any, index: number) => (
                <button
                  key={index}
                  onClick={() => setQuery(item.text)}
                  className="popular-item"
                >
                  {item.text}
                </button>
              ))}
            </div>
          )}
          
          {query.length >= 2 && suggestionsData?.searchSuggestions?.suggestions && (
            <ul className="suggestions-list">
              {suggestionsData.searchSuggestions.suggestions.map((suggestion: any) => (
                <li
                  key={`${suggestion.type}-${suggestion.id}`}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <span className={`suggestion-type ${suggestion.type}`}>
                    {suggestion.type === 'product' ? '🍕' : 
                     suggestion.type === 'category' ? '📁' : '🏷️'}
                  </span>
                  <span className="suggestion-text">{suggestion.text}</span>
                  {suggestion.category && (
                    <span className="suggestion-category">in {suggestion.category}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};
```

### Search Results Page

```typescript
const SearchResultsPage = () => {
  const searchParams = new URLSearchParams(window.location.search);
  const query = searchParams.get('q') || '';
  
  const { data, loading, error } = useQuery(FUZZY_SEARCH, {
    variables: { query, limit: 40 },
    skip: !query
  });
  
  if (loading) return <div>Searching...</div>;
  if (error) return <div>Error searching</div>;
  
  const results = data?.fuzzySearch || [];
  
  return (
    <div className="search-results">
      <h1>Search Results for "{query}"</h1>
      <p>{results.length} products found</p>
      
      {results.length === 0 ? (
        <div className="no-results">
          <p>No products found for "{query}"</p>
          <p>Try:</p>
          <ul>
            <li>Check spelling</li>
            <li>Use more general terms</li>
            <li>Browse our categories</li>
          </ul>
        </div>
      ) : (
        <div className="product-grid">
          {results.map((product: any) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Order Search (Admin)

```typescript
const OrderSearch = () => {
  const [query, setQuery] = useState('');
  const [searchOrders, { data, loading }] = useLazyQuery(gql`
    query SearchOrders($query: String!, $limit: Int) {
      searchOrders(query: $query, limit: $limit) {
        id
        orderNumber
        customerName
        customerEmail
        status
        statusDisplay
        total
        createdAt
      }
    }
  `);
  
  const handleSearch = useCallback(
    debounce((q: string) => {
      if (q.length >= 2) {
        searchOrders({ variables: { query: q, limit: 20 } });
      }
    }, 300),
    []
  );
  
  return (
    <div className="order-search">
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          handleSearch(e.target.value);
        }}
        placeholder="Search orders by number, name, email..."
      />
      
      {loading && <div>Searching...</div>}
      
      {data?.searchOrders && (
        <table>
          <thead>
            <tr>
              <th>Order #</th>
              <th>Customer</th>
              <th>Email</th>
              <th>Status</th>
              <th>Total</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {data.searchOrders.map((order: any) => (
              <tr key={order.id}>
                <td>{order.orderNumber}</td>
                <td>{order.customerName}</td>
                <td>{order.customerEmail}</td>
                <td>{order.statusDisplay}</td>
                <td>${order.total}</td>
                <td>{new Date(order.createdAt).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
```

---

## 🎯 **Search Scoring Logic**

The fuzzy search uses relevance scoring to rank results:

| Match Type | Score |
|------------|-------|
| Exact name match | +100 |
| Name contains query | +80 |
| Query contains name | +70 |
| Fuzzy name match | 0-60 (based on similarity) |
| Exact word match in name | +20 |
| Prefix word match | +15 |
| Similar word (80%+) | +10 |
| Description contains query | +30 |
| Fuzzy description match | 0-20 |
| Category match | +25 |
| Tag match | +20 |
| Featured product | +10 |
| High rating (4.5+) | +5 |
| Good rating (4.0+) | +3 |

---

## 🔧 **Fuzzy Matching Examples**

| User Types | Finds |
|------------|-------|
| "margrita" | Margherita |
| "pep" | Pepperoni |
| "chiken" | Chicken |
| "veg" | Vegetarian, Veggie Supreme |
| "hawain" | Hawaiian |
| "meat lover" | Meat Lovers |
| "bbq" | BBQ Chicken |

---

## ⚡ **Performance Tips**

1. **Debounce autocomplete** — Wait 300ms after user stops typing
2. **Limit suggestions** — 8-10 suggestions is optimal
3. **Cache popular searches** — They rarely change
4. **Min query length** — 2 characters minimum for suggestions
5. **Use fuzzySearch for results** — Better than basic search

---

## 📝 **Complete GraphQL Operations**

```graphql
# Fuzzy search products
query FuzzySearch($query: String!, $limit: Int, $includeUnavailable: Boolean) {
  fuzzySearch(query: $query, limit: $limit, includeUnavailable: $includeUnavailable) {
    id
    name
    slug
    basePrice
    currentPrice
    isOnSale
    discountPercentage
    imageUrl
    category {
      id
      name
      slug
    }
    tags {
      id
      name
    }
    averageRating
  }
}

# Get search suggestions
query SearchSuggestions($query: String!, $limit: Int) {
  searchSuggestions(query: $query, limit: $limit) {
    query
    totalCount
    suggestions {
      type
      id
      text
      category
      slug
      score
    }
    products {
      id
      text
      category
    }
    categories {
      id
      text
      slug
    }
    tags {
      id
      text
      slug
    }
  }
}

# Get popular searches
query PopularSearches {
  popularSearches {
    text
    type
    slug
  }
}

# Search orders (admin/staff only)
query SearchOrders($query: String!, $limit: Int) {
  searchOrders(query: $query, limit: $limit) {
    id
    orderNumber
    customerName
    customerEmail
    customerPhone
    status
    statusDisplay
    orderType
    total
    createdAt
  }
}

# Basic search (simple)
query BasicSearch($search: String!) {
  searchProducts(search: $search) {
    id
    name
    basePrice
    imageUrl
  }
}
```

---

## ✅ **Ready to Use!**

The search system supports:
- ✅ Fuzzy/typo-tolerant search
- ✅ Autocomplete suggestions
- ✅ Relevance scoring
- ✅ Category and tag search
- ✅ Order search for admin
- ✅ Popular searches

Happy searching! 🔍

