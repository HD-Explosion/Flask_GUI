from app import app
from flask import render_template, send_file, request, Flask
from flask import render_template, flash, redirect, url_for, g
from flask import make_response, session
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
alluser_folders = os.path.join(Path(app.root_path), 'static/user_folders')
ipfilename = "iplist.csv"
ip_folder = os.path.join(Path(app.root_path), 'static/ip', 'iplist.csv')
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(email.send_ip, trigger="interval", weeks=2, args=[app, ipfilename, ip_folder])
scheduler.add_job(clean.remove_userfolder, trigger="interval", weeks=2, args=[alluser_folders])
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


################################################################################################################################################
@app.route('/sayhello', methods=['GET'])
def say_hello():
    return "<button>click me</button>"



@app.route('/', methods=['GET', 'POST'])

################################################################################################################################################
@app.route('/',methods=['GET','POST'])

def ui():
    # track user ip and append to iplist.csv
    visitor_ip = request.remote_addr.encode()
    ip_folder = os.path.join(Path(app.root_path), 'static/ip', 'iplist.csv')
    visit_time = str(datetime.now()).encode()
    with open(ip_folder, 'ab') as file:
        file.write(visitor_ip + "  ".encode() + visit_time)
        file.write('\n'.encode())

    try:
        if session['USERID'] is not None:
            print('at / ')
            print("session detected.")
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
            print("Folder path and name are set..")
            shutil.rmtree(app.config['USER_FOLDER'])
            print("Old folder deleted...")
            os.mkdir(app.config['USER_FOLDER'])
            print("New folder created....")


    except Exception:
        print("No session exist, create a new session")
        session['USERID'] = str(uuid.uuid4())
        app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
        if not os.path.exists(app.config['USER_FOLDER']):
            os.mkdir(app.config['USER_FOLDER'])

    return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])
    
def af_request(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp

########################################################################################################################################
@app.route('/upload_multi_files', methods=['GET', 'POST'])
def upload_multi_files():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])

    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        cnt = len(files)
        count = 5
        filenames = []
        for file in files:
            if count == 0:
                break
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                count -= 1
                file.save(os.path.join(app.config['USER_FOLDER'], filename))
                filenames.append(filename)
            else:
                flash('Allowed file types are csv')
                return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])

        try:
            names = reader.filesread(filenames)
            if names == 0:
                flash("Wrong file format, try different csv files")
                return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])
        except:
            flash("Invalid csv files uploaded, try different csv files")
            return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])

        session['FILENAME'] = filenames

        with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'wb') as f:
            pickle.dump(names, f)
        session["USERFILESTATUS"] = "multiple"
        return render_template('ui.html', lists=names, files=filenames, filestatus=session["USERFILESTATUS"], cnt=cnt)


@app.route('/upload_single_file', methods=['GET', 'POST'])
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
            try:
                names = reader.fileread(filename)
                if names == 0:
                    flash("Wrong file format, try different csv files")
                    return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])
            except:
                flash("Invalid csv file uploaded, try a different csv file")
                return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])

            flash(filename + ' successfully uploaded', 'uploadnotice')

        else:
            flash('Allowed file types are csv')
            return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])
        with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'wb') as f:
            pickle.dump(names, f)
        return render_template('ui.html', lists=names, files=filename)


