from fastapi.templating import Jinja2Templates

# object for directory containing html templates for views returning template responses
templates = Jinja2Templates(directory="templates")

# helper function to convert auth credentials to dictionary    
def credentials_to_dict(credentials):
    
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
            }