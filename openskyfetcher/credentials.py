from json import loads, load, dumps
from os import path


class credential:
    def __init__(self, identifier, hostname, username, password):
        self.identifier = identifier
        self.hostname = hostname
        self.username = username
        self.password = password

    def __str__(self):
        return 'ID: "{}",HN:"{}", UN:"{}", PW:"{}"'.format(
            self.identifier, self.hostname, self.username, self.password
        )

creds = {}

creds["default"] = credential("default", "openskyapi", "", "")
if path.isfile("credentials.json"):
    with open("credentials.json", "r") as fp1:
        for ii in load(fp1):
            creds[ii[0]] = credential(*ii)

if __name__ == "__main__":
    for k, v in creds.items():
        print(k, v)
