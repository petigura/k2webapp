#!/usr/bin/env python 
from cStringIO import StringIO as sio
import sqlite3
import os.path
import copy
from time import strftime

import numpy as np
from flask import Flask #  creating a flask application,
# render a HTML template with the given context variables
from flask import render_template 
# access the request object which contains the request data
from flask import request 
from flask import url_for # get the URL corresponding to a view
from flask import session # store and retrieve session variables in every view
from flask import redirect # redirect to a given URL
# access the request object which contains the request data
from flask import flash  # to display messages in the template
import pandas as pd
from werkzeug.contrib.profiler import ProfilerMiddleware

import k2_catalogs

host = os.environ['K2WEBAPP_HOST']
port = int(os.environ['K2WEBAPP_PORT'])
app = Flask(__name__)
app.secret_key = os.urandom(24)

K2_ARCHIVE = os.environ['K2_ARCHIVE']
K2_ARCHIVE_URL = "http://portal.nersc.gov/project/m1669/K2/"

def is_eKOI_string(d):
    """
    Return a string explaining the disposition status of eKOI

    Parameters
    -----------
    d : dictionary with 
        - is_eKOI
        - is_eKOI_date
    """

    if d['is_eKOI']==None:
        outstr = "No disposition" % d
    else:
        if d['is_eKOI']==1:
            outstr = "Designated as eKOI on %(is_eKOI_date)s " % d
        if d['is_eKOI']==0:
            outstr = "Designated as not eKOI on %(is_eKOI_date)s " % d

    return outstr

def is_EB_string(d):
    """
    Return a string explaining the disposition status of EB

    Parameters
    -----------
    d : dictionary with 
        - is_EB
        - is_EB_date
    """

    is_EB = d['is_EB']
    
    if is_EB==None:
        outstr = "No disposition" % d
    else:
        outstr = "Designated is %s on %s " % (is_EB,d['is_EB_date'])
    return outstr

def db_insert(dbpath,dbidx):
    form = request.form
    print form
    keys = form.keys()
    if len(keys)==0:
        return None

    key = keys[0]
    if key=='is_eKOI':
        db_key = 'is_eKOI'
        dict_db_val = dict(Yes=1, No=0, NULL=None)
    elif key=='is_EB':
        db_key = 'is_EB'
        dict_db_val = dict(Y_OOT='Y_OOT', Y_SE='Y_SE', N='N', NULL=None)
    else:
        return None

    d = {}
    d[db_key] = dict_db_val[form[key]]
    db_date_key = db_key+'_date'
    d[db_date_key] = strftime("%Y-%m-%d %H:%M:%S")

    sqlcmd = "UPDATE candidate SET %s=?,%s=? WHERE id=?" % (db_key,db_date_key)
    values = (d[db_key],d[db_date_key],dbidx)
    con = sqlite3.connect(dbpath)
    with con:
        cur = con.cursor()
        cur.execute(sqlcmd,values)


is_EB_buttons = {
    'Y_SE':'Y Secondary Eclipse',
    'Y_OOT':'Y OOT Variability',
    'N':'N'
}

def starname_to_dbidx(dbpath,starname):
    print "connecting to database %s" % dbpath 

    con = sqlite3.connect(dbpath)
    with con:
        cur = con.cursor()
        query = """
        SELECT id from candidate 
        GROUP BY starname
        HAVING id=MAX(id)
        AND starname=%s""" % starname

    cur.execute(query)
    dbidx, = cur.fetchone()
    return dbidx