########################################################################################################################################
@app.route('/click_show_h', methods=['GET', 'POST'])
def click_show_h():
    if request.method == 'POST':
        try:
            protein = request.form.get("protein")
            state1 = request.form.get("state1")
            state2 = request.form.get("state2")
            time_point = "overwrite in function part"
            max = float(request.form.get("max"))
            max_step = int(request.form.get("max_step"))
            negative = request.form.get("negative")
            color1 = request.form.get("color1")
            color2 = request.form.get("color2")
            significance = float(request.form.get("significance"))
            sig_filter = request.form.get("sig_filter")
            direction = request.form.get("direction")
            nsize = int(request.form.get('nsize'))
            if direction == "vertical":
                rotation = "V"
            else:
                rotation = "H"

            if negative:
                min = float(request.form.get("min"))
                min_step = int(request.form.get("min_step"))
                color = color2
                session["COLOR"] = 2
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step, min, min_step,
                                               time_point, negative, color, significance, sig_filter, rotation, nsize]
            else:
                color = color1
                session["COLOR"] = 1
                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), max, max_step, 0.0, 0,
                                               time_point, negative, color, significance, sig_filter, rotation, nsize]

            session["COLORLIST"] = [['r', 'g', 'b', 'o', 'y'], ['rb', 'br', 'ob', 'bg']]
            session["USERPLOTSTATUS"] = "heatmap"

        except:
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
            if os.path.exists(os.path.join(app.config['USER_FOLDER'], 'names.pickle')):
                flash("WARNING: Missing parameter or invalid input!!!", 'error')
                with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
                    names = pickle.load(f)
                Data1 = names[-1]
                Time_Points = names[-2]
                filename = session['FILENAME']
                session["USERPLOTSTATUS"] = "heatmap"
                return render_template('ui.html', lists=names, files=filename)
            else:
                flash("WARNING: Please upload csv files", 'error')
                return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])

        print(session['PASSEDPARAMETERS'])

    return redirect('/plot')


@app.route('/click_show_v', methods=['GET', 'POST'])
def click_show_v():
    if 'pbd_code' in request.form.keys():
        return redirect('/plot')

    if request.method == 'POST':
        try:
            with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
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
            textsize = float(request.form.get("text_size"))
            showlist = request.form.get("show_list")
            plotxsize = float(request.form.get("plot_X_size"))
            plotysize = float(request.form.get("plot_Y_size"))
            significance = float(request.form.get("significance"))
            min_dif = float(request.form.get("min_dif"))
            color = request.form.get("color")
            nsize = int(request.form.get('nsize'))

            print(color)
            if color:

                if color == "pattern1":
                    color = ['#000000', '#B40000', '#000096', '#F09600', '#009600', '#009696']
                elif color == "pattern2":
                    color = ['#170E34', '#162850', '#264A6D', '#005CA5', '#00909D', '#DAE0E6']
                elif color == "pattern3":
                    color = ['#511845', '#8F1941', '#C7203C', '#F0593A', '#F7AFA6', '#FFD769']
                elif color == "pattern4":
                    color = ['#BE3726', '#F05D29', '#F1892E', '#F1B23C', '#F1D540', '#BBD873']
                elif color == "pattern5":
                    color = ['#C54129', '#DD762E', '#718161', '#D7C492', '#4D3E3E', '#170E34']
                elif color == "pattern6":
                    color = ['#E34798', '#D180B4', '#BC94C4', '#DFA2C8', '#DFA2C8', '#FCE2DA']
                elif color == "pattern7":
                    color = ['#FFE65D', '#FCB628', '#889756', '#527435', '#434E53', '#5B8B84']

                session['PASSEDPARAMETERS'] = [str(protein), str(state1), str(state2), time_point, size,
                                               X_scale_l, X_scale_r, Y_scale, interval, color, significance, min_dif,
                                               plotxsize, plotysize, showlist, textsize, nsize]
                print(session["PASSEDPARAMETERS"])
                session["USERPLOTSTATUS"] = "volcanoplot"

            else:
                flash("Missing Color pattern", "error")
                app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])

                with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
                    names = pickle.load(f)
                Data1 = names[-1]
                Time_Points = names[-2]
                filename = session['FILENAME']
                session["USERPLOTSTATUS"] = "volcanoplot"
                return render_template('ui.html', lists=names, files=filename)



        except:
            app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
            if os.path.exists(os.path.join(app.config['USER_FOLDER'], 'names.pickle')):
                flash("Missing or invalid parameter input", "error")
                with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
                    names = pickle.load(f)
                Data1 = names[-1]
                Time_Points = names[-2]
                filename = session['FILENAME']
                session["USERPLOTSTATUS"] = "volcanoplot"
                return render_template('ui.html', lists=names, files=filename)
            else:
                flash("WARNING: Please upload csv files", 'error')
                return render_template('ui.html', lists=[['protein'], ['state'], ['time point']])

        return redirect('/plot')


