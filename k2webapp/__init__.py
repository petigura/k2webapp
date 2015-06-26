from flask import Flask
app = Flask(__name__)

import os
import k2webapp.views
from werkzeug.contrib.profiler import ProfilerMiddleware

app.secret_key = os.urandom(24)
app.config['host'] = os.environ['K2WEBAPP_HOST']
app.config['port'] = int(os.environ['K2WEBAPP_PORT'])

@app.route('/vetting/<k2_camp>/<run>/<starname_url>',methods=['GET','POST'])
def display_vetting(k2_camp,run,starname_url):
    print k2webapp.views.display_vetting(k2_camp,run,starname_url)
    return k2webapp.views.display_vetting(k2_camp,run,starname_url)
    

@app.route('/vetting/list/<k2_camp>/<run>/',methods=['GET','POST'])
def display_vetting_list(k2_camp,run):
    return k2webapp.views.display_vetting_list(k2_camp,run)

