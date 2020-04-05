from app import app

from flask import render_template, send_file,request
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
import numpy as np
import io
from PIL import Image
from app import HDX_Plots_for_web
from app import reader
import os
import urllib.request
from werkzeug.utils import secure_filename



@app.route('/')
def ui():
    return render_template('ui.html')

@app.route('/upload_file', methods=['POST']) 
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
                global filename 
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                count -= 1
        flash('File(s) successfully uploaded')

        return redirect('/parameter')

# @app.route('/', methods=['POST'])
# def save():
#     name = request.form['name']

#     if request.method == 'POST':
#         params = request.data.getlist('params[]')

#     return params


@app.route('/index')

def index():
    user = 'Xiaohe'
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




@app.route('/error')
def error():
    return render_template('error.html')






## Create matrix image for testing
# @app.route('/plotshow')




# def plotshow():
#     raw_data = [
#     [[255,255,255],[255,255,255],[255,255,255]],
#     [[0,0,1],[255,255,255],[0,0,0]],
#     [[255,255,255],[0,0,0],[255,255,255]],
#     [[100,50,23],[55,23,76],[157,75,32]]
# ]
#     # my numpy array 
#     arr = np.array(raw_data)

#     # convert numpy array to PIL Image
#     img = Image.fromarray(arr.astype('uint8'))

#     # create file-object in memory
#     file_object = io.BytesIO()

#     # write PNG in file-object
#     img.save(file_object, 'PNG')

#     # move to beginning of file so `send_file()` it will read from start    
#     file_object.seek(0)

#     #return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
#     #return render_template('ui.html',user_image =file_object )

#     return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    

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





@app.route('/parameter')
def parameter():
    names = reader.fileread(filename)
    return render_template('parameters.html',lists = names,files=filename)




    # Save Data as csv file
    # Data1.to_csv("For plot.csv", index=False, sep=',')
    # protein = 'h2B'
    # m = []
    # for time in Time_points1:
    #     state1 = 'AB'
    #     x1 = list(Data1[protein + '_' + state1 + '_' + time + '_SD'])
    #     while np.core.numeric.NaN in x1:
    #         x1.remove(np.core.numeric.NaN)
    #     m += x1
    # print(np.array(m).astype(float).mean())
    # t1 = t.ppf(1-0.01, 3)
    # print(t1)
    # T = uptakeplot(Data1, Proteins, Time_points1, States1, 5, 4, file_name='H3H4_4deg.pdf',
    #                color=[(192 / 255, 0, 0), 'k', (192 / 255, 0, 0), (22 / 255, 54 / 255, 92 / 255),
    #                       'sienna'])
    # for time in Time_points1:
    #     for state in States1:
    #         Data1[state + '_' + time] = Data1[state + '_' + time].astype('float')
    #     Data1['Sub1' + '_' + time] = Data1['Mtr4' + '_' + time] - Data1['Mtr4+RNA' + '_' + time]
    #     Data1['Sub3' + '_' + time] = Data1['TRAMP Complex' + '_' + time] - Data1['TRAMP Complex+RNA' + '_' + time]
    # c = ['k', (192 / 255, 0, 0), (1, 165 / 255, 0),(22 / 255, 54 / 255, 92 / 255), 'sienna']
    # K = HDX_Plots_for_web.heatmap(Data1, 'H32_XENLA', 'H3H4dm', 'RV-H3H4dm', Time_Points, rotation='H', max=5, step=10, color='rb', min=-5, step2=10,
    #             file_name='FL_ASF1.eps')
    #         # a = v(Data1, Time_points1, [P], S1, S2, colors=c, filename='{} {}-{}_v.eps'.format(P, S1, S2))
    # c = ['k', (192 / 255, 0, 0), (1, 165 / 255, 0),(22 / 255, 54 / 255, 92 / 255),'sienna']
    # for k, time in enumerate(Time_points1):
    # a = v(Data1, Time_points1, ['Nap1'], 'Nap1 Alone', 'Nap1 Bound', colors=c, filename='Taz2_v_new_{}s.eps')
        # for time in Time_points1:
    #     H = wood(df, 'Apo', 'ADP', time)
    # return render_template('parameters.html',lists = [Proteins,States,Time_Points],files=filename)

#     return send_file(file_object, mimetype='application/postscript', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.eps')
    
