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
api = OpenSkyApi(username="erikson1988", password="hooda-1581-pigger!")
# api = OpenSkyApi()
#######Bounding Boxes#########
bboxes = {
    "USNorthEast": (40.3, 43.0, -75.1, -70.5),
    "USNorthEast-RICTShore": (41.1, 42.0, -72.3, -71.0),
    "midatlantic": (36.6, 39.5, -77.0, -74.0),
    "EasternVAShore": (36.5, 39.0, -76.5, -70.75),
    "francoEurope": (45.8389, 47.8229, 5.9962, 10.5226),
}
bboxname = "USNorthEast-RICTShore"
##############
bbox = bboxes[bboxname]
sh = {"time": -1, "states": []}
for i in range(7200):
    try:
        sh = api.get_states(time_secs=0, bbox=bbox)
        now = datetime.now()
        print(
            "Time: {}  ".format(now.strftime("%y%m%d-%H:%M:%S")), end="",
        )
        print(" Update time: {}  Got: {} reports!".format(sh.time, len(sh.states)))
    except Exception as e:
        print("Something broke", e)
    time.sleep(3)
