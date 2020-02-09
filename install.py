import bs
import bsInternal
import os
import shutil
import json
import urllib
import urllib2
install_modules=[]
for i in ["zipfile", "io", "string", "re"]:
    try: __import__(i)
    except ImportError: install_modules.append(i+".py")
import bsUI
installerNowVersion = 1

class InstallError(Exception):
    def __init__(self):
        pass

class DownloadError(Exception):
    def __init__(self, url, path):
        self.path = path
        self.url = url

env=bs.getEnvironment()
gInstallPath=str(env["userScriptsDirectory"])
#str(env["configFilePath"].split("/")[0:-2]) if env["platform"] == "android" else str(env["userScriptsDirectory"])

if env["platform"] == "android":
    import socket
    proxy_handler = urllib2.ProxyHandler({"https": "https://github.com"})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)

def download(url, path):
    try:
        u = urllib2.urlopen(url.replace(" ", "%20"))
        fp = open(path, 'wb')
        while True:
            chunk = u.read(8192)
            if not chunk: break
            fp.write(chunk)
        fp.close()
    except Exception as E:
        print(str(E))
        raise DownloadError(url=url, path=path)

if len(install_modules) > 0:
    for i in install_modules:
        download("https://github.com/DrovGamedev/BombSquad-Hardcore-Modpack/raw/master/"+i, gInstallPath)

def get_versions_from_source(last=False):
    file = "versions.json"
    path = os.path.join(gInstallPath, file)
    url = "https://github.com/DrovGamedev/BombSquad-Hardcore-Modpack/raw/master/"+file
    download(url=url, path=path)
    data={}
    try:
        if os.path.exists(path): data=json.load(open(path))
    except Exception:
        data={}
        os.remove(path)
        print("versions-file was broken")
    if last:
        if len(data) > 0:
            a={"None": 0}
            for i in data:
                if data.get(i) > a.get(a.keys()[0]): a={i: data.get(i)}
            if a.get("None") is None: data=a
    return data

installedVersionPath = os.path.join(gInstallPath, "about_modpack.json")
if os.path.exists(installedVersionPath):
    try: installed_version = json.load(open(installedVersionPath))
    except Exception: installed_version = 0
else: installed_version = 0
versions = get_versions_from_source()
if len(versions) > 0:
    last_version = {"None": 0}
    for i in versions:
        if i != "install.py":
            if versions.get(i) > last_version.get(last_version.keys()[0]): last_version = {i: versions.get(i)}
    if last_version.get("None") is not None: last_version = {}
installer_version = versions.get("install.py", 0)
versions.pop("install.py")

if installerNowVersion < installer_version:
    download("https://github.com/DrovGamedev/BombSquad-Hardcore-Modpack/raw/master/install.py", gInstallPath)
    bs.quit()

def format_version(file):
    path=gInstallPath
    result=0
    try: modpack=zipfile.ZipFile(file=os.path.join(path, file))
    except Exception: modpack=None
    if modpack is not None:
        if "about_modpack.json" in modpack.namelist():
            path=(os.path.join(os.path.join(path, "temp_path"), file))
            modpack.extract("about_modpack.json", path)
            try: result=int(json.load(open(os.path.join(path, "about_modpack.json"), "r")).get("version", {"v":0}).get("v"))
            except Exception as E: bsInternal._log("error reading version-file: "+str(E))
        modpack.close()
    return result

def update(version=None, ignore_old_versions=True):
    if version is None: version=last_version.get(last_version.keys()[0]) if len(last_version) > 0 else None
    path=(os.path.join(gInstallPath, "about_modpack.json"))
    if isinstance(version, int):
        if version in versions.values(): version = {"version": {"name": i, "v": versions.get(i)} for i in versions if versions.get(i) == version}
    if isinstance(version, dict):
        if len(version) > 0:
            def inst():
                json.dump(version, open(path, "w+"))
                extract_file(data=version)
            if ignore_old_versions:
                if installed_version < version["version"]["v"]: inst()
            else: inst()

def load(version=None):
    path = gInstallPath
    try:
        if version is None: files = last_version if last_version is not None else {}
        else:
            files = versions
            files = {i: files.get(i) for i in files if files.get(i) == version}
        if len(files) > 0:
            for i in files:
                if not isinstance(i, str): i=str(i)
                path=os.path.join(path, i)
                if not os.path.exists(path): download("https://github.com/DrovGamedev/BombSquad-Hardcore-Modpack/raw/master/"+i, path)
    except Exception as E:
        bsInternal._log(str(E))

def get_loaded_versions(debug=False):
    path=gInstallPath
    version_install={}
    if len(os.listdir(path))>0:
        versions_list=[i for i in os.listdir(path) if zipfile.is_zipfile(path+"/"+i)]
        if debug: bsInternal._log(str(versions_list))
        versions={}
        for i in versions_list:
            a=format_version(file=i)
            if a > 0: versions.update({a: i})
        if debug: bsInternal._log(str(versions))
        if len(versions) > 0:
            version_install=versions.keys()[0]
            for i in versions:
                if debug: bsInternal._log(str(i))
                if i > version_install: version_install=i
            version_install={version_install: versions.get(version_install)}
        if os.path.exists(os.path.join(path, "temp_path")): shutil.rmtree(os.path.join(path, "temp_path"))
    return version_install

def extract_file(data={}):
    try:
        path=os.path.join(gInstallPath, str(data["version"]["name"]))
        if os.path.exists(path) and zipfile.is_zipfile(path):
            zipfile.ZipFile(path).extractall(gInstallPath)
            bs.screenMessage(bs.Lstr(resource='settingsWindowAdvanced.mustRestartText'), color=(1, 1, 0))
    except Exception:
        raise InstallError()

def update_modpack(net=False, version=None):
    if version is None:
        if net: load(last_version)
        if len(last_version) > 0: update()
    else:
        if version in versions.values():
            if version not in get_loaded_versions().values(): load(version=version)
            a = get_loaded_versions()
            if version in a.values(): update(version=version, ignore_old_versions=False)



if "get_setting" in dir(bs):
    if bs.get_setting("auto-update", False): update_modpack(True)
else: update_modpack(True)