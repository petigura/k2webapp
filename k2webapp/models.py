import sqlite3
from time import strftime
import os
from k2phot.io_utils import k2_catalogs
from flask import request 
import pandas as pd

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

    def template_variables(self):
        """
        Return dictionary used to render the template.
        """
        tempVars = { 
#            "table":table,
#            "tablelong":tablelong,
            "cattable":self.cat.ix[self.starname]
        }

        coords = self.cat['ra dec'.split()].itertuples(index=False)
        coords = map(list,coords)
        target = dict(self.cat.ix[self.starname]['ra dec'.split()])
        target['starname'] = self.starname
        tempVars['target'] = target
        starcoords = self.cat.ix[[self.starname]]['ra dec'.split()].itertuples(index=False),
        chartkw = dict(
            coords = coords,
            starcords = starcoords,
            starname = self.starname
        )
        tempVars = dict(tempVars,**chartkw)

        tempVars['phot_outdir'] = self.phot_outdir
        return tempVars 
        

class Vetter(Photometry):
    def __init__(self, k2_camp, run, starname_url):
        super(self.__class__, self).__init__(k2_camp, run, starname_url)
        self.tpspath = os.path.join(K2_ARCHIVE,'TPS/%s/' % run )
        self.dbpath = os.path.join(K2_ARCHIVE,self.tpspath,'scrape.db')

    def starname_to_dbidx(self):
        return starname_to_dbidx(self.dbpath,self.starname_url)

    def template_variables(self):
        tempBars = super(self.__class__, self).template_variables()

        cat = self.cat
        dbidx = self.starname_to_dbidx()
        starname = self.starname_url
        run = self.run
        dbpath = self.dbpath
        db_insert(dbpath,dbidx)
        db_insert_comments(dbpath,dbidx)
        # Pull current values from datavase row
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
        tempVars['is_eKOI_string'] = is_eKOI_string(dfdict)
        tempVars['is_EB_string'] = is_EB_string(dfdict)
        tempVars['run'] = run
        tempVars['tps_outdir'] = os.path.join(
            K2_ARCHIVE_URL,'TPS/%s/output/%s/' % (run,starname)
            )
        print tempVars['phot_outdir']
        print dfdict
        tempVars['vetting_comment'] = dfdict['vetting_comment']
        return tempVars

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

