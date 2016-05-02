import os
import sqlite3
from time import strftime

from flask import request 
import pandas as pd
import numpy as np
from astropy.io import fits
import h5py

from k2phot.io_utils import k2_catalogs
from k2phot.config import bjd0
import k2utils.photometry
from k2phot.lightcurve import Normalizer

K2_ARCHIVE = os.environ['K2_ARCHIVE']
K2_ARCHIVE_URL = os.environ['K2_ARCHIVE_URL']

class Photometry(object):
    def __init__(self, k2_camp, run, starname):
        self.k2_camp = k2_camp
        self.run = run
        self.starname = starname
        cat = k2_catalogs.read_cat(k2_camp)
        cat.index = cat.epic.astype(str)
        self.cat = cat
        self.phot_outdir = os.path.join(
            K2_ARCHIVE_URL,'photometry/%s/output/%s/' % (run,starname)
            )

        self.fitsfile = os.path.join(self.phot_outdir,'%s.fits' % starname)

    def template_variables_common(self):
        tempVars = {}
        tempVars = { 
            "cattable":self.cat.ix[self.starname]
        }
        tempVars['phot_outdir'] = self.phot_outdir
        tempVars['starname'] = self.starname
        return tempVars

    def template_variables(self):
        """
        Return dictionary used to render the template.
        """
        tempVars = self.template_variables_common()
        # Figure out location on the FOV
        field_star_coords = np.round(self.cat['ra dec'.split()],2).itertuples(index=False)
        #field_star_coords = self.cat['ra dec'.split()].itertuples(index=False)
        #field_star_coords = ["[%.1f,%.1f]" % i for i in field_star_coords]
        
        field_star_coords = map(list,field_star_coords)
        target_star_coords = \
                        self.cat.ix[self.starname]['ra dec'.split()].tolist()

        print target_star_coords
        scatter_fov = dict(
            field_star_coords = field_star_coords,
            target_star_coords = target_star_coords,
            starname = self.starname
            )
        tempVars['scatter_fov'] = scatter_fov

        # Prep the infomation for the interactive photometry plot
        lc = k2utils.photometry.read_fits(self.fitsfile)
        lc = pd.DataFrame(lc)
        lc = lc[~lc.fmask]
        t,f = lc.t,lc.fdt_t_rollmed
        norm = Normalizer(np.nanmedian(f))
        f = norm.norm(f) + 1
        t = t - bjd0
        scatter = dict(
            data=[list(tup) for tup in zip(t,f)],
            xlabel = 'BJD-%i' % bjd0,
            ylabel = 'Normalized Flux',
            title = 'Normalized Flux'
            )
        tempVars['scatter'] = scatter
        return tempVars 

