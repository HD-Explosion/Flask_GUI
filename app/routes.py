from app import app
from flask import render_template, send_file,request,Flask
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
from pathlib import Path
from flask import jsonify

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def ui():
    if os.path.exists(os.path.join(Path(app.root_path).parent,'FL_ASF1.png')):
        os.remove(os.path.join(Path(app.root_path).parent,'FL_ASF1.png'))
        

    return render_template('ui.html',lists=[['protein'],['state'],['time point']])
 




@app.route('/click_show_h',methods=['GET', 'POST'])
def click_show_h():
    if request.method == 'POST':
        protein = request.form.get("protein")
        state1 = request.form.get("state1")
        state2 = request.form.get("state2")
        time_point = request.form.get("time_point")
        size = request.form.get("size")
        X_scale = request.form.get("X_scale")
        Y_scale_l = request.form.get("Y_scale_l")
        Y_scale_r = request.form.get("Y_scale_r")
        interval = request.form.get("interval")
        color = request.form.get("color")
        significance = request.form.get("significance")
        min_dif = request.form.get("min_dif")

        #name_li = request.form.getlist("name")

        global passedParameters
        passedParameters = [str(protein), str(state1), str(state2), size, X_scale, Y_scale_l, Y_scale_r,
                            time_point, interval, color, significance, min_dif]

        #print(protein, state1,size,X_scale,Y_scale_l,Y_scale_r)
        #print(time_point,interval,color,significance,min_dif)

    return redirect('/plot')

@app.route('/replot',methods=['get','POST'])
def replot():
    return render_template('ui.html',lists = names,files=filename)

@app.route('/click_show_v',methods=['GET', 'POST'])
def click_show_v():
    if request.method == 'POST':
        protein = request.form.get("protein")
        state1 = request.form.get("state1")
        state2 = request.form.get("state2")
        time_point = request.form.get("time_point")
        size = request.form.get("size")
        X_scale = request.form.get("X_scale")
        Y_scale_l = request.form.get("Y_scale_l")
        Y_scale_r = request.form.get("Y_scale_r")
        interval = request.form.get("interval")
        color = request.form.get("color")
        significance = request.form.get("significance")
        min_dif = request.form.get("min_dif")

        #name_li = request.form.getlist("name")

        global passedParameters
        passedParameters = [str(protein), str(state1), str(state2), size, X_scale, Y_scale_l, Y_scale_r,
                            time_point, interval, color, significance, min_dif]

        #print(protein, state1,size,X_scale,Y_scale_l,Y_scale_r)
        #print(time_point,interval,color,significance,min_dif)

    return redirect('/plot')


if __name__ == '__main__':
    app.run(debug=True)

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
                count -= 1
                file.save(os.path.join(UPLOAD_FOLDER,filename))
        flash(filename + 'successfully uploaded')
        global names
        names = reader.fileread(filename)
        # print(names)
        global Data1
        Data1 = names[-1]
        global Time_Points
        Time_Points = names[-2]
        # print(Data1)

        return render_template('ui.html',lists = names,files=filename,ipaddr = ("ip: " + request.remote_addr))        #  /parameters for test

@app.route('/upload_file_merge', methods=['POST'])
def upload_file_merge():
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
        flash(filename + ' successfully uploaded')
        global names
        names = reader.fileread(filename)
        # print(names)
        global Data1
        Data1 = names[-1]
        global Time_Points
        Time_Points = names[-2]
        # print(Data1)

        return render_template('ui.html',lists = names,files=filename)        #  /parameters for test


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
@app.route('/plotshow')
def plotshow():
    file_png = 'FL_ASF1.png'
    if os.path.exists(os.path.join(Path(app.root_path).parent,file_png)):
        return send_file(os.path.join(Path(app.root_path).parent,file_png), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')



@app.route('/downloadcsv')
def downloadcsv():
    file_csv = 'For plot.csv'
    return send_file(os.path.join(Path(app.root_path).parent,file_csv), mimetype='text/csv', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.csv')


@app.route('/downloadeps')
def downloadeps():
    file_eps = 'FL_ASF1.eps'
    return send_file(os.path.join(Path(app.root_path).parent,file_eps), mimetype='image/eps', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.eps')



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



ALLOWED_EXTENSIONS = {'csv','txt','xls','pdf','docx'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




'''
@app.route('/parameters')                 #  /parameters for test
def parameter():
    names = reader.fileread(filename)
    return render_template('parameters.html',lists = names,files=filename)

def get_param():
    value = request.form['name']

'''


@app.route('/plot')
def plot():
    Data1.to_csv("For plot.csv", index=False, sep=',')
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

    K = HDX_Plots_for_web.heatmap(Data1,passedParameters[0], passedParameters[1], 
    passedParameters[2],Time_Points, rotation='H', max=5, step=10, color='rb', min=-5, step2=10,file_name='FL_ASF1')

    return redirect('/replot')
