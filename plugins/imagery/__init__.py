import displayplugin as dp

import datetime as dt
import os, shutil
import urllib
from subprocess import call



class Imagery:
    def update(self):
        tmpdir = dp.gentmpdir()
        
        params = {
            'enabled'     : True,
            'updateFreq'  : dt.timedelta(minutes=20),
            'dispDuration': dt.timedelta(seconds=60),
            'priority'    : (1,1.0),
            'location'    : 'half',
            'html'        : 'file://'+tmpdir+"/imagery.html"
        }

        ## copy required files to the temporary directory
        shutil.copy('style.css', tmpdir)
        shutil.copy('imagery.html', tmpdir)

        ## arguments to be used by "gifsicle" for altering the animated gifs
        args = '--loop -d 25 "#0--1" -d300 "#-1" --colors=256 -O2 --resize "1064"x"769"'

        ## visibile imagery
        filename="http://www.ssd.noaa.gov/goes/east/eaus/vis-animated.gif"
        urllib.URLopener().retrieve(filename, tmpdir+"/visa.gif")
        call('gifsicle {0}/visa.gif {1} > {0}/vis.gif'.format(tmpdir,args),shell=True)
        if not os.path.exists(tmpdir+'/vis.gif'):
            raise Exception("vis.gif file was not found during update")

        ## infrared imagery
        filename = "http://www.ssd.noaa.gov/goes/east/eaus/rb-animated.gif"
        urllib.URLopener().retrieve(filename, tmpdir+"/rba.gif")
        call('gifsicle {0}/rba.gif {1} > {0}/rb.gif'.format(tmpdir,args),shell=True)
        if not os.path.exists(tmpdir+'/rb.gif'):
            raise Exception("rb.gif file was not found during update")

        ## water vapor imagery
        filename = "http://www.ssd.noaa.gov/goes/east/eaus/wv-animated.gif"
        urllib.URLopener().retrieve(filename, tmpdir+"/wva.gif")
        call('gifsicle {0}/wva.gif {1} > {0}/wv.gif'.format(tmpdir,args),shell=True)
        if not os.path.exists(tmpdir+'/wva.gif'):
            raise Exception("wva.gif file was not found during update")

        return params


## the list of all available displays in this plugin,
## as required by the plugin loader
def init():
    return  [Imagery()]
