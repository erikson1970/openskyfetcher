import base64
from gzip import compress
from base64 import b64encode
from json import dumps
import time
from datetime import datetime
from struct import pack
import traceback
import credentials
import openskyapi

# datetime object containing current date and time
now = datetime.now()
print("now =", now)
dt_string = now.strftime("%y%m%d-%H:%M:%S")

# records time of first data entry, time of last and number of reports.
firstTime = -1
lastTime = -1
stateReports = 0

# Fields in data
field = [
    "icao24",
    "callsign",
    "origin_country",
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "heading",
    "vertical_rate",
    "sensors",
    "geo_altitude",
    "squawk",
    "spi",
    "position_source",
]
innerfields = [
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "heading",
    "vertical_rate",
    "geo_altitude",
    "spi",
    "position_source",
]
outerfields = ["icao24", "callsign", "origin_country", "squawk"]
# includes index short int for "icao24", "callsign", "origin_country"
field_packFMT = "HHHHLLfff?ffff?H"
pack_ERROR = pack(
    field_packFMT, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, False, 0.0, 0.0, 0.0, 0.0, False, 0
)

# Compression: 9999 ==> always , 0 ==> never, 1...N ==> if more than N states are reported
useCompression = 6

specialFields = {ii: {} for ii in outerfields}

# Proxy & SSL handling
useProxy = False
proxydict = None
if useProxy:
    commonProxy = (
        credentials.creds["commonProxy"].hostname
        if "commonProxy" in credentials.creds
        else None
    )
    proxydict = (
        {"http": commonProxy, "https": commonProxy, "ftp": commonProxy}
        if not commonProxy is None
        else {
            "http": credentials.creds["httpProxy"].hostname
            if "httpProxy" in credentials.creds
            else None,
            "https": credentials.creds["httpsProxy"].hostname
            if "httpsProxy" in credentials.creds
            else None,
            "ftp": credentials.creds["ftpProxy"].hostname
            if "ftpProxy" in credentials.creds
            else None,
        }
    )
SSLverify = credentials.creds["SSLverify"].hostname if "SSLverify" in credentials.creds else True
print("Proxy: {}   SSL Verif: {} ".format(proxydict, SSLverify))

#
credID = "myAPIkey" if "myAPIkey" in credentials.creds else "default"

api = openskyapi.OpenSkyApi(
    username=credentials.creds[credID].username,
    password=credentials.creds[credID].password,
    proxyDict=proxydict,
    verify=SSLverify,
)

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
filename = "ADSB_DATA_{}_{}.adsb".format(bboxname, now.strftime("%y%m%d-%H%M%S"))
bbox = bboxes[bboxname]
print("writing ADSB Data to {}".format(filename))
with open(filename, "w") as file1:
    file1.write('[\n[{},"{}",{},{}],\n'.format(int(time.time()), "BBOX", 0, list(bbox)))
    file1.write(
        '[{},"{}",{},{}],\n'.format(
            int(time.time()),
            "STRUCTURE",
            0,
            dumps(
                [
                    outerfields,
                    innerfields,
                    field_packFMT,
                    "useCompression={}".format(useCompression),
                ]
            ),
        )
    )
