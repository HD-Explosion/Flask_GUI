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
from app import email
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import pickle



global ipdict
ipdict = {} 
scheduler = BackgroundScheduler()

ipfilename = "iplist.csv"
#ipfilepath = os.path.join(Path(app.root_path),'static/ip',ipfilename)
#ipfiledata = pd.read_csv(ipfilepath, dtype=str, index_col=0)
ipfiledata = "IP TEST DATA 1:0:0:27"
#ipfiledata = csv.read(os.path.join(Path(app.root_path),'static/ip',ipdict))
scheduler.start()
scheduler.add_job(email.send_ip,trigger="interval", seconds=45, args =[app,ipfilename,ipfiledata])

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app.config['ALLOWED_EXTENSIONS'] = {'csv','txt'}



#...
# @app.route('/visits-counter')
# def visits():
#     if 'visits' in session:
#         session['visits'] = session.get('visits') + 1  # reading and updating session data
#     else:
#         session['visits'] = 1 # setting session data



#     return "Total visits: {} {}".format(session.get('visits'),session['USERID'])

################################################################################################################################################
@app.route('/',methods=['GET','POST'])
def ui():
    try:
        if session['USERID'] is not None:
            print('at / ')
            print("session detected.")
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
            print("Folder path and name are set..")
            shutil.rmtree(app.config['USER_FOLDER'])
            print("Old folder deleted...")
            os.mkdir(app.config['USER_FOLDER'])
            print("new folder created....")
        
    except Exception:
        print("No session exist, create a new session")
        session['USERID'] = str(uuid.uuid4())
        app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
        if not os.path.exists(app.config['USER_FOLDER']):
            os.mkdir(app.config['USER_FOLDER'])



                
    # resp = make_response(render_template('ui.html',lists=[['protein'],['state'],['time point']]))
    # resp.set_cookie('userID',userid)

    #return resp
    return render_template('ui.html',lists=[['protein'],['state'],['time point']])

########################################################################################################################################
@app.route('/upload_multi_files', methods=['GET','POST'])
def upload_multi_files():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])

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
                #global filename
                filename = secure_filename(file.filename)
                session['FILENAME'] = filename
                #print(filename)
                count -= 1
                file.save(os.path.join(app.config['USER_FOLDER'],filename))
        ipaddress = "IP: " + request.remote_addr
        flash(filename + ' successfully uploaded from: ' + ipaddress)

        if (request.remote_addr in ipdict): 
            ipdict[request.remote_addr] += 1
        else: 
            ipdict[request.remote_addr] = 1
  
        for key, value in ipdict.items(): 
            print ("% s : % d"%(key, value))  



        names = reader.fileread(filename)
        with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'wb') as f:
            pickle.dump(names, f)


        return render_template('ui.html',lists = names,files=filename)   

@app.route('/upload_single_file', methods=['GET','POST'])
def upload_single_file():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static', session['USERID'])

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
            flash(filename + ' successfully uploaded from: ' + ipaddress)
        else:
            flash('Allowed file types are csv')
            return redirect(request.url)

        if (request.remote_addr in ipdict):
            ipdict[request.remote_addr] += 1
        else:
            ipdict[request.remote_addr] = 1

        for key, value in ipdict.items():
            print("% s : % d" % (key, value))

        
        names = reader.fileread(filename)
        with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'wb') as f:
            pickle.dump(names, f)

        return render_template('ui.html', lists=names, files=filename)

    #def upload_file():                                                # single-file allowed version
    # if request.method == 'POST':
    #     # check if the post request has the file part
    #     if 'file' not in request.files:
    #         flash('No file part')
    #         return redirect(request.url)
    #     file = request.files['file']
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         global filename
    #         filename = secure_filename(file.filename)
    #         print(filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #
    #     flash(filename + ' successfully uploaded')
    #     global names
    #     names = reader.fileread(filename)
    #     # print(names)
    #     global Data1
    #     Data1 = names[-1]
    #     global Time_Points
    #     Time_Points = names[-2]
    #     # print(Data1)
    #
    #     return render_template('ui.html', lists = names, files=filename, ipaddr = ("ip: " + request.remote_addr))        #  /parameters for test


# @app.route('/upload_file_merge', methods=['POST'])
# def upload_file_merge():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'files[]' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         files = request.files.getlist('files[]')
#         count = 2
#         for file in files:
#             if count == 0:
#                 break
#             if file and allowed_file(file.filename):
#                 #global filename
#                 filename = secure_filename(file.filename)
#                 session['FILENAME'] = filename
#                 #print(filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 count -= 1
#         flash(filename + ' successfully uploaded')
#         global names
#         names = reader.fileread(filename)
#         # print(names)
#         global Data1
#         Data1 = names[-1]
#         global Time_Points
#         Time_Points = names[-2]
#         # print(Data1)

#         return render_template('ui.html',lists = names,files=filename,ipaddr = ("ip: " + request.remote_addr))        #  /parameters for test



# @app.route('/start_over')
# def start_over():
#     app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
#     if os.path.exists(os.path.join(app.config['USER_FOLDER'],'FL_ASF1.png')):
#         for f in glob.glob(os.path.join(app.config['USER_FOLDER'],'*')):
#             os.remove(f)
        

