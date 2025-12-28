"""
URL configuration for pizza_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.conf import settings
from django.conf.urls.static import static
import json

class CustomGraphQLView(GraphQLView):
    """Custom GraphQL view with better error handling"""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Log errors for debugging
        if response.status_code == 400:
            try:
                data = json.loads(response.content)
                if 'errors' in data:
                    print("\n" + "="*50)
                    print("GRAPHQL ERROR DETAILS:")
                    print("="*50)
                    for error in data['errors']:
                        print(f"Message: {error.get('message', 'Unknown error')}")
                        if 'locations' in error:
                            print(f"Location: {error['locations']}")
                        if 'path' in error:
                            print(f"Path: {error['path']}")
                        if 'extensions' in error:
                            print(f"Extensions: {error['extensions']}")
                        print("-"*50)
                    print("="*50 + "\n")
                else:
                    print(f"400 Error but no 'errors' in response: {data}")
            except Exception as e:
                print(f"Error parsing response: {e}")
                print(f"Response content: {response.content[:500]}")
        
        return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(CustomGraphQLView.as_view(graphiql=True))),  # GraphiQL interface for testing
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
