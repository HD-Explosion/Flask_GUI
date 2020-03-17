from flask import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