#     return render_template('ui.html',lists=[['protein'],['state'],['time point']])


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
            max_step= float(request.form.get("max_step"))
            negative = request.form.get("negative")
            color1 = request.form.get("color1")
            color2 = request.form.get("color2")
            significance = float(request.form.get("significance"))
            sig_filter = request.form.get("sig_filter")

            if negative:
                min = float(request.form.get("min"))
                min_step = float(request.form.get("min_step"))
                color = color2
                session["COLOR"] = 2
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step, min, min_step,
                    time_point, negative, color, significance, sig_filter]
            else:
                color = color1
                session["COLOR"] = 1
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step,0.0,0,
                    time_point, negative, color, significance, sig_filter]

            
        except:
            flash("Missing or invalid parameter input")
            with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
                names = pickle.load(f)
            Data1 = names[-1]
            Time_Points = names[-2]
            filename = session['FILENAME']

            return render_template('ui.html',lists = names,files=filename)




        print(session['PASSEDPARAMETERS'])
        print(color)
        print(negative)
    return redirect('/plot')


@app.route('/click_show_v',methods=['GET', 'POST'])
def click_show_v():
    if request.method == 'POST':
        try:
            protein = request.form.get("protein")
            state1 = request.form.get("state1")
            state2 = request.form.get("state2")
            time_point = request.form.get("time_point")
            size = int(request.form.get("size"))
            X_scale = int(request.form.get("X_scale"))
            Y_scale_l = int(request.form.get("Y_scale_l"))
            Y_scale_r = int(request.form.get("Y_scale_r"))
            interval = int(request.form.get("interval"))
            color = request.form.get("color")
            significance = request.form.get("significance")
            min_dif = request.form.get("min_dif")

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

            
        except:
            flash("Missing or invalid parameter input")
            with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
                names = pickle.load(f)
            Data1 = names[-1]
            Time_Points = names[-2]
            filename = session['FILENAME']

            return render_template('ui.html',lists = names,files=filename)




        print(session['PASSEDPARAMETERS'])
        print(color)
        print(negative)
    return redirect('/plot')



#############################################################################################################################################

@app.route('/plot',methods=['GET','POST'])
def plot():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
    # read parameters from saved file
    with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    Data1 = names[-1]

    Time_Points = names[-2]

    Data1.to_csv(os.path.join(app.config['USER_FOLDER'],'For_plot.csv'), index=False, sep=',')
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

        # ' = [str(protein), str(state1), str(state2), max, max_step, min, min_step,
        #                     time_point, negative, color, significance, sig_filter]

#try:
    K = HDX_Plots_for_web.heatmap(app.config['USER_FOLDER'],Data1, session['PASSEDPARAMETERS'][0], 
    session['PASSEDPARAMETERS'][1], session['PASSEDPARAMETERS'][2], Time_Points, 
    f = session['PASSEDPARAMETERS'][-1], pp = session['PASSEDPARAMETERS'][-2],
    rotation='H', max = session['PASSEDPARAMETERS'][3],step = session['PASSEDPARAMETERS'][4], 
    color=session['PASSEDPARAMETERS'][9], min = session['PASSEDPARAMETERS'][5], 
    step2 = session['PASSEDPARAMETERS'][6], file_name='FL_ASF1')
    #except:
    #    print("Function not impelemented properly")



    # K = HDX_Plots_for_web.heatmap(Data1, '[0], '[1],
    #                               '[2], Time_Points, rotation='H', max=5, step=10, color='rb', min=-5,
    #                               step2=10, file_name='FL_ASF1')
    #         # a = v(Data1, Time_points1, [P], S1, S2, colors=c, filename='{} {}-{}_v.eps'.format(P, S1, S2))
    # c = ['k', (192 / 255, 0, 0), (1, 165 / 255, 0),(22 / 255, 54 / 255, 92 / 255),'sienna']
    # for k, time in enumerate(Time_points1):
    # a = v(Data1, Time_points1, ['Nap1'], 'Nap1 Alone', 'Nap1 Bound', colors=c, filename='Taz2_v_new_{}s.eps')
    # for time in Time_points1:
    #     H = wood(df, 'Apo', 'ADP', time)
    # return render_template('parameters.html',lists = [Proteins,States,Time_Points],files=filename)

    #     return send_file(file_object, mimetype='application/postscript', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.eps')

    return redirect('/replot')






########################################################################################################################################################


@app.route('/replot',methods=['GET','POST'])
def replot():
    with open(os.path.join(app.config['USER_FOLDER'],'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    return render_template('ui.html',lists = names,files=session['FILENAME'])

##########################################################################################################################################################

@app.route('/plotshow',methods=['GET','POST'])
def plotshow():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
    file_png = 'FL_ASF1.png'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'],file_png)):
        return send_file(os.path.join(app.config['USER_FOLDER'],file_png), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='Sample_Icon.png')


@app.route('/downloadcsv',methods=['GET','POST'])
def downloadcsv():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
    file_csv = 'For_plot.csv'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'],file_csv)):
        return send_file(os.path.join(app.config['USER_FOLDER'],file_csv), mimetype='text/csv', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.csv')
    else:
        return send_file(os.path.join('./static/image','UTD.png'), mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='Sample_Icon.png')


@app.route('/downloadeps',methods=['GET','POST'])
def downloadeps():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path),'static',session['USERID'])
    file_eps = 'FL_ASF1.eps'

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

# if __name__ == '__main__':
#     app.run(debug=True)





# @app.route('/', methods=['POST'])
# def save():
#     name = request.form['name']

#     if request.method == 'POST':
#         params = request.data.getlist('params[]')

#     return params


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

#     return send_file(file_object, mimetype='image/png', as_attachment=True,cache_timeout=0,attachment_filename='HDX_Plot.png')



