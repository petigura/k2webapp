from flask import Flask
app = Flask(__name__)

import os
import k2webapp.views

app.secret_key = os.urandom(24)
app.config['host'] = os.environ['K2WEBAPP_HOST']
app.config['port'] = int(os.environ['K2WEBAPP_PORT'])
from datetime import datetime
print "webapp started %s" % datetime.now()

@app.route('/photometry/<k2_camp>/<run>/<starname>')
def display_photometry(k2_camp,run,starname):
    return k2webapp.views.display_photometry( k2_camp,run,starname)

@app.route('/vetting/<k2_camp>/<run>/<starname>',methods=['GET','POST'])
def display_vetting(k2_camp,run,starname):
    return k2webapp.views.display_vetting(k2_camp,run,starname)

@app.route('/vetting/list/<k2_camp>/<run>/',methods=['GET','POST'])
def display_vetting_list(k2_camp,run):
    return k2webapp.views.display_vetting_list(k2_camp,run)