class Vetter(object):
    def __init__(self,k2_camp,run,starname_url):
        self.k2_camp = k2_camp
        self.run = run
        self.starname_url = starname_url

        self.tpspath = os.path.join(K2_ARCHIVE,'TPS/%s/' % run )
        self.dbpath = os.path.join(K2_ARCHIVE,self.tpspath,'scrape.db')
        cat = k2_catalogs.read_cat(k2_camp)
        cat.index = cat.epic.astype(str)
        self.cat = cat

    def starname_to_dbidx(self):
        return starname_to_dbidx(self.dbpath,self.starname_url)
    def get_display_vetting_tempVars(self):
        cat = self.cat
        dbidx = self.starname_to_dbidx()

        starname = self.starname_url
        run = self.run
        dbpath = self.dbpath
        db_insert(dbpath,dbidx)
        con = sqlite3.connect(self.dbpath)
        query = "SELECT * from candidate WHERE id=%i" % dbidx
        df = pd.read_sql(query,con)
        con.close()

        if len(df)==0:
            return "Star %s not in %s" % (starname,tps_basedir0)
        if len(df)>1:
            return "Row returned must be unique"

        dfdict = dict(df.iloc[0] )
        table = df['P t0 tdur s2n grass num_trans'.split()]
        tablelong = df
        table,tablelong = map(lambda x : dict(x.iloc[0]),[table,tablelong])

        table['Depth [ppt]'] = 1e3*tablelong['mean']
        tempVars = { 
            "table":table,
            "tablelong":tablelong,
            "cattable":cat.ix[starname]
       }

        coords = cat['ra dec'.split()].itertuples(index=False)
        coords = map(list,coords)
        target = dict(cat.ix[starname]['ra dec'.split()])
        target['starname'] = starname
        tempVars['target'] = target
        starcoords = cat.ix[[starname]]['ra dec'.split()].itertuples(index=False),
        chartkw = dict(
            coords = coords,
            starcords = starcoords,
            starname = starname
        )

        tempVars = dict(tempVars,**chartkw)
        tempVars['is_eKOI_string'] = is_eKOI_string(dfdict)
        tempVars['is_EB_string'] = is_EB_string(dfdict)
        tempVars['is_EB_buttons'] = is_EB_buttons
        tempVars['run'] = run
        tempVars['phot_outdir'] = os.path.join(
            K2_ARCHIVE_URL,'photometry/%s/output/%s/' % (run,starname)
            )
        tempVars['tps_outdir'] = os.path.join(
            K2_ARCHIVE_URL,'TPS/%s/output/%s/' % (run,starname)
            )
        return tempVars

@app.route('/vetting/<k2_camp>/<run>/<starname_url>',methods=['GET','POST'])
def display_vetting(k2_camp,run,starname_url):
    vetter = Vetter(k2_camp,run,starname_url)
    tempVars = vetter.get_display_vetting_tempVars()
    print "tpsoutdir" +tempVars['tps_outdir']

    html = render_template('vetting_template_C1.html',**tempVars)

    return html

@app.route('/vetting/list/<k2_camp>/<run>/',methods=['GET','POST'])
def display_vetting_list(k2_camp,run):
    # Handle button input
    if request.method == "POST":
        keys = request.form.keys()
        if keys.count('starname_list')==1:
            starname_list = request.form.get('starname_list', '').split()
            session['username'] = request.form.get('username','')
            session['starname_list'] = map(str,starname_list)
            session['nstars'] = len(starname_list)
        if keys.count('prev')==1:
            session["starlist_index"]-=1
        if keys.count('next')==1:
            session["starlist_index"]+=1
        if keys.count('clear')==1:
            session.clear()

    dbpath = os.path.join(K2_ARCHIVE,'TPS/%s/scrape.db' % run)

    # Default behavior when the page is first loaded
    if "starname_list" not in session:
        return render_template('vetting_session_start_template.html')    
    if len(session["starname_list"])==0:
        return render_template('vetting_session_start_template.html')    
    if "starlist_index" not in session:
        session["starlist_index"] = 0

    if session['starlist_index'] < 0:
        session['starlist_index'] = 0 
    if session['starlist_index'] >= session['nstars']:
        session['starlist_index'] = session['nstars'] - 1
    
    print session
    res = query_starname_list(dbpath,session['starname_list'])
    starname_current = res.iloc[ session['starlist_index']]['starname']
    vetter = Vetter(k2_camp,run,starname_current)

    res['starname_current'] = (res['starname']==starname_current)
    res = res.to_dict('records')
    
    tempVars = vetter.get_display_vetting_tempVars()    
    tempVars['res'] = res
    print tempVars['tps_outdir']
    template = render_template('vetting_session_template.html',**tempVars)
    return template

def query_starname_list(dbpath,starname_list):
    con = sqlite3.connect(dbpath)
    with con:
        cur = con.cursor()
        query = """
SELECT starname,is_eKOI,is_EB from candidate 
GROUP BY starname
HAVING id=MAX(id)
AND starname in %s""" % str(tuple(starname_list))
        cur.execute(query)
        res = cur.fetchall()
    
    res = pd.DataFrame(res,columns=['starname','is_eKOI','is_EB'])
    res.index = res.starname
    res = res.ix[starname_list]
    res['is_eKOI_color'] = res.is_eKOI.apply(is_eKOI_to_color)
    res['is_EB_color'] = res.is_EB.apply(is_EB_to_color)
    return res

def is_EB_to_color(s):
    if s==None:
        return 'LightGray'
    elif s[0]=='Y':
        return 'Tomato'
    elif s[0]=='N':
        return 'RoyalBlue'

def is_eKOI_to_color(is_eKOI):
    if is_eKOI==1:
        return 'RoyalBlue'
    elif is_eKOI==0:
        return 'Tomato'
    else:
        return 'LightGray'

if __name__=="__main__":
#    app.config['PROFILE'] = True
#    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    app.run(host=host,port=port,debug=True)
