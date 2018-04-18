#! /usr/bin/python

# need debian package :
# python-gps gpsd gpsd-clients

import sys
import os
from gps import *
from time import *
import time
import threading
import json
import argparse
from datetime import datetime

from keystone.radio import Radio
import keystone.constants as constants

gpsd = None #setting the global variable

class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            #this will continue to loop and grab EACH set of gpsd info to clear the buffer
            gpsd.next()

if __name__ == '__main__':
    # Get configuration file in argument
    parser = argparse.ArgumentParser(description='Collect DAB signal and GPS informations')
    parser.add_argument('-l', '--services_list', action='store_true', help='Reset services database and search services from 5A to 13F', required=False)
    parser.add_argument('-q', '--quiet', action='store_true', help='Limit output verbosity', required=False)
    parser.add_argument('-t', '--time_sleep', default='2', type=int, help='Time (in sec.) to sleep between 2 query (default 2)', required=False)
    parser.add_argument('-s', '--service', type=int, help='Select service to monitor', required=False)
    parser.add_argument('-o', '--output', help='Output directory', required=False)
    cli_args = parser.parse_args()

    if cli_args.services_list == True:
        with Radio("/dev/ttyACM0", mode=constants.DAB) as r:
            # Reset database
            print "Reset services database"
            r.reset
            
            # Search from 5A to 13F (See annexe A)
            print "Searching services from 5A to 13F..."
            r.dab_auto_search(start_index=0, end_index=40, clear=False)
            
            # Display service list
            print "-- SERVICES LIST --"
            i=0
            for p in r.programs:
                try:
                    p_name = p.name
                except:
                    p_name = 'unknown'
                    
                try:
                    p_eid = hex(p.info.ensemble_id)
                except:
                    p_eid = 'unknown'
                    
                try:
                    p_sid = hex(p.info.service_id)
                except:
                    p_sid = 'unknown'
                    
                try:
                    p_type = p.type
                except:
                    p_type = 'unknown'
                    
                try:
                    p_atype = p.application_type
                except:
                    p_atype = 'unknown'
                
                print "%s = name: %s (eid: %s, sid: %s), type: %s, application_type: %s" % (i, p_name, p_eid, p_sid, p_type, p_atype)
                #try:
                    #print "%s = name: %s (eid: %s, sid: %s), type: %s, application_type: %s" % (i, p.name, hex(p.info.ensemble_id), hex(p.info.service_id), p.type, p.application_type)
                #except:
                    #print "%s = name: unknown" % (i)
                i+=1

    else:
        if cli_args.service:
            print "Loading ..."
            if cli_args.output:
                frow = "%s/data_%s.raw" % ( cli_args.output, datetime.now().strftime('%Y%m%d_%H%M%S') )
                #frow = cli_args.output . '/data_'.datetime.now().strftime('%Y%m%d_%H%M%S').'.raw'
                print "Writing RAW data to %s" % (frow)
            try:
                with Radio("/dev/ttyACM0", mode=constants.DAB) as r:
                    if cli_args.service <= len(r.programs):
                        program = r.programs[cli_args.service]
                    else:
                        print "ERROR: Service %s can not be selected. (Use --services_list to list all services)" % cli_args.service
                        sys.exit(1)
                    
                    # Set the volume to 10 (Max is 16)
                    r.volume = 10
                    
                    # Request stereo sound
                    r.stereo = True
                    
                    # Play the selected program
                    program.play()
                    
                    # Waiting tunning
                    while r.status != 0:
                        #print 'wait ...'
                        time.sleep(0.5)
                    
                    print "PLAYING : %s" % program.name
                    print "Ensemble ID        : %s" % hex(program.info.ensemble_id)
                    print "Ensemble name      : %s" % r.ensemble_name(cli_args.service, 'DAB')
                    print "Service ID         : %s" % hex(program.info.service_id)
                    print "Data rate          : %skbps" % r.data_rate
                    print "-------------------------------------"
                    gpsp = GpsPoller()
                    try:
                        gpsp.start()
                        if cli_args.quiet == False:
                            print "                     utc         latitude        longitude         altitude            speed            climb  signal strength   signal quality"
                        while True:
                            if (gpsd.fix.mode == 3):
                                if cli_args.quiet == False:
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.utc, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.fix.latitude, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.fix.longitude, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.fix.altitude, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.fix.speed, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=gpsd.fix.climb, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=r.signal_strength.strength, fill=' ', align='>', width=16),
                                    print '{message:{fill}{align}{width}}'.format(message=r.dab_signal_quality, fill=' ', align='>', width=16)
                                
                                marker = {
                                    'utc' : gpsd.utc,
                                    'latitude' : gpsd.fix.latitude,
                                    'longitude' : gpsd.fix.longitude,
                                    'altitude' : gpsd.fix.altitude,
                                    'speed' : gpsd.fix.speed,
                                    'clim' : gpsd.fix.climb,
                                    'signal_strength' : r.signal_strength.strength,
                                    'signal_quality' : r.dab_signal_quality
                                    }
                                
                                # Write marker into file (a json line by line)
                                if cli_args.output:
                                    with open(frow, 'a') as outfile:
                                        json.dump(marker, outfile)
                                        outfile.write('\n')
                            else:
                                if cli_args.quiet == False:
                                    print 'Waiting NMEA mode 3D'
                            time.sleep(float(cli_args.time_sleep))

                    except (KeyboardInterrupt, SystemExit):
                        print "\nKilling Thread..."
                        gpsp.running = False
                        # wait for the thread to finish what it's doing
                        gpsp.join()
                        print "Done."
            except:
                sys.exit(1)
        else:
            parser.print_help()
            print "ERROR: You need to specify service to monitor. (Use --services_list to list all services)"
            sys.exit(1)
    
    print "Exiting."
