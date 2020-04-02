from flask import *
import os
from werkzeug.utils import secure_filename
from app import app
import urllib.request

UPLOAD_FOLDER = 'C:\\Users\\zhangxc\\PycharmProjects\\HD Explosion Project\\app\\uploads'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv','txt','xls','pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('ui.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        count = 2
        for file in files:
                if count == 0:
                    break
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    count -= 1
        flash('File(s) successfully uploaded')

        return redirect('/')



        # single upload version
        '''
            if request.method == 'POST':
                # check if the post request has the file part
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('File successfully uploaded')
                    return redirect('/')
                else:
                    flash('Allowed file types are csv,txt,xls')
                    '''


@app.route('/', methods=['POST'])
def save():
    name = request.form['name']

    if request.method == 'POST':
        params = request.data.getlist('params[]')

    return params

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