# @app.route('/click_show_cm', methods=['GET', 'POST'])
# def click_show_cm():
#     form = request.form
#     with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
#         names = pickle.load(f)
#     Data1 = names[-1]
#     paths = HDX_Plots_for_web.cm(
#         os.path.join(alluser_folders, session['USERID']),Data1, form.get("pbd_code"), form.get('chain_id'),form.get('protein'),
#         form.get('seq'), form.get('aas_per_row'), 155,float(form.get('bar_height')), .1,form.get('state1'),
#         form.get('state2'), 1000, ['10', '100'], form.get('min_diff'), form.get('max_diff'),
#     )
#     return jsonify(paths)

@app.route('/click_show_cm', methods=['POST'])
def click_show_cm():

    # all data from user, eg:
    # ******************************
    # aas_per_row: "155"
    # bar_height: "4"
    # chain_id: "RTT109"
    # color: "pattern1"
    # colors: "pattern7"
    # max_diff: "0.2"
    # min_diff: "0.2"
    # pbd_code: "2xgj.pdb"
    # protein: "Protein1"
    # seq: "DSTDLFDVFEETPVELPTDSNGEKNADTNVGDTPDHTQDKKHGLEEEKEEHEENNSENKKIKSNKSKTEDKNKKVVVPVLADSFEQEASREVDASKGLTNSETLQVEQDGKVRLSHQVRHQVALPPNYDYTPIAEHKRVNEARTYPFTLDPFQDTAISCIDRGESVLVSAHTSAGKTVVAEYAIAQSLKNKQRVIYTSPIKALSNQKYRELLAEFGDVGLMTGDITINPDAGCLVMTTEILRSMLYRGSEVMREVAWVIFDEVHYMRDKERGVVWEETIILLPDKVRYVFLSATIPNAMEFAEWICKIHSQPCHIVYTNFRPTPLQHYLFPAHGDGIYLVVDEKSTFREENFQKAMASISNQIGDDPNSTDSRGKKGQTYKGGSAKGDAKGDIYKIVKMIWKKKYNPVIVFSFSKRDCEELALKMSKLDFNSDDEKEALTKIFNNAIALLPETDRELPQIKHILPLLRRGIGIHHSGLLPILKEVIEILFQEGFLKVLFATETFSIGLNMPAKTVVFTSVRKWDGQQFRWVSGGEYIQMSGRAGRRGLDDRGIVIMMIDEKMEPQVAKGMVKGQADRLDSAFHLGYNMILNLMRVEGISPEFMLEHSFFQFQNVISVPVMEKKLAELKKDFDGIEVEDEENVKEYHEIEQAIKGYREDVRQVVTHPANALSFLQPGRLVEISVNGKDNYGWGAVVDFAKRINKRNPSAVYTDHESYIVNVVVNTMYIDSPVNLLKPFNPTLPEGIRPAEEGEKSICAVIPITLDSIKSIGNLRLYMPKDIRASGQKETVGKSLREVNRRFPDGIPVLDPVKNMKIEDEDFLKLMKKIDVLNTKLSSNPLTNSMRLEELYGKYSRKHDLHEDMKQLKRKISESQAVIQLDDLRRRKRVLRRLGFCTPNDIIELKGRVACEISSGDELLLTELIFNGNFNELKPEQAAALLSCFAFQERCKEAPRLKPELAEPLKAMREIAAKIAKIMKDSKIEVVEKDYVESFRHELMEVVYEWCRGATFTQICKMTDVYEGSLIRMFKRLEELVKELVDVANTIGNSSLKEKMEAVLKLIHRDIVSAGSLYL"
    # show_ss: "on"
    # state1: "State2"
    # state2: "State2"
    # time_points: "All"
    # ******************************
    ####
    # 1. show data
    form = request.form
    print(form)
    # print(app.config['USER_FOLDER'])
    with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    Data1 = names[-1]
    # 2. plot
    
    sec = form.get('seq').replace(" ", "").replace('\n', '').replace('\r', '')
    a = HDX_Plots_for_web.cm(os.path.join(alluser_folders, session['USERID']),Data1, form.get("pbd_code"), form.get('chain_id'),form.get('protein'),
            form.get('show_ss'), sec, int(form.get('aas_per_row')),float(form.get('bar_height')), .1,form.get('state1'),
            form.get('state2'), form.get('time_points'), names[-2],  form.get('min_diff'), form.get('max_diff'))
    print("out...")
    print(a)
    ####
    # 3. update link of ['plotshow', '/downloadeps']
    ...
    print("test...")
    file_png = "-1.png"
    path = str(os.path.join(app.config['USER_FOLDER'], file_png)).replace("\\", "/")
    print(os.path.join(app.config['USER_FOLDER'], file_png))
    print(path)
    # return send_file(os.path.join(app.config['USER_FOLDER'], file_png), mimetype='image/png', as_attachment=True,
    #                  cache_timeout=0, attachment_filename='HDX_Plot.png')
    return "/static/user_folders/" + session['USERID'] + "/" + file_png
    # return jsonify({'src': path})
    # 4. :return: picture url(png), eg:
    # /static/simple.png


    # return '/static/simpleeeeeeeee.png'

