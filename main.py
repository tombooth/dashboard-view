
import config, scss
from flask import Flask, jsonify, render_template
from flask.ext.assets import Environment, Bundle
from dashboard.module import Module
# from lib.filters import *
# from lib.slugify import slugify

# jinja.filters['slugify'] = slugify

app = Flask(__name__)
app.debug = True

assets = Environment(app)
assets.url = app.static_url_path
scss.config.LOAD_PATHS = [
    '../govuk_frontend_toolkit/stylesheets/',
    '../govuk_elements/public/sass/',
]
scss = Bundle('css/main.scss', filters='pyscss', output='css/main.css')
assets.register('scss_all', scss)

@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/static/<path:path>', methods=['GET'])
def static_files():
    return send_from_directory(config.STATIC_PATH, path)


@app.route('/<path:path>', methods=['GET'])
def dashboard(path):
    root = Module.from_slug(path)
    root.fetch()
    return render_template('dashboard.html',
        title=root.title,
        content=root.render(),
        govuk_template_path='/static/govuk-template/')


if __name__ == '__main__':
    app.run()
