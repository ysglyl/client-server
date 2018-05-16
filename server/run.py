from flask import Flask, render_template
from app.face.view import face
from app.db.dbhelper import db

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('app/db/db.cfg')
app.register_blueprint(face, url_prefix='/face')

db.init_app(app)


@app.before_first_request
def init_db():
    db.create_all()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Index')


@app.route('/canvas')
def canvas():
    return render_template('canvas.html')


@app.errorhandler(404)
def handler_error_404(error):
    return '404', 404


@app.errorhandler(500)
def handler_error_500(error):
    return '500', 500


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=True)