###################################################################################################################################################################################

@app.route('/plot', methods=['GET', 'POST'])
def plot():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
        names = pickle.load(f)
    Data1 = names[-1]
    Time_Points = names[-2]
    Data1.to_csv(os.path.join(app.config['USER_FOLDER'], 'For_plot.csv'), index=False, sep=',')

    if session["USERPLOTSTATUS"] == "heatmap":
        try:
            K = HDX_Plots_for_web.heatmap(app.config['USER_FOLDER'], Data1, session['PASSEDPARAMETERS'][0],
                                          session['PASSEDPARAMETERS'][1], session['PASSEDPARAMETERS'][2], Time_Points,
                                          f=session['PASSEDPARAMETERS'][11], pp=session['PASSEDPARAMETERS'][10],
                                          rotation=session['PASSEDPARAMETERS'][12], max=session['PASSEDPARAMETERS'][3],
                                          step=session['PASSEDPARAMETERS'][4],
                                          color=session['PASSEDPARAMETERS'][9], min=session['PASSEDPARAMETERS'][5],
                                          step2=session['PASSEDPARAMETERS'][6], file_name='Plot',
                                          nsize=session['PASSEDPARAMETERS'][13])
            print(K)
            return redirect('/replot')
        except:
            print("Function not impelemented properly")
            return redirect('/replot')

    else:
        try:
            if session['PASSEDPARAMETERS'][3] == Time_Points:
                timep = Time_Points
            else:
                timep = [session['PASSEDPARAMETERS'][3]]
            a = HDX_Plots_for_web.v(app.config['USER_FOLDER'], Data1, timep, session['PASSEDPARAMETERS'][0],
                                    session['PASSEDPARAMETERS'][1],
                                    session['PASSEDPARAMETERS'][2], session['PASSEDPARAMETERS'][4],
                                    session['PASSEDPARAMETERS'][9], file_name='Plot',
                                    md=session['PASSEDPARAMETERS'][11],
                                    ma=session['PASSEDPARAMETERS'][10], msi=session['PASSEDPARAMETERS'][8],
                                    xmin=session['PASSEDPARAMETERS'][5],
                                    xmax=session['PASSEDPARAMETERS'][6], ymin=session['PASSEDPARAMETERS'][7],
                                    sizeX=session['PASSEDPARAMETERS'][12], sizeY=session['PASSEDPARAMETERS'][13],
                                    lif=session['PASSEDPARAMETERS'][14], tsize=session['PASSEDPARAMETERS'][15],
                                    nsize=session['PASSEDPARAMETERS'][16])
            return redirect('/replot')
        except:
            print("Function not impelemented properly")
            return redirect('/replot')


