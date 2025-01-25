import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import User

def login_page(request):
    """
    Display the login page with Spotify authentication button.
    """
    return render(request, 'calendar_app/login.html')

def spotify_login(request):
    """
    Redirect user to Spotify's authorization page.
    """
    # Spotify authorization URL
    scope = 'user-read-private user-read-email'
    auth_url = f'https://accounts.spotify.com/authorize?client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scope}'
    return redirect(auth_url)

def spotify_callback(request):
    """
    Handle the callback from Spotify after user authorizes the app.
    """
    code = request.GET.get('code')
    
    # Exchange authorization code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    }
    
    # Get tokens from Spotify
    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()
    
    # Get user info from Spotify
    user_url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f"Bearer {token_info['access_token']}"}
    user_response = requests.get(user_url, headers=headers)
    spotify_user = user_response.json()
    
    # Get or create user in our database
    user, created = User.objects.get_or_create(
        spotify_id=spotify_user['id'],
        defaults={
            'username': spotify_user['email'],
            'email': spotify_user['email'],
        }
    )
    
    # Update tokens
    user.access_token = token_info['access_token']
    user.refresh_token = token_info['refresh_token']
    user.token_expires_at = datetime.now() + timedelta(seconds=token_info['expires_in'])
    user.save()
    
    # Log the user in
    login(request, user)
    return redirect('home')

@login_required
def home(request):
    """
    Display the main calendar page.
    Requires user to be logged in.
    """
    return render(request, 'calendar_app/home.html')

@login_required
def add_song(request):
    """
    Display the add song page.
    Requires user to be logged in.
    """
    return render(request, 'calendar_app/add_song.html')