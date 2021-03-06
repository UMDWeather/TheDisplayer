################################################################################
## SPC Outlook Plugin:
## 
## Reads the shape files for day 1, 2, and 3 of the SPC outlooks from the SPC
## website. If there is any activity at our current lat/lon location
## (defined as location below) OR if there is unusually severe weather anywhere
## across the country, the appropriate maps will be shown for those days.
## Additionally, if our location has hail, tornado, wind probabilities, those
## maps are shown as well
################################################################################
import displayplugin as dp

import datetime as dt
import os,shutil
import spc
import urllib
import re


## Configurables
#########################

## The categorical outlook levels in ascending order of severity are:
##   (TSTM, MRGL, SLGT, ENH, MDT, HIGH)

minLocOutlook = "TSTM"          # minimum level of convection probability
                                # for our local area to trigger the map shown

minNatOutlook = "ENH"           # same as above, except for the whole nation


dispTime = 8000                 # time (msec) to show each image in slideshow


#####################################################################

      
class Outlook:
    def update(self):
        tmpdir = dp.gentmpdir()            
        params = {
            'enabled'     : False,
            'updateFreq'  : dt.timedelta(minutes=30),
            'dispDuration': dt.timedelta(seconds=45),
            'priority'    : (1,2.0),
            'location'    : 'half',
            'html'        : 'file://'+tmpdir+'/spc_outlook.html'
        }
        shutil.copy('style.css',tmpdir)
        
        ## determine which day outlooks we need to display
        allOutlooks = spc.getOutlooksForLoc()
        myOutlooks  = spc.getOutlooksForLoc(latlon)
        imgToShow=[]
        for day in allOutlooks:

            ## if there is no categorical probability at all, skip this day
            category = 'CATEGORICAL'
            if not category in allOutlooks[day]:
                continue

            ## make sure the probability meets the minimum level
            ## for either our location, or the whole nation
            if minNatOutlook in allOutlooks[day][category] or \
               minLocOutlook in myOutlooks[day][category] :
                imgToShow.append("day{0}otlk_prt.gif".format(day))
                ## search also to see if hail, tornado, or wind
                ## maps should be shown (only if there is a probability
                ##  for our current location)
                for c in myOutlooks[day]:
                    urlWord = None
                    if c == 'TORNADO':
                        urlWord = "torn"
                    elif c == "WIND":
                        urlWord = "wind"
                    elif c == "HAIL":
                        urlWord = "hail"
                    if urlWord and len(myOutlooks[day][c]) > 0:
                        imgToShow.append("day{0}probotlk_{1}.gif".format(day,urlWord))

        ## download the images
        for img in imgToShow:
            dl = urllib.URLopener()
            dl.retrieve("http://www.spc.noaa.gov/products/outlook/"+img, tmpdir+'/'+img)

        ## also look at mesoscale discussions for our office location
        msd = spc.getMesoDiscussions(nws_office)
        count = 10
        for m in msd:
            res = re.search(r'\<img.*src\=\"(.*?)\".*\>', m['description'])
            if res:
                filename = 'mes{0:02d}.gif'.format(count)
                urllib.URLopener().retrieve(res.group(1),tmpdir+'/'+filename)
                imgToShow.append(filename)
        
        ## Create the html file to display
        with open(tmpdir+'/spc_outlook.html','w') as html:
            slideshow = ""
            if len(imgToShow) > 1:
                slideshow = 'id="slideshow"'
            
            html.write('''
<html>
  <head>
    <link rel="stylesheet" type="text/css" href="../common/style.css">
    <link rel="stylesheet" type="text/css" href="style.css">
    <script src="../common/jquery.min.js"></script>
    <script>
      $(function() {
        $("#slideshow > div:gt(0)").hide();
        setInterval(function() {
          $('#slideshow > div:first')
           .hide()
          .next()
          .show()
          .end()
          .appendTo('#slideshow');
        },  '''+str(dispTime)+''');
      });
    </script>
 </head>
<body>
    <div '''+slideshow+''' >''');
            for img in imgToShow:
                dayNum = img[3]
                html.write('<div class="slide wrapper"><div class="header"><h1>Severe Weather Outlook  (Day {1})</h1></div><div class="content"><img src="{0}"/></div></div>'.format(img,dayNum))
            html.write('''
  </div>
</body>
</html>''')
        params['enabled'] = len(imgToShow) > 0
        return params


## the list of all available displays in this plugin,
## as required by the plugin loader
def init():
    return [ Outlook() ]