sh = {"time": -1, "states": []}
try:
    for i in range(7200):
        try:
            #            print("sh:", sh)
            try:
                sh = api.get_states(time_secs=0, bbox=bbox)
            except (KeyboardInterrupt, SystemExit) as sh_e:
                raise sh_e
            except Exception as sh_e:
                print(
                    "{} / {} Error: During API Fetch {}".format(
                        datetime.now().strftime("%y%m%d-%H:%M:%S"),
                        int(time.time()),
                        sh_e,
                    )
                )
                sh = None
            if not sh is None:
                with open(filename, "a") as file1:  # append mode
                    changeInners = set([])
                    if sh.states and len(sh.states) > 0:
                        statesArr = []
                        for sVect in sh.states:
                            thisStateArr = []
                            tState = sVect.__dict__
                            for specF in outerfields:
                                if tState[specF] in specialFields[specF]:
                                    thisIDX = specialFields[specF][tState[specF]]
                                else:
                                    thisIDX = (
                                        max([-1] + list(specialFields[specF].values()))
                                        + 1
                                    )
                                    specialFields[specF][tState[specF]] = thisIDX
                                    changeInners.add(
                                        specF
                                    )  # keep track of which inners have changed values
                                thisStateArr.append(thisIDX)
                            thisStateArr.extend([tState[jj] for jj in innerfields])
                            #                        print("thisStateArr:", thisStateArr)
                            try:
                                statesArr.append(pack(field_packFMT, *thisStateArr))
                            except Exception as e:
                                print("Pack Error: {},\n {}".format(e, thisStateArr))
                                statesArr.append(pack_ERROR)
                        if changeInners:
                            file1.write(
                                '[{},"{}",{},"{}"],\n'.format(
                                    int(time.time()),
                                    "IDX_UPDATE",
                                    len(changeInners),
                                    str(
                                        b64encode(
                                            compress(
                                                dumps(
                                                    [
                                                        [
                                                            jjj,
                                                            list(
                                                                list(
                                                                    zip(
                                                                        *sorted(
                                                                            [
                                                                                (v, k)
                                                                                for k, v in specialFields[
                                                                                    jjj
                                                                                ].items()
                                                                            ]
                                                                        )
                                                                    )
                                                                )[1]
                                                            ),
                                                        ]
                                                        for jjj in changeInners
                                                    ]
                                                ).encode("utf-8")
                                            )
                                        )
                                    ),
                                )
                            )
                        if firstTime < 0:
                            firstTime = sh.time
                        lastTime = sh.time
                        stateReports += len(sh.states)
                        if useCompression < 0 or (
                            useCompression > 0 and len(sh.states) >= useCompression
                        ):
                            file1.write(
                                '[{},"{}",{},"{}"],\n'.format(
                                    int(time.time()),
                                    "STATES",
                                    len(sh.states),
                                    str(b64encode(compress(b"".join(statesArr)))),
                                )
                            )
                        else:
                            file1.write(
                                '[{},"{}",{},"{}"],\n'.format(
                                    int(time.time()),
                                    "STATES",
                                    len(sh.states),
                                    str(b64encode(b"".join(statesArr))),
                                )
                            )
                        # str.encode(dumps([i.__dict__ for i in sh.states]))))))
                    else:
                        file1.write(
                            "[{},{},0,None],\n".format(int(time.time()), "ERROR")
                        )
                print(
                    "{} Update at: {} / {} with {} state vectors. {} unique icao24 seen.".format(
                        datetime.now().strftime("%y%m%d-%H:%M:%S"),
                        int(time.time()),
                        sh.time,
                        len(sh.states),
                        len(specialFields["icao24"]),
                    )
                )
                time.sleep(10)
            else:
                print(
                    "{} / {} No data: openSky returned None".format(
                        datetime.now().strftime("%y%m%d-%H:%M:%S"), int(time.time())
                    )
                )
                time.sleep(2)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            with open(filename, "a") as file1:  # append mode
                file1.write(
                    '[{},"{}",{},"{}"],\n'.format(int(time.time()), "error", 0, e)
                )
            print("Error: {}".format(e))
            print("Traceback!!!:\n")
            traceback.print_exc()
finally:
    print("Closing File...")
    with open(filename, "a") as file1:  # append mode
        file1.write(
            '[{},"{}",{},{}]\n]\n'.format(
                int(time.time()),
                "CLOSED",
                0,
                '{{"totalTime":{},"lastTime":{},"stateReports":{},"unique":{}}}'.format(
                    lastTime - firstTime,
                    lastTime,
                    stateReports,
                    len(specialFields["icao24"]),
                ),
            )
        )

