#!/usr/bin/python
# archiveuploader, upload fscons2017 vids + metadata to archive.org
# 2018, david noble

# general imports
import os
from internetarchive import upload
import vidmeta

# settings

queuedir = "/home/dave/storage/Video/Various/fscons2017/complete-talks"
completelist = "/home/dave/storage/Video/Various/fscons2017/archived.dat"
collection = "opensource_movies"
creator = "Norwegian UNIX User Group"
subject = "FSCONS 2017"

# functions

def dummyupload(talk, col, crtr, subj):
    metafile = os.path.join(queuedir, talk, "data.xml")
    mediafile = os.path.join(queuedir, talk, (talk + ".webm"))
    vm = vidmeta.parse(metafile)
    spkrlist = []
    for spkr in vm.get_speakers().get_speaker():
        spkrlist.append(spkr.get_speakerName())
    identifier = vm.get_slug()[:100] if len(vm.get_slug()) > 100 else vm.get_slug()
    md = dict(mediatype = "movies", collection = col, title = vm.get_title(), creator = crtr, subject = subj, description = vm.get_description(), credits = ", ".join(spkrlist))
    print("##### METADATA ######\n%s" % md)
    print("##### IDENTIFIER ######\n%s" % identifier)
    print("##### MEDIAFILE ######\n%s" % mediafile)


def realupload(talk, col, crtr, subj):
    metafile = os.path.join(queuedir, talk, "data.xml")
    mediafile = os.path.join(queuedir, talk, (talk + ".webm"))
    vm = vidmeta.parse(metafile)
    spkrlist = []
    for spkr in vm.get_speakers().get_speaker():
        spkrlist.append(spkr.get_speakerName())
    identifier = vm.get_slug()[:100] if len(vm.get_slug()) > 100 else vm.get_slug()
    md = dict(mediatype = "movies", collection = col, title = vm.get_title(), creator = crtr, subject = subj, description = vm.get_description(), credits = ", ".join(spkrlist))
    print("##### METADATA ######\n%s" % md)
    print("##### IDENTIFIER ######\n%s" % identifier)
    print("##### MEDIAFILE ######\n%s" % mediafile)
    r = upload(identifier, files=[mediafile, metafile], metadata = md)
    if r[0].status_code == 200: 
        print("Upload successful!")
        with open(completelist, "a") as cl:
            cl.write(talk)
    else:
        print("Upload failed!?")
# main loop

for talk in os.listdir(queuedir): 
    realupload(talk, collection, creator, subject)

    
