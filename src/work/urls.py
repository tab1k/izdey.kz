from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('users/', include('users.urls')),
    path('myaccount/', include('myaccount.urls')),
    path('favorites/', include('favorites.urls')),
    path('wallet/', include('wallet.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-panel/', include('admin_app.urls')),
    path('offers/', include('offers.urls')),

    # ALLAUTH
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)