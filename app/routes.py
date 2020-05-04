from app import app
from flask import render_template, send_file,request,Flask
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for,g
from flask import  make_response, session
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
import glob
import json
import uuid
import shutil
import datetime
import csv
from app import email
from app import clean
import time
from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import pickle



# add schedule task to remove temp files every 2 weeks and send ip list every 2 weeks
alluser_folders = os.path.join(Path(app.root_path),'static/user_folders')
ipfilename = "iplist.csv"
ip_folder = os.path.join(Path(app.root_path),'static/ip','iplist.csv')
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(email.send_ip,trigger="interval", hours=1, args =[app,ipfilename,ip_folder])
scheduler.add_job(clean.remove_userfolder,trigger="interval", weeks=2, args =[alluser_folders])
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())



app.config['ALLOWED_EXTENSIONS'] = {'csv','txt'}



################################################################################################################################################
@app.route('/',methods=['GET','POST'])
def ui():
    # track user ip and append to iplist.csv
    visitor_ip = request.remote_addr.encode()
    ip_folder = os.path.join(Path(app.root_path),'static/ip','iplist.csv')
    visit_time = str(datetime.now()).encode()
    with open(ip_folder,'ab') as file:
        file.write(visitor_ip + "  ".encode() + visit_time)
        file.write('\n'.encode())

    try:
        if session['USERID'] is not None:
            print('at / ')
            print("session detected.")
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
            print("Folder path and name are set..")
            shutil.rmtree(app.config['USER_FOLDER'])
            print("Old folder deleted...")
            os.mkdir(app.config['USER_FOLDER'])
            print("New folder created....")


    except Exception:
        print("No session exist, create a new session")
        session['USERID'] = str(uuid.uuid4())
        app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
        if not os.path.exists(app.config['USER_FOLDER']):
            os.mkdir(app.config['USER_FOLDER'])


    return render_template('ui.html',lists=[['protein'],['state'],['time point']])

########################################################################################################################################
@app.route('/upload_multi_files', methods=['GET','POST'])
def upload_multi_files():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])

    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        count = 5
        filenames = []
        for file in files:
            if count == 0:
                break
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                count -= 1
                file.save(os.path.join(app.config['USER_FOLDER'],filename))
                filenames.append(filename)
        session['FILENAME'] = filenames

        ipaddress = "IP: " + request.remote_addr
        for item in filenames:
            flash(item + '  successfully uploaded from: ' + ipaddress)

        names = reader.filesread(filenames)
        print(names)
        # Check the file formart if thr return from reader is 0, wrong formart
        if names == 0:
            return render_template('ui.html',lists = names,files=filenames)

        with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'wb') as f:
            pickle.dump(names, f)
        session["USERFILESTATUS"] = "multiple"

        return render_template('ui.html',lists = names,files=filenames,filestatus = session["USERFILESTATUS"])

@app.route('/upload_single_file', methods=['GET','POST'])
def upload_single_file():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session['FILENAME'] = filename
            file.save(os.path.join(app.config['USER_FOLDER'], filename))
            ipaddress = "IP: " + request.remote_addr
            flash(filename + ' successfully uploaded from: ' + ipaddress,'uploadnotice')
        else:
            flash('Allowed file types are csv')
            return redirect(request.url)

        names = reader.fileread(filename)

        if names == 0:
            flash('Wrong file format')
            return render_template('ui.html',lists=[['protein'],['state'],['time point']])

        with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'wb') as f:
            pickle.dump(names, f)
        return render_template('ui.html', lists=names, files=filename)




########################################################################################################################################
@app.route('/click_show_h',methods=['GET', 'POST'])
def click_show_h():
    if request.method == 'POST':
        try:
            protein = request.form.get("protein")
            state1 = request.form.get("state1")
            state2 = request.form.get("state2")
            time_point = request.form.get("time_point")
            max = float(request.form.get("max"))
            max_step= int(request.form.get("max_step"))
            negative = request.form.get("negative")
            color1 = request.form.get("color1")
            color2 = request.form.get("color2")
            significance = float(request.form.get("significance"))
            sig_filter = request.form.get("sig_filter")

            if negative:
                min = float(request.form.get("min"))
                min_step = int(request.form.get("min_step"))
                color = color2
                session["COLOR"] = 2
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step, min, min_step,
                    time_point, negative, color, significance, sig_filter]
            else:
                color = color1
                session["COLOR"] = 1
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step,0.0,0,
                    time_point, negative, color, significance, sig_filter]

            session["USERPLOTSTATUS"] = "heatmap"

        except:
            flash("WARNING: Missing parameter or invalid input!!!",'error')
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])

            with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
                names = pickle.load(f)
            Data1 = names[-1]
            Time_Points = names[-2]
            filename = session['FILENAME']
            session["USERPLOTSTATUS"] = "heatmap"
            return render_template('ui.html',lists = names,files=filename)

        print(session['PASSEDPARAMETERS'])

    return redirect('/plot')




