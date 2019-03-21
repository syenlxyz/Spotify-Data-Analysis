### PSTAT 235 Spotify Data Analysis
### Author: Syen Yang Lu, Mingxi Chen
### Spotify Web APi request in Python

import base64
import requests

# Client Credentials for request token
# Please do not distribute these API keys anywhere in the public
apikey = {
    'CLIENT_ID':'Your Own Client ID',
    'CLIENT_SECRET':'Your Own Client Secret'
}

def get_access_token():
    # Extract Client Credentials
    CLIENT_ID = apikey['CLIENT_ID']
    CLIENT_SECRET = apikey['CLIENT_SECRET']
    
    # Convert Client ID and Secret into the required format: <base64 encoded client_id:client_secret>
    CLIENT_CREDENTIALS = ':'.join([CLIENT_ID,CLIENT_SECRET])
    ENCODED_STRING = b'Basic ' + base64.b64encode(CLIENT_CREDENTIALS.encode())

    # Header Parameter
    headers = {
        'Authorization': ENCODED_STRING,
    }

    # Request body parameter
    data = {
      'grant_type': 'client_credentials' # Specify grant type
    }

    # Post request for access token
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data).json()
    token = ' '.join([response['token_type'], response['access_token']]) # Join token type and access token
    return token

def get_genre_seed(ACCESS_TOKEN):
    # Header Parameter
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': ACCESS_TOKEN
    }

    # Get request for genre
    response = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=headers).json()
    return response['genres']

def get_item(GENRE, LIMIT, OFFSET, ACCESS_TOKEN):
    # Header Parameter
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': ACCESS_TOKEN
    }

    # Query Parameter
    params = (
        ('q', ' '.join(['genre:' + GENRE,  # Pull songs from genre one at a time
                        'year:2000-2020'])), # limit the songs between 2000-2020
        ('type', 'track'), # Specify the type of query
        ('market', 'US'), # Country code
        ('limit', LIMIT), # Max number of result to return
        ('offset', OFFSET), # Index of first result to return
    )
        
    # Get request item query
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params).json()
    return response

def get_audio_features(TRACK_ID, ACCESS_TOKEN):
    # Header Parameter
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': ACCESS_TOKEN
    }   

    # Query Parameter
    params = (
        ('ids', TRACK_ID),
    )

    # Get request for audio features
    response = requests.get('https://api.spotify.com/v1/audio-features', headers=headers, params=params).json()
    return response['audio_features']

def get_data(GENRE, LIMIT, OFFSET, ACCESS_TOKEN):
    # Get item with some specification on genre, limit and offset
    response = get_item(GENRE, LIMIT, OFFSET, ACCESS_TOKEN)['tracks']['items']
    
    # Extract IDs from response
    track_id = [x['id'] for x in response]
    artists_id = [';'.join([item['id'] for item in x['artists']]) for x in response]
    album_id = [x['album']['id'] for x in response]
    
    # Extract Names from response
    track_name = [x['name'].replace(',',';') for x in response]
    artists_name = [';'.join([item['name'].replace(',',';') for item in x['artists']]) for x in response]
    album_name = [x['album']['name'].replace(',',';') for x in response]
    
    # Extract track info
    album_type = [x['album']['album_type'] for x in response]
    release_date = [x['album']['release_date'] for x in response]
    release_date_precision = [x['album']['release_date_precision'] for x in response]
    is_explicit = [x['explicit'] for x in response]
    track_popularity = [x['popularity'] for x in response]
    
    # Define a list of genre
    genre = [GENRE for x in range(len(response))] 
    
    # Concatenate the columns
    result = list(zip(
        track_id, artists_id, album_id, track_name, artists_name, album_name,
        album_type, release_date, release_date_precision,
        is_explicit, track_popularity, genre
    ))
    
    # Get audio features for each song
    key_to_drop = ['type', 'id', 'uri', 'track_href', 'analysis_url']
    audio_features = get_audio_features(','.join(track_id), ACCESS_TOKEN)
    audio_features = [[x[key] for key in x.keys() if key not in key_to_drop] for x in audio_features]
    
    # Combine and return the result
    data = [list(result[x]) + audio_features[x] for x in range(len(response))]
    return data

def get_artist_total_follower(ARTIST_ID, ACCESS_TOKEN):  
    # Header Parameter
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': ACCESS_TOKEN
    }    
    
    # Query Parameter
    params = (
        ('ids', ARTIST_ID),
    )
    
    # Get request for number of follower for each artist
    response = requests.get('https://api.spotify.com/v1/artists', headers=headers, params=params).json()
    return [x['followers']['total'] for x in response['artists']]