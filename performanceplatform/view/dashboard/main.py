import config
import requests

from flask import Flask, jsonify, render_template

from module import Module


app = Flask(__name__)
app.debug = True


@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/<path:path>', methods=['GET'])
def dashboard(path):
    root = Module.from_slug(path)

    return render_template('page.html',
        title=root.title,
        content=root.render())


if __name__ == '__main__':
    app.run()