@app.route('/click_show_v',methods=['GET', 'POST'])
def click_show_v():
    if request.method == 'POST':
        #try:
        with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
                names = pickle.load(f)
  
        protein = request.form.get("protein")
        state1 = request.form.get("state1")
        state2 = request.form.get("state2")
        time_point = request.form.get("time_point")
        if time_point == "ALL":
            time_point = names[-2]
        size = int(request.form.get("size"))
        X_scale_l = float(request.form.get("X_scale_l"))
        X_scale_r = float(request.form.get("X_scale_r"))
        Y_scale = int(request.form.get("Y_scale"))
        interval = float(request.form.get("interval"))
        showlist = request.form.get("show_list")
        plotxsize = float(request.form.get("plot_X_size"))
        color = request.form.get("color")
        if color == "pattern1":
            color = [(75/255, 140/255, 97/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255)]
        elif color == "pattern2":
            color = [(75/255, 140/255, 97/255),(12/255, 110/255, 22/255),(200/255, 200/255, 100/255),(150/255, 160/255, 80/255),(50/255, 50/255, 50/255)]

        significance = float(request.form.get("significance"))
        min_dif = float(request.form.get("min_dif"))


        session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), time_point, size,
        X_scale_l,X_scale_r, Y_scale, interval, color, significance, min_dif,showlist,plotxsize]
        print(session["PASSEDPARAMETERS"])
        session["USERPLOTSTATUS"] = "volcanoplot"


        #except:
        # flash("Missing or invalid parameter input","error")
        # app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])

        # with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
        #     names = pickle.load(f)
        # Data1 = names[-1]
        # Time_Points = names[-2]
        # filename = session['FILENAME']
        # session["USERPLOTSTATUS"] = "volcanoplot"
        # return render_template('ui.html',lists = names,files=filename)

    return redirect('/plot')




@app.route('/plot',methods=['GET','POST'])
def plot():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
    with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    Data1 = names[-1]
    Time_Points = names[-2]
    Data1.to_csv(os.path.join(app.config['USER_FOLDER'],'For_plot.csv'), index=False, sep=',')

    if session["USERPLOTSTATUS"] == "heatmap":


    #try:
        K = HDX_Plots_for_web.heatmap(app.config['USER_FOLDER'],Data1, session['PASSEDPARAMETERS'][0],
        session['PASSEDPARAMETERS'][1], session['PASSEDPARAMETERS'][2], Time_Points,
        f = session['PASSEDPARAMETERS'][-1], pp = session['PASSEDPARAMETERS'][-2],
        rotation='H', max = session['PASSEDPARAMETERS'][3],step = session['PASSEDPARAMETERS'][4],
        color=session['PASSEDPARAMETERS'][9], min = session['PASSEDPARAMETERS'][5],
        step2 = session['PASSEDPARAMETERS'][6], file_name = 'Plot')
        #except:
        #    print("Function not impelemented properly")



        return redirect('/replot')

    else:
        #session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), time_point,
        # size, X_scale_l,X_scale_r, Y_scale, interval, color, significance, min_dif]
        #colors = [(75/255, 140/255, 97/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255),(12/255, 110/255, 22/255)]

        a = HDX_Plots_for_web.v(app.config['USER_FOLDER'], Data1, Time_Points, session['PASSEDPARAMETERS'][0], session['PASSEDPARAMETERS'][1],
         session['PASSEDPARAMETERS'][2], session['PASSEDPARAMETERS'][4], session['PASSEDPARAMETERS'][9], file_name = 'Plot', md = session['PASSEDPARAMETERS'][11],
         ma = session['PASSEDPARAMETERS'][10], msi = session['PASSEDPARAMETERS'][8], xmin = session['PASSEDPARAMETERS'][5],
         xmax = session['PASSEDPARAMETERS'][6], ymin = session['PASSEDPARAMETERS'][7],plotlist = session['PASSEDPARAMETERS'][12],
         plotxsize = session['PASSEDPARAMETERS'][13])

        return redirect('/replot')


########################################################################################################################################################


@app.route('/replot',methods=['GET','POST'])
def replot():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
    with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    return render_template('ui.html',lists = names,files=session['FILENAME'],plot_status = session["USERPLOTSTATUS"], paras =session['PASSEDPARAMETERS'] )

##########################################################################################################################################################

@app.route('/plotshow',methods=['GET','POST'])
def plotshow():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
    file_png = 'Plot.png'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'],file_png)):
        return send_file(os.path.join(app.config['USER_FOLDER'],file_png), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='Sample_Icon.png')


@app.route('/downloadcsv',methods=['GET','POST'])
def downloadcsv():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
    file_csv = 'For_plot.csv'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'],file_csv)):
        return send_file(os.path.join(app.config['USER_FOLDER'],file_csv), mimetype='text/csv', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.csv')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='Sample_Icon.png')


@app.route('/downloadeps',methods=['GET','POST'])
def downloadeps():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static/user_folders',session['USERID'])
    file_eps = 'Plot.eps'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'],file_eps)):
        return send_file(os.path.join(app.config['USER_FOLDER'],file_eps), mimetype='image/eps', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.eps')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='Sample_Icon.png')



###############################################################################################################################################################################

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






def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


###############################################################################################################################################################


# @app.route('/index')

# def index():
#     user = 'Xiaohe'
#     posts = [
#         {
#             'author': {'username': 'John'},
#             'body': 'Beautiful day in Portland!'
#         },
#         {
#             'author': {'username': 'Susan'},
#             'body': 'The Avengers movie was so cool!'
#         }
#     ]
#     return render_template('index.html', title='Home', user=user, posts=posts)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect(url_for('index'))
#     return render_template('login.html', title='Sign In', form=form)




# @app.route('/error')
# def error():
#     return render_template('error.html')
