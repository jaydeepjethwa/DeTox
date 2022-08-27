"""Authorization module for connecting youtube account using google oauth 2.0."""
 
def credentials_to_dict(credentials):
    """Helper function to convert auth credentials to dictionary.

    Args:
        credentials (Credentials): Google OAuth 2.0 Credentials object.

    Returns:
        dict: Credentials converted to python dictionary
    """
    
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
            }
    
from .google_oauth2 import auth_router