#!/bin/bash

DOMAIN="api.marinapizzas.com.au"
# Or use IP: DOMAIN="170.64.219.198"

echo "=== Testing Pizza Store Backend ==="
echo "Domain: $DOMAIN"
echo ""

echo "1. Health Check:"
HEALTH=$(curl -s http://$DOMAIN/health/)
if [ "$HEALTH" = "OK" ]; then
    echo "✓ Health: OK"
else
    echo "✗ Health: Failed - $HEALTH"
fi
echo ""

echo "2. GraphQL Test (with verbose output):"
GRAPHQL_RESPONSE=$(curl -s -X POST http://$DOMAIN/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}')

if echo "$GRAPHQL_RESPONSE" | grep -q "__typename"; then
    echo "✓ GraphQL: Working"
    echo "Response: $GRAPHQL_RESPONSE"
elif echo "$GRAPHQL_RESPONSE" | grep -q "doctype"; then
    echo "✗ GraphQL: Returned HTML (error page)"
    echo "Response preview:"
    echo "$GRAPHQL_RESPONSE" | head -10
else
    echo "? GraphQL: Unexpected response"
    echo "Response: $GRAPHQL_RESPONSE"
fi
echo ""

echo "3. GraphQL Test (Products Query):"
PRODUCTS=$(curl -s -X POST http://$DOMAIN/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ products { id name price } }"}')

if echo "$PRODUCTS" | grep -q "products"; then
    echo "✓ Products Query: Working"
    echo "$PRODUCTS" | head -5
else
    echo "? Products Query: Check response"
    echo "$PRODUCTS" | head -10
fi
echo ""

echo "4. Admin Panel:"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/admin/)
if [ "$ADMIN_STATUS" = "200" ] || [ "$ADMIN_STATUS" = "301" ] || [ "$ADMIN_STATUS" = "302" ]; then
    echo "✓ Admin: Accessible (HTTP $ADMIN_STATUS)"
    echo "   Open in browser: http://$DOMAIN/admin/"
else
    echo "✗ Admin: Failed (HTTP $ADMIN_STATUS)"
fi
echo ""

echo "5. Static Files:"
STATIC=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/static/admin/css/base.css)
if [ "$STATIC" = "200" ]; then
    echo "✓ Static Files: Working"
else
    echo "? Static Files: HTTP $STATIC"
fi
echo ""

echo "=== Test Complete ==="
echo ""
echo "If GraphQL returned HTML, check:"
echo "  - CORS settings in .env"
echo "  - ALLOWED_HOSTS includes the domain"
echo "  - Server logs: sudo tail -50 /var/www/pizza-store-backend/logs/gunicorn-error.log"

