# render a HTML template with the given context variables
from flask import render_template, request,session
import models
import os
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
        return render_template('vetting_session_start.html')    
    if len(session["starname_list"])==0:
        return render_template('vetting_session_start.html')    
    if "starlist_index" not in session:
        session["starlist_index"] = 0

    if session['starlist_index'] < 0:
        session['starlist_index'] = 0 
    if session['starlist_index'] >= session['nstars']:
        session['starlist_index'] = session['nstars'] - 1

    res = models.query_starname_list(dbpath,session['starname_list'])
    starname_current = res.iloc[ session['starlist_index']]['starname']
    vetter = models.Vetter(k2_camp,run,starname_current)
    res['starname_current'] = (res['starname']==starname_current)
    res = res.to_dict('records')
    tempVars = vetter.template_variables()
    tempVars['res'] = res
    template = render_template('vetting_session.html',**tempVars)
    return template
