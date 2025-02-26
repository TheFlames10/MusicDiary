import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.http import JsonResponse
import requests
from datetime import datetime, timedelta
import random
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import User

# Add your Spotify API credentials
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET
))

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

@login_required
def search_songs(request):
    """
    Search for songs using the Spotify API.
    Requires user to be logged in.
    """
    query = request.GET.get('q')
    if query:
        results = spotify.search(q=query, type='track', limit=10)
        tracks = results['tracks']['items']
        songs = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'albumCover': track['album']['images'][0]['url']} for track in tracks]
        return JsonResponse(songs, safe=False)
    return JsonResponse([], safe=False)

@login_required
def discover(request):
    """
    Display the discover page with personalized song recommendations.
    Requires user to be logged in.
    """
    # Get songs from local storage (we'll need to modify this to use a database later)
    songs = request.session.get('songs', {})
    
    # Get user's saved songs and analyze them
    user_tracks = []
    genres = {}
    
    for date, song in songs.items():
        # Get full track details from Spotify
        track_results = spotify.search(q=f"track:{song['title']}", type='track', limit=1)
        if track_results['tracks']['items']:
            track = track_results['tracks']['items'][0]
            user_tracks.append(track['id'])
            
            # Get artist genres
            artist_id = track['artists'][0]['id']
            artist = spotify.artist(artist_id)
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1
    
    recommendations = {}
    
    # Get recommendations based on user's calendar songs
    if user_tracks:
        calendar_recommendations = spotify.recommendations(
            seed_tracks=user_tracks[:5],
            limit=15
        )
        recommendations['calendar'] = calendar_recommendations['tracks']
    
    # Get recommendations based on top genre
    top_genre = max(genres.items(), key=lambda x: x[1])[0] if genres else None
    if top_genre:
        genre_recommendations = spotify.recommendations(
            seed_genres=[top_genre],
            limit=15
        )
        recommendations['genre'] = genre_recommendations['tracks']
    
    # Get random popular tracks
    random_tracks = spotify.search(
        q='year:2024',
        type='track',
        limit=15,
        offset=random.randint(0, 100)
    )
    recommendations['random'] = random_tracks['tracks']['items']
    
    return render(request, 'calendar_app/discover.html', {'recommendations': recommendations})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()
        return redirect('profile')
    return render(request, 'calendar_app/profile.html')