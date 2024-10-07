from .app import app
from control.views import views
from urllib.parse import quote
app.register_blueprint(views)

def urlencode_filter(s):
    return quote(s)

app.jinja_env.filters['urlencode'] = urlencode_filter
