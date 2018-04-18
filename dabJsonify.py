#! /usr/bin/python

import os
import json
import math
import argparse

def is_nan(x):
	return isinstance(x, float) and math.isnan(x)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jsonify dabCollect.py RAW file')
    parser.add_argument('-i', '--input', help='Input file', required=True)
    parser.add_argument('-o', '--output', help='Output file', required=True)
    cli_args = parser.parse_args()

    print "Processing %s file to %s" % (cli_args.input, cli_args.output)
    markers = []
    with open(cli_args.input, 'r') as infile:
        for line in infile:
            j_content = json.loads(line)
            
            valid = True
            for attribute, value in j_content.iteritems():
                #print "%s - |%s|"  % (attribute, value)
                if is_nan(value):
                    valid = False
                    print 'Can not process record : %s' % (j_content)
            if valid:
                markers.append(j_content)
        
    with open(cli_args.output, 'w') as outfile:
        json.dump(markers, outfile, allow_nan=False)

    print "Done."
