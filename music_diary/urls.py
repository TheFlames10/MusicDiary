from django.contrib import admin
from django.urls import path
from calendar_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login'),
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('home/', views.home, name='home'),
    path('song/add', views.add_song, name='add_song'),
]