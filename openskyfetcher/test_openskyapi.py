from opensky_api import OpenSkyApi
from gzip import compress
from base64 import b64encode
from json import dumps
import time
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
print("now =", now)
dt_string = now.strftime("%y%m%d-%H:%M:%S")

# s=time.time()
# print(s)
api = OpenSkyApi(username="erikson1988",password="hooda-1581-pigger!")
#api = OpenSkyApi()
#######Bounding Boxes#########
bboxes = {"USNorthEast": (40.3, 43.0, -75.1,  -70.5),
          "USNorthEast-RICTShore":(41.1, 42.0, -72.3, -71.0 ),
          "midatlantic": (36.6, 39.5, -77.0,  -74.0),
          "EasternVAShore": (36.5, 39.0, -76.5,  -70.75),
          "francoEurope": (45.8389, 47.8229, 5.9962, 10.5226)}
bboxname = "USNorthEast-RICTShore"
##############
filename = "ADSB_DATA_{}_{}.json".format(
    bboxname, now.strftime("%y%m%d-%H%M%S"))
bbox=bboxes[bboxname]
print("writing ADSB Data to {}".format(filename))
with open(filename, "w") as file1:
    file1.write("[{},\n".format(bbox))
sh = {"time": -1, "states": []}
try:
    for i in range(7200):
        try:
            sh = api.get_states(time_secs=0, bbox=bbox)
            with open(filename, "a") as file1:  # append mode
                if sh.states and len(sh.states) > 0:
                    file1.write("[{},{},'{}'],\n".format(sh.time, len(sh.states), b64encode(compress(
                        str.encode(dumps([[ii for ii in sh.states[0].__dict__.keys()], [[jj for jj in ii.__dict__.values()] for ii in sh.states]]))))))
                    # str.encode(dumps([i.__dict__ for i in sh.states]))))))
                else:
                    file1.write("[{},0,None],\n".format(sh.time))
            print(dumps([[ii for ii in sh.states[0].__dict__.keys()], [[jj for jj in ii.__dict__.values()] for ii in sh.states]]))
            #print(sh)
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            with open(filename, "a") as file1:  # append mode
                file1.write("[{},-1,'{}'],\n".format(sh.time, e))
            print("Error: {}".format(e))
finally:
    print("Closing File...")
    with open(filename, "a") as file1:  # append mode
        file1.write("[{},0,'CLOSED']\n]\n".format(sh.time))

# for i in range(10):
#    sh = api.get_states(time_secs=int(s-1800*i), bbox=bbox)
#    print("{} {}".format(int(s-1800*i),sh))