####################################################################################################################################################################################


@app.route('/replot', methods=['GET', 'POST'])
def replot():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    with open(os.path.join(app.config['USER_FOLDER'], 'names.pickle'), 'rb') as f:
        names = pickle.load(f)
        try:
            return render_template('ui.html', lists=names, files=session['FILENAME'],
                                   plot_status=session["USERPLOTSTATUS"], paras=session['PASSEDPARAMETERS'],
                                   cl_list=session["COLORLIST"])
        except:
            return render_template('ui.html', lists=names, files=session['FILENAME'],
                                   plot_status=session["USERPLOTSTATUS"], paras=session['PASSEDPARAMETERS'],
                                   cl_list=["epmty"])


##########################################################################################################################################################

@app.route('/plotshow', methods=['GET', 'POST'])
def plotshow():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    file_png = 'Plot.png'
    file_png2 = '-1.png'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'], file_png)):
        return send_file(os.path.join(app.config['USER_FOLDER'], file_png), mimetype='image/png', as_attachment=True,
                         cache_timeout=0, attachment_filename='HDX_Plot.png')
    elif os.path.exists(os.path.join(app.config['USER_FOLDER'], file_png2)):
        return send_file(os.path.join(app.config['USER_FOLDER'], file_png2), mimetype='image/png', as_attachment=True,
                         cache_timeout=0, attachment_filename='HDX_Plot2.png')
    else:
        return send_file(os.path.join('./static/image', 'UTD.png'), mimetype='image/png', as_attachment=True,
                         cache_timeout=0, attachment_filename='Sample_Icon.png')


@app.route('/downloadcsv', methods=['GET', 'POST'])
def downloadcsv():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    file_csv = 'For_plot.csv'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'], file_csv)):
        return send_file(os.path.join(app.config['USER_FOLDER'], file_csv), mimetype='text/csv', as_attachment=True,
                         cache_timeout=0, attachment_filename='HDX_Plot.csv')
    else:
        return send_file(os.path.join('./static/image', 'UTD.png'), mimetype='image/png', as_attachment=True,
                         cache_timeout=0, attachment_filename='Sample_Icon.png')


@app.route('/downloadeps', methods=['GET', 'POST'])
def downloadeps():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    file_eps = 'Plot.eps'
    file_eps1 = '-1.eps'

    if os.path.exists(os.path.join(app.config['USER_FOLDER'], file_eps)):
        return send_file(os.path.join(app.config['USER_FOLDER'], file_eps), mimetype='image/eps', as_attachment=True,
                         cache_timeout=0, attachment_filename='HDX_Plot.eps')
    elif os.path.exists(os.path.join(app.config['USER_FOLDER'], file_eps1)):
        return send_file(os.path.join(app.config['USER_FOLDER'], file_eps1), mimetype='image/eps', as_attachment=True,
                         cache_timeout=0, attachment_filename='HDX_Plot2.eps')
    else:
        return send_file(os.path.join('./static/image', 'UTD.png'), mimetype='image/png', as_attachment=True,
                         cache_timeout=0, attachment_filename='Sample_Icon.png')


@app.route('/downloaddemo', methods=['GET', 'POST'])
def downloaddemo():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static')
    file_demo = 'Demofile.csv'

    return send_file(os.path.join(app.config['USER_FOLDER'], file_demo), mimetype='text/csv', as_attachment=True,
                     cache_timeout=0, attachment_filename='Demofile.csv')


@app.route('/downloadlist', methods=['GET', 'POST'])
def downloadlist():
    app.config['USER_FOLDER'] = os.path.join(Path(app.root_path), 'static/user_folders', session['USERID'])
    file_list = 'list.csv'

    return send_file(os.path.join(app.config['USER_FOLDER'], file_list), mimetype='text/csv', as_attachment=True,
                     cache_timeout=0, attachment_filename='list.csv')


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
    app.config['ALLOWED_EXTENSIONS'] = {'csv', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

###############################################################################################################################################################
