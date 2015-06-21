#!/usr/bin/env python
"""
monitor-music.py
Copyright 2011 Aaron Goss

This file is part of Monitor Toys.

Monitor Toys is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Monitor Toys is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Monitor Toys.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys, os, optparse, re, subprocess

from time      import gmtime, strftime
from appscript import *

INPUT_FILE      = "~/tmp/pianobar.out" # Modify to change the default file location
DEFAULT_MSG     = "Music: not playing"
SECONDS_IN_HOUR = 3600
MAX_CHAR_LENGTH = 50

HEADERS = ["Now Playing",
           "Artist",
           "Album",
           "Time Remaining"]

def main(argv):
    parser = optparse.OptionParser()

    parser.add_option("-a", "--album", action="store_true", dest="album", default=False,
                      help="Print most recent album played")
    parser.add_option("-f", "--full-song-info", action="store_true", dest="fullInfo", default=False,
                      help="Print the full song-information w/out tokenizing it")
    parser.add_option("-i", "--input-file", dest="file", default=INPUT_FILE,
                      help="File pianobar output is being directed to (i.e. file to monitor")
    parser.add_option("-n", "--station", action="store_true", dest="station", default=False,
                      help="Print most recent station selected")
    parser.add_option("-r", "--artist", action="store_true", dest="artist", default=False,
                      help="Print most recent artist played")
    parser.add_option("-s", "--song-title", action="store_true", dest="song", default=False,
                      help="Print most recent song title being played")
    parser.add_option("-t", "--time", action="store_true", dest="time", default=False,
                      help="Print most recent time remaining information")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print all output with header information (e.g. 'Now Playing: XXXXX')")
    (opts, args) = parser.parse_args(argv)

    monitor = ITunesMonitor(opts)
    
    # Try iTunes first, then try Pianobar
    if not monitor.test():
        monitor = PianobarMonitor(opts)
        if not monitor.test():
            return 1
    try:
        if opts.fullInfo:
            songInfo = monitor.getAllSongInfo()
            if opts.verbose:
                for i in xrange(len(songInfo)):
                    print("%s: %s" % (HEADERS[i], songInfo[i]))
            else:
                for snippet in songInfo:
                    print(snippet)
            return 0
        
        if opts.station:
            station = monitor.getStation()
            if opts.verbose:
                print("Station: %s" % station)
            else:
                print(station)
                
        if opts.song:
            songTitle = monitor.getSongTitle()
            if opts.verbose:
                print("%s: %s" % (HEADERS[0], songTitle))
            else:
                print(songTitle)
                
        if opts.artist:
            songArtist = monitor.getSongArtist()
            if opts.verbose:
                print("%s: %s" % (HEADERS[1], songArtist))
            else:
                print(songArtist)
                
        if opts.album:
            songAlbum = monitor.getSongAlbum()
            if opts.verbose:
                print("%s: %s" % (HEADERS[2], songAlbum))
            else:
                print(songAlbum)
            
        if opts.time:
            timeRemaining = monitor.getSongRemainingTime()
            if opts.verbose:
                print("%s: %s" % (HEADERS[3], timeRemaining))
            else:
                print(timeRemaining)
                    
    except IOError:
        print(DEFAULT_MSG)
        return 1
            
    return 0

class PianobarMonitor():
    """
    PianobarMonitor()
    
    This class is concerned with monitoring Pianobar output.  This output should be piped to a file
    which is read in by this class and parsed for its content.
    """
    def __init__(self, opts):
        self.opts = opts
    
    def test(self):
        # Run 'fuser' against the pianobar file to see if a process is attached to it
        p = subprocess.Popen(["fuser", self.opts.file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.communicate()[0]
    
        return result not in (None, "")
    
    def getStation(self):
        p = subprocess.Popen(["grep", "Station", self.opts.file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result  = p.communicate()[0]
        station = result.split("\r")[-1]
        
        if "Station" in station:
            #Strip out unnecessary contents and whitespce chars
            station = station.replace("|>", "")
            station = re.sub("\(.*\)", "", station)
            station = station.strip()
            station = station.rstrip()
            return truncateContent(station)
        else:
            return ""
    
    def getAllSongInfo(self):
        return [self.getSongTitle(),
                self.getSongArtist(),
                self.getSongAlbum(),
                self.getSongRemainingTime()]

    def getSongTitle(self):
        title = self.parseSongInfo()
    
        if title is not None:
            return truncateContent(title.split("by")[0])
        else:
            return ""
    
    def getSongArtist(self):
        artist = self.parseSongInfo()
        
        if artist is not None:
            return truncateContent(artist.split("\"")[3])
        else:
            return ""
    
    def getSongAlbum(self):
        album = self.parseSongInfo()
        if album is not None:
            return truncateContent(album.split("\"")[5])
        else:
            return ""
    
    def getSongRemainingTime(self):
        time = ""
        try:
            with open(self.opts.file, 'ra') as fileH:
                #Read in the last 12 bytes of the file -- time info
                #is 12 bytes long; make sure the pointer is reset when
                #the file is closed 
                fileH.seek(-12, 2)
                time = fileH.read(12).rstrip()
                fileH.close()
        except Exception:
            time = ""
        
        return time
        
    def parseSongInfo(self):
        try:
            p = subprocess.Popen(["grep", "|>", self.opts.file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = p.communicate()[0]
            output = result.split("\r")[-1].split("\n")[-2].replace("|>", "")
            output = re.sub("^\s*", "", output)
            
            # Return None if the output doesn't contain "by"
            return output if "by" in output else None
    
        except Exception:
            return None
    
class ITunesMonitor():
    """
    ITunesMonitor()
    
    This class is used to monitor the output from iTunes, using the appscript
    bindings library.  This library allows this class to directly access the
    applications running on OSX, and request information from the running
    instances.
    """
    def __init__(self, opts):
        self.opts   = opts
        self.itunes = app("itunes")
    
    def test(self):
        #Check isrunning -- other operations which actually _open_ itunes
        if self.itunes.isrunning():
            return self.itunes.player_state() in (k.playing, k.paused)
        return False
    
    def getAllSongInfo(self):
        return [self.getSongTitle(),
                self.getSongArtist(),
                self.getSongAlbum(),
                self.getSongRemainingTime()]
    
    def getStation(self):
        return ""
    
    def getSongTitle(self):
        track = self.itunes.current_track()
        return truncateContent(track.name())
    
    def getSongArtist(self):
        track = self.itunes.current_track()
        return truncateContent(track.artist())
    
    def getSongAlbum(self):
        track = self.itunes.current_track()
        return truncateContent(track.album())

    def getSongRemainingTime(self):
        track      = self.itunes.current_track()
        playerTime = self.itunes.player_position()
        
        formatStr  = "%M:%S" if playerTime <= SECONDS_IN_HOUR else "%H:%M:%S"

        playerTime = strftime(formatStr, gmtime(playerTime))
        playerTime = '/'.join([playerTime, str(track.time())])

        return playerTime

def truncateContent(content):
    if len(content) > MAX_CHAR_LENGTH:
        return "%s ..." % content[:MAX_CHAR_LENGTH]
    else:
        return content

if __name__ == '__main__':
    sys.exit(main(sys.argv))
