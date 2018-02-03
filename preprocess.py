#!/usr/bin/python3
# Preprocess - generate separate XML metadata for each talk
# 2017, David Noble

from xml.dom.minidom import parse, parseString
import vidmeta
import fileinput
import os

# Settings
schedule = "/home/dave/storage/Video/Various/fscons2017/schedule.xml"
mediadir = "/home/dave/storage/Video/Various/fscons2017/talks"
titleslide = "/home/dave/storage/Video/Various/fscons2017/title-template.svg"


# parse schedule
sched = parse(schedule)


# Functions
def handleTalkDetails(talk):
    td = {}
    td['id'] = talk.getAttribute("id")
    if talk.getElementsByTagName("optout")[0].firstChild.nodeValue == "false":
        td['title'] = talk.getElementsByTagName("title")[0].firstChild.nodeValue
        td['slug'] = talk.getElementsByTagName("slug")[0].firstChild.nodeValue
        try:
            td['desc'] = talk.getElementsByTagName("description")[0].firstChild.nodeValue
        except:
            print("No description found for talk {placeholder}".format(placeholder=td['id']))
            td['desc'] = "no description"
        td['speakers'] = []
        if talk.getElementsByTagName("persons") != None:
            for speaker in talk.getElementsByTagName("person"):
                if speaker.firstChild.nodeValue != "\n":   ## fugly hack
                    td['speakers'].append(speaker.firstChild.nodeValue)
        else:
            print("No speakers found for talk {placeholder}".format(placeholder=td['id']))
        return td
    else:
        print("Talk ID {placeholder} opted out of recording.".format(placeholder=talk.getAttribute("id")))
        return False

def gatherFilenames(td):
    print("Files for {title} by {speaker}, one per line. End with blank.".format(title=td['title'],speaker=", ".join(td['speakers'])))
    td['files'] = []
    while True:
        line = input()
        if line:
            td['files'].append(line)
        else:
            break
    return td

def gatherTimes(td):
    td['inpoint'] = input("start time in seconds:")
    td['outpoint'] = input("end time in seconds (total):")
    return td

def prepTalkDir(td): 
    # gen talk dir with symlinks to original media
    td['talkpath'] = os.path.join(mediadir, td['slug'])
    os.mkdir(td['talkpath'])
    i = 1
    for mediafile in td['files']: 
        os.symlink(mediafile, os.path.join(td['talkpath'], "{seq}.mov".format(seq=i)))
        i = i+1
    return td

def genTitleSlides(td):
    # Generate title slides as .png by means of search-and-replace
    tfile = open(titleslide, "r")
    tstr = tfile.read()
    if len(td['speakers']) >= 2:
        speakerstring = ", ".join(td['speakers'])
    else:
        speakerstring = td['speakers'][0]
    titlestring = td['title']
    tstr = tstr.replace("Speaker name speaker name", speakerstring)
    tstr = tstr.replace("This is a placeholder for the title text", titlestring)
    ftpath = os.path.join(td['talkpath'], "title.svg")
    ftfile = open(ftpath, "w")
    ftfile.write(tstr)
    ftfile.close()
    return td

def genMetaXML(td): 
    vmeta = vidmeta.video()
    smeta = vidmeta.speakersType()
    fmeta = vidmeta.sourcefilesType()
    vmeta.set_title(td['title'])
    vmeta.set_description(td['desc'])
    vmeta.set_slug(td['slug'])
    for s in td['speakers']:
        spkr = vidmeta.speakerType()
        spkr.set_speakerName(s)
        smeta.add_speaker(spkr)
    vmeta.set_speakers(smeta)
    for f in td['files']:
        ft = vidmeta.sourcefileType()
        ft.set_file(f)
        fmeta.add_sourcefile(ft)
    vmeta.set_sourcefiles(fmeta)
    vmeta.set_inpoint(int(td['inpoint']))
    vmeta.set_duration(int(td['outpoint']))
    vfile = open(os.path.join(td['talkpath'], "data.xml"), "w")
    vmeta.export(vfile, 0)
    vfile.close()

# Main loop
for event in sched.getElementsByTagName("event"):
    td = handleTalkDetails(event)
    if td != False: 
       td = gatherFilenames(td)
       td = gatherTimes(td)
       td = prepTalkDir(td)
       genTitleSlides(td)
       genMetaXML(td)
    else:
        print("Not handling talk")

