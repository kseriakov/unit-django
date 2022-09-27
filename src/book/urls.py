from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from store.views import BookViewSet, auth_github, UserBookRelationView

router = DefaultRouter()
router.register('book', BookViewSet, 'books')
router.register('book-relations', UserBookRelationView, 'relations')

urlpatterns = [
    path('auth/github/', auth_github),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('social_django.urls', namespace='social')),
]