class Vetter(Photometry):
    """
    Vetter object
    """
    def __init__(self, k2_camp, run, candidatename):
        starname, candidate = candidatename.split('.')
        self.candidate = int(candidate)
        super(self.__class__, self).__init__(k2_camp, run, starname)
        self.candidatename = candidatename
        self.tpspath = os.path.join(K2_ARCHIVE,'TPS/%s/' % run )
        self.dbpath = os.path.join(K2_ARCHIVE,'TPS/scrape.db')
        self.outdir = os.path.join(self.tpspath,'output/%s/' % self.starname )
        
    def starname_to_dbidx(self):
        return starname_to_dbidx(self.dbpath,self.starname)

    def template_variables(self):
        tempVars = self.template_variables_common()

        cat = self.cat
        dbidx = self.starname_to_dbidx()
        starname = self.starname
        run = self.run
        dbpath = self.dbpath
        db_insert(dbpath, dbidx)
        db_insert_comments(dbpath, dbidx)

        # Pull current values from datavase row
        con = sqlite3.connect(self.dbpath)
        query = "SELECT * from candidate WHERE id=%i" % dbidx
        print query
        df = pd.read_sql(query,con)
        con.close()

        if len(df)==0:
            return "Star %s not in %s" % (starname,tps_basedir0)
        if len(df)>1:
            return "Row returned must be unique"

        dfdict = dict(df.iloc[0] )
        # phot_basedir = dfdict['phot_basedir']
        table = df #df['P t0 tdur s2n grass num_trans phot_basedir'.split()]
        tablelong = df
        table,tablelong = map(lambda x : dict(x.iloc[0]),[table,tablelong])
        # table['Depth [ppt]'] = 1e3*tablelong['mean']


        tempVars['table'] = table
        tempVars['is_eKOI_string'] = is_eKOI_string(dfdict)
        tempVars['is_EB_string'] = is_EB_string(dfdict)
        tempVars['run'] = run
        tempVars['tps_outdir'] = os.path.join(
            K2_ARCHIVE_URL,'TPS/%s/output/%s/' % (run,starname)
            )
        tempVars['vetting_comment'] = dfdict['vetting_comment']
        # tempVars['phot_run'] = phot_basedir.split('/')[-3]
        tempVars['k2_camp'] = self.k2_camp
        tempVars['candidatename'] = self.candidatename
        '''
        h5file = os.path.join(self.outdir,"{}.grid.h5".format(self.starname))
        with h5py.File(h5file) as h5:
            fit = h5['dv']['fit']['fit'][:]
            f = h5['dv']['fit']['f'][:]
            t = h5['dv']['fit']['t'][:]
            lc = h5['dv']['lc'][:]
            rLbl = h5['dv']['rLbl'][:]
            lcPF0 = h5['dv']['lcPF0'][:]

        rLbl = pd.DataFrame(rLbl)
        lc = pd.DataFrame(lc)
        lcPF = pd.DataFrame(lcPF0)
        lc = pd.merge(lc,rLbl,left_index=True,right_index=True) # Add in transit labels
        lcPF = pd.merge(lcPF['t tPF'.split()],lc,on='t')
        lcPF_even = lcPF[(lcPF.totRegLbl > 0) & (lcPF.totRegLbl % 2==0)]
        lcPF_odd = lcPF[(lcPF.totRegLbl > 0) & (lcPF.totRegLbl % 2==1)]

        
        scatter_phasefold = dict(
            data_phot=[list(tup) for tup in zip(t,f)],
            data_fit=[list(tup) for tup in zip(t,fit)],
            data_odd=[list(tup) for tup in zip(lcPF_odd.tPF,lcPF_odd.f)],
            data_even=[list(tup) for tup in zip(lcPF_even.tPF,lcPF_even.f)],            
            )
        tempVars['scatter_phasefold'] = scatter_phasefold

        b_in = (rLbl['tRegLbl']>=0) & ~lc['fmask']
        b_out = (rLbl['tRegLbl']<0) & ~lc['fmask']
        t = lc['t']
        f = lc['f']
        scatter_trans = dict(
            data_out=[list(tup) for tup in zip(t[b_out],f[b_out])],
            data_in=[list(tup) for tup in zip(t[b_in],f[b_in])],
            )
        tempVars['scatter_trans'] = scatter_trans
        '''

        return tempVars

def starname_to_dbidx(dbpath, starname):
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

def db_insert_comments(dbpath,dbidx):
    form = request.form
    keys = form.keys()
    if len(keys)==0:
        return None

    key = keys[0]
    val = form[key]
    if key=='vetting_comment':
        db_key = 'vetting_comment'
        dict_db_val = dict(Yes=1, No=0, NULL=None)
    else:
        return None 

    sqlcmd = "UPDATE candidate SET %s='%s' WHERE id=%s" % (key,val,dbidx)
    con = sqlite3.connect(dbpath)
    with con:
        cur = con.cursor()
        cur.execute(sqlcmd)

def query_candidatename_list(dbpath, run, candidatename_list):
    con = sqlite3.connect(dbpath)
    with con:
        cur = con.cursor()
        query = """
SELECT starname || '.' || substr('00'||candidate, -2, 2) as candidatename, is_eKOI, is_EB FROM candidate WHERE run='{}'
""".format(run)
        if len(candidatename_list)==1:
            query += "AND candidatename is '%s'" % candidatename_list[0]
        else:
            query += "AND candidatename in %s" % str(tuple(candidatename_list))
        cur.execute(query)
        res = cur.fetchall()
        print res

    res = pd.DataFrame(res,columns=['candidatename','is_eKOI','is_EB'])

    if len(res)==0:
        return None
    
    res.index = res.candidatename
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

