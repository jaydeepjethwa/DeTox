"""Contains configurations helpful throught the project"""

from fastapi.templating import Jinja2Templates

# object for directory containing html templates for views returning template responses
templates = Jinja2Templates(directory="templates")