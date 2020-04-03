from app import app
from flask import render_template, send_file,request
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
import numpy as np
import io
from PIL import Image
from app import HDX_Plots

import os
import urllib.request
from werkzeug.utils import secure_filename



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

@app.route('/', methods=['POST'])
def save():
    name = request.form['name']

    if request.method == 'POST':
        params = request.data.getlist('params[]')

    return params


@app.route('/index')

def index():
    user = {'username': 'Xiaohe'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/ui')
def ui():
    return render_template('ui.html')


@app.route('/error')
def error():
    return render_template('error.html')







@app.route('/plotshow')
def plotshow():
    raw_data = [
    [[255,255,255],[255,255,255],[255,255,255]],
    [[0,0,1],[255,255,255],[0,0,0]],
    [[255,255,255],[0,0,0],[255,255,255]],
    [[100,50,23],[55,23,76],[157,75,32]]
]
    # my numpy array 
    arr = np.array(raw_data)

    # convert numpy array to PIL Image
    img = Image.fromarray(arr.astype('uint8'))

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object
    img.save(file_object, 'PNG')

    # move to beginning of file so `send_file()` it will read from start    
    file_object.seek(0)

    #return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    #return render_template('ui.html',user_image =file_object )

    return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r



ALLOWED_EXTENSIONS = {'csv','txt','xls','pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# @app.route('/plotshow')
# def plotshow():


#     File_name = 'static/files/20191010_djb_H3H4dm.csv'
#     csvFile = open(File_name, "r")
#     reader = cs.reader(csvFile)
#     # Set up time points and states
#     Time_points1 = ['10', '100', '1000', '10000', '100000']
#     States1 = ['H3H4dm', 'RV-H3H4dm']
#     Proteins = ['H32_XENLA']
#     Columns = []
#     # Crate column to store data
#     for Protein in Proteins:
#         Columns.append(Protein)
#         Columns.append(Protein + '_' + 'MaxUptake')
#         for State in States1:
            
#             Columns.append(State)
#             for Time in Time_points1:
#                 Columns.append(Protein + '_' + State + '_' + Time)
#                 Columns.append(Protein + '_' + State + '_' + Time + '_SD')
#     Data1 = pd.DataFrame(columns=Columns)
#     n, i = 0, 0
#     Sequence = ''
#     Sequence_number = ''
#     # Read data form reader to Data
#     for item in reader:
#         if n != 0:
#             if item[0] in Proteins:
#                 if Sequence_number != item[1] + '-' + item[2]:
#                     i += 1
#                     Sequence_number = item[1] + '-' + item[2]
#                     Data1.loc[i, item[0]] = Sequence_number
#                     Data1.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
#                 Time = str(int(float(item[9]) * 60 + 0.5))
#                 State = item[8]
#                 Protein = item[0]
#                 if Time != '0':
#                     Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
#                     Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
#         else:
#             n = n + 1
#     csvFile.close()
#     # Save Data as csv file
#     Data1.to_csv("For plot.csv", index=False, sep=',')

#     K = HDX_Plots.heatmap(Data1, 'H32_XENLA', 'H3H4dm', 'RV-H3H4dm', Time_points1, rotation='H', max=5, step=10, color='rb', min=-5, step2=10,
#                 file_name='FL_ASF1.eps')





#     # create file-object in memory
#     file_object = io.BytesIO()



#     K.savefig(file_object, format='eps')


#     # move to beginning of file so `send_file()` it will read from start    
#     file_object.seek(0)

#     #return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
#     #return render_template('ui.html',user_image =file_object )

#     return send_file(file_object, mimetype='application/postscript', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.eps')
    