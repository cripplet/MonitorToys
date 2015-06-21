Monitor Toys
Aaron Goss
http://sourceforge.net/projects/monitortoys

Version: 1.0

This project is a collection of scripts to monitor various services and print output which may be
used by tools such as GeekTool and Conky for displaying information directly on the desktop.  Services
include weather information and music monitoring.

This project is delivered AS IS with no warranty or guarantee of functionality.  By using these scripts,
you are agreeing to the conditions specified in the included LICENSE.txt file, indemnifying the developer
of these scripts from any problems or issues which may accompany their use.

Simply put, I wrote these for fun and don't guarantee they can't be used to circumvent security on your
system or that they won't cause further problems.  If they work, great; if something goes wrong, I won't
be accountable for any damages incurred by their use.

Dependencies
------------
  You will need a Python interpeter (2.6+) installed on your system and included in your $PATH.  For more 
  information please see the Python website: <http://www.python.org/>

  - weather.py: 
    - You need an active network connection to gather statistics from "Yahoo! Weather".
    - This script contains a mapping between characters for output and weather codes from "Yahoo! Weather"
      These mappings are written for the Conky Forecast font set, but may be modified for any weather
      font set.  See the Modifying Monitor Toys section for more details.

  - monitor-music.py:
    - This script works with output from either iTunes or Pianobar.  For more information, please
      consult their websites: <http://www.apple.com/itunes/>; <https://github.com/PromyLOPh/pianobar>
    - MAC installations will also need the appscript library installed and accessible via their
      Python installation.  For more information, please see appscript's website: 
      <http://appscript.sourceforge.net/>

Installation
------------
These scripts require no installation other than extracting the tarball.  To integrate them with 
your tools (e.g. GeekTool or Conky), you should keep them in a centralized location and update
them from there.  Once extracted, you should make sure they are also executable:
     chmod 755 *.py

Fonts For weather.py Output
---------------------------
The weather.py script was built with a specific font set in mind.  I used conkyForecast icons
because they are fairly comprehensive in providing various icons for different conditions.  You
can adjust the script to work with any weather font, but since these are freely available, I
recommend using them.  When adding weather.py output to GeekTool or Conky, use whichever weather
font set you prefer.

For more information regarding modifying the weather.py script to use a different font set, see
Modifying Monitor Toys.


Receiving iTunes Info
---------------------
  - MAC:
    If you have iTunes installed and the appscript library also installed, monitor-music.py
    should work out of the box.  Simply start iTunes and run monitor-music with one of the
    basic switches:

    	  monitor-music.py -f
	      
    You should see information regarding the currently playing song.

Receiving Pianobar Info
-----------------------
  - MAC and Linux:
    Pianobar's content streams directly to the console -- this should be redirected to a 
    file on your system.  I aliasing the 'pianobar' command, tee-ing the output to a file.

    	 # Example alias found in ~/.bashrc
      	 alias pianobar='pianobar | tee ~/your_file_here.out'

    WARNING: this file has the potential to grow quickly; make sure you periodically clean
    	     it out, or remove it.  Though unlikely, unrestrained growth has the potential
	     of running you out of disk space.

    Once you have Pianobar directing its output to a file, invoke monitor-music.py with
    this filename.

	monitor-music.py -f -i ~/your_file_here.out

Integrating with Conky or GeekTool
----------------------------------
Once you have the scripts working with Pianobar, "Yahoo! Weather", and/or Pianobar, you
can use GeekTool or Conky to take the output from the various switches and print them
to the desktop.  For example, adding this command to GeekTool or Conky will print full
song information w/headers describing each outputted line:
    	     
    monitor-music.py -fv

Modifying Monitor Toys
----------------------
Since these scripts are provided free and open, please feel free to customize them according
to your system and/or environment.  If you choose to add/remove functionality, please don't
hesitate to contact me and let me know what you've done.

Here are the basic modifications I would recommend.

  - monitor-music.py
    The default file for monitoring Pianobar output is set to "~/tmp/pianobar.out".  You can
    either use the '--input-file/-i' parameter to explicitly direct the script to read from	
    a specific file, or modify the "INPUT_FILE" parameter in the file to point to whichever
    file you've chosen Pianobar to write.  This parameter is located in the upper 1/3 portion
    of monitor-music.py.

  - weather.py
    As of the first release, this script (in its original state) requires you to pass in your
    zip code with the '--zip-code/-z' parameter.  You can modify this script to set a default
    zip code using the "DEFAULT_ZIP" parameter which is set to "" by default.  Open the file
    in a text-editor and change "" to your zip code (e.g. "10001").  This will force the script
    to fetch weather for this location unless otherwise directed by the zip code parameter.

    You may also modify the default temperature unit requested for the weather.  This default
    setting is found in the "DEFAULT_UNIT" parameter.  Change this to "c" to recieve results
    in celsius.

    This script contains an extensive map for weather codes from "Yahoo! Weather", mapping them
    to characters which are printed.  For example, from a terminal, print the current icon for
    the weather

    	weather.py -i

    The resulting output should be a single character; this character corresponds to a character
    in the ConkyForecast font set.  If you desire a different font set, you will need to modify
    the mapping in this script.  To do this, open the weather.py script in a terminal and find
    the map:
    	
	WEATHER_ICONS = {0: "1", #tornado
		      	 1: "4", #tropical storm
			 ...

    Do NOT modify the numbers on the left-side of the ":" -- these correspond to the weather
    codes returned from "Yahoo! Weather"; instead, change the character in double-quotes to whichever
    will output the desired icon.

