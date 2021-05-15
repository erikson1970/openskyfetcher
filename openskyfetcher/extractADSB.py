import json
from struct import unpack,calcsize
from gzip import decompress
from base64 import b64decode
import os


def getGoodFile(
    filename="default_blob422_18", path=".", extension=".adsb", showSize=True
):
    while not os.path.isfile(filename):
        print("Invalid File: ", filename)
        chooser = []
        for FN in sorted(os.listdir(path)):
            if FN.lower().endswith(extension):
                print(
                    "{} - {} {}".format(
                        str(len(chooser)).rjust(3),
                        str(len(open(FN).readlines())).rjust(6, ".") + " lines - "
                        if showSize
                        else "",
                        FN,
                    )
                )
                chooser.append(FN)
        choice = input(
            "Choose " + str(range(len(chooser))) + " or Enter Valid Filename: "
        )
        if len(choice) < 3:
            filename = chooser[int(choice)]
        print("You Chose: ", filename)
        return filename


def getCSV(filename="filename"):
    packSize=-1
    with open(filename, "r") as fp1:
        for i, theLine in enumerate(fp1):
            theLine = theLine.strip()
            try:
                if i == 0:
                    # skipping line 0
                    continue
                else:
                    # print("FILE INPUT:", theLine)
                    if len(theLine) < 2:
                        continue
                    else:
                        ff = json.loads(
                            theLine[:-1] if theLine.endswith((",", "]]")) else theLine
                        )
            except Exception as e:
                print("Line {}: JSON/READING error - Bad Line: {}".format(i, theLine))
                print(e)
                continue
            if ff[1] == "STRUCTURE":
                outerfields, innerfields, field_packFMT, compression = ff[-1]
                packSize=calcsize(field_packFMT)
                specialFields = {ii: [] for ii in outerfields}
                useCompression = int(compression.split("=")[-1])
                print(",".join(["receive_time"] + outerfields + innerfields))
            elif ff[1] == "BBOX" or ff[1] == "error":
                ## skipping bounding box and errors in input file
                continue
            elif ff[1] == "CLOSED":
                print("Completed Parsing")
                break
            elif ff[1] == "STATES":
                for stateEntry in [
                    b64decode(ff[-1][2:-1])[ii * packSize : (ii + 1) * packSize]
                    if ff[2] < useCompression
                    else decompress(b64decode(ff[-1][2:-1]))[ii * packSize : (ii + 1) * packSize]
                    for ii in range(ff[2])
                ]:
                    result = list(unpack(field_packFMT, stateEntry))
                    for ii, jj in enumerate(outerfields):
                        result[ii] = '"{}"'.format(specialFields[jj][result[ii]])
                    print(",".join([str(ii) for ii in [ff[0]] + result]))
            elif ff[1] == "IDX_UPDATE":
                indices = json.loads(
                    decompress(b64decode(ff[-1][2:-1])).decode("utf-8")
                )
                for idx in indices:
                    specialFields[idx[0]] = idx[1]
            else:
                print("Line {}: parsing error - Bad Line Type: {}".format(i, ff[1]))


if __name__ == "__main__":
    filename = "default_blob422_18.adsb"
    filename = getGoodFile()
    getCSV(filename)

