# render a HTML template with the given context variables
from flask import render_template, request,session
import models
import os
import pandas as pd
K2_ARCHIVE = os.environ['K2_ARCHIVE']

def display_photometry(k2_camp,run,starname):
    phot = models.Photometry(k2_camp, run, starname)
    tempVars = phot.template_variables()
    html = render_template('photometry.html',**tempVars)
    return html

def photometry_json(k2_camp,run,starname):
    phot = models.Photometry(k2_camp, run, starname)
    return phot.get_photometry_json()

def display_vetting(k2_camp,run,starname):
    vetter = models.Vetter(k2_camp,run,starname)
    tempVars = vetter.template_variables() 
    print "tpsoutdir" +tempVars['tps_outdir']
    html = render_template('vetting.html',**tempVars)
    return html

def display_vetting_list(k2_camp, run):
    # Handle button input
    if request.method == "POST":
        keys = request.form.keys()
        if keys.count('candidatename_list')==1:
            candidatename_list = request.form.get('candidatename_list', '').split()
            session['username'] = request.form.get('username','')
            session['candidatename_list'] = map(str,candidatename_list)
            session['nstars'] = len(candidatename_list)
        if keys.count('prev')==1:
            session["index"]-=1
        if keys.count('next')==1:
            session["index"]+=1
        if keys.count('clear')==1:
            session.clear()

    dbpath = os.path.join(K2_ARCHIVE,'TPS/scrape.db')

    # Default behavior when the page is first loaded
    if "candidatename_list" not in session:
        return render_template('vetting_session_start.html')    
    if len(session["candidatename_list"])==0:
        return render_template('vetting_session_start.html')    
    if "index" not in session:
        session["index"] = 0

    if session['index'] < 0:
        session['index'] = 0 
    if session['index'] >= session['nstars']:
        session['index'] = session['nstars'] - 1

    res = models.query_candidatename_list(dbpath, run, session['candidatename_list'])
    print res

    if type(res)==type(None):
        return render_template('vetting_session_start_nostars.html')    
    
    inp = pd.DataFrame(session['candidatename_list'], columns=['candidatename'])
    notin = inp[~inp.candidatename.isin(res.candidatename)]
    if len(notin) > 0:
        return "{} not in database".format( notin.candidatename.tolist())

    candidatename_current = res.iloc[session['index']]['candidatename']
    vetter = models.Vetter(k2_camp, run, candidatename_current)
    res['candidatename_current'] = (res['candidatename']==candidatename_current)
    res = res.to_dict('records')
    tempVars = vetter.template_variables()
    print tempVars
    tempVars['res'] = res
    template = render_template('vetting_session.html',**tempVars)
    return template
