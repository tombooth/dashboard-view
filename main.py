import config

from flask import Flask, jsonify, render_template

from dashboard.module import Module


app = Flask(__name__)
app.debug = True


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
        asset_path='/static/govuk-template/')


if __name__ == '__main__':
    app.run()
