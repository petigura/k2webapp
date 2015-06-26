#!/usr/bin/env python 
from k2webapp import app

if __name__=="__main__":
    app.run(host=app.config['host'],port=app.config['port'],debug=True)
