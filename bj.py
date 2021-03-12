#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import subprocess

# function definitions
def parse_bytes_output(bytes_string):
    if bytes_string.endswith("bytes"):
        bytes_string = bytes_string.replace("Gbytes"," * 1000000000")
        bytes_string = bytes_string.replace("Mbytes"," * 1000000")
        bytes_string = bytes_string.replace("Kbytes"," * 1000")
        bytes_string = eval(bytes_string)
    elif bytes_string.endswith(('G','M','K')):
        bytes_string = bytes_string.replace("G"," * 1000000000")
        bytes_string = bytes_string.replace("M"," * 1000000")
        bytes_string = bytes_string.replace("K"," * 1000")
        bytes_string = eval(bytes_string)
    return(int(bytes_string))

def reduce_units(stringOne, stringTwo):
    stringOne = str(stringOne)
    stringTwo = str(stringTwo)
    if (stringOne.endswith("0") and stringTwo.endswith("0")):
        stringOneLn = len(stringOne) - len(stringOne.rstrip('0'))
        stringTwoLn = len(stringTwo) - len(stringTwo.rstrip('0'))
        k_count = 0
        while stringOne.endswith('000'):
            stringOne = re.sub("000$", "", stringOne)
            k_count = k_count + 1
        stringOne = stringOne + ('k'*k_count)

        stringOne = stringOne.replace("kkk", "Gb")
        stringOne = stringOne.replace("kk", "Mb")
        stringOne = stringOne.replace("k", "Kb")

        stringTwo = stringTwo.replace("000", "k")
        stringTwo = stringTwo.replace("kkk", "Gb")
        stringTwo = stringTwo.replace("kk", "Mb")
        stringTwo = stringTwo.replace("k", "Kb")

        stringOne = re.sub(r"([0-9]+)([0-9]{3})([G|M|K]b)","\g<1>.\g<2>\g<3>", stringOne)
        if '.' in stringOne:
            stringOne = re.sub(r"0*?Gb$","Tb", stringOne)
            stringOne = re.sub(r"0*?Mb$","Gb", stringOne)
            stringOne = re.sub(r"0*?Kb$","Mb", stringOne)

        stringTwo = re.sub(r"([0-9]+)([0-9]{3})([G|M|K]b)","\g<1>.\g<2>\g<3>", stringTwo)
        if '.' in stringTwo:
            stringTwo = re.sub(r"0*?Gb$","Tb", stringTwo)
            stringTwo = re.sub(r"0*?Mb$","Gb", stringTwo)
            stringTwo = re.sub(r"0*?Kb$","Mb", stringTwo)

        fractionString = "{}/{}".format(stringOne, stringTwo)
    return(fractionString)


bjobs_json = subprocess.check_output(['bjobs', '-a', '-json', '-o', 'jobid stat queue kill_reason dependency exit_reason time_left %complete run_time max_mem memlimit nthreads hrusage exit_code'])
bjobs_json = bjobs_json.decode(sys.stdout.encoding)
bjobs_json = json.loads(bjobs_json)

# parase information to display
jobsrunning = bjobs_json['JOBS']

pend_count = 0
run_count = 0
exit_count = 0

header = "\x1b[38;5;3m" + "JOB ID\tSTATUS\tQUEUE\t\tRAM USAGE\tTIMELIMIT"
print(header)
for listnb in range(1,len(bjobs_json['RECORDS'])):
    jobid = bjobs_json['RECORDS'][listnb]['JOBID']
    stats = bjobs_json['RECORDS'][listnb]['STAT']
    if stats == "PEND":
        pend_count = pend_count + 1
        continue
    queue = bjobs_json['RECORDS'][listnb]['QUEUE']
    time_left = bjobs_json['RECORDS'][listnb]['TIME_LEFT']
    completed = bjobs_json['RECORDS'][listnb]['%COMPLETE'].replace(" L","")


    # generate result line to display with color based on status
    if stats == "DONE":
        # $(tput setaf 28)
        line_output = "\x1b[38;5;28m" + "{}\t{}\t{}".format(jobid, stats, queue)
    elif stats == "RUN":
        # $(tput setaf 248)
        line_output = "\x1b[38;5;248m" + "{}\t{}\t{}".format(jobid, stats, queue)
        run_count = run_count + 1
    elif stats == "EXIT":
        # $(tput setaf 197)
        line_output = "\x1b[38;5;197m" + "{}\t{}\t{}".format(jobid, stats, queue)
        exit_count = exit_count + 1
    else:
        line_output = "{}\t{}\t{}".format(jobid, stats, queue)


    # Extra columns to display if there is information
    max_mem = bjobs_json['RECORDS'][listnb]['MAX_MEM']
    memlimit = bjobs_json['RECORDS'][listnb]['MEMLIMIT']
    if max_mem != "":
            max_mem = parse_bytes_output(max_mem)
            memlimit = parse_bytes_output(memlimit)
            memusage = reduce_units(max_mem, memlimit)
            memusage = reduce_units(max_mem, memlimit)
            line_output+= "\t{}".format(memusage)


    exit_code = bjobs_json['RECORDS'][listnb]['EXIT_CODE']
    if exit_code != None and exit_code != "":
        exit_reason = bjobs_json['RECORDS'][listnb]['EXIT_REASON']
        line_output+= "\t{}\t{}".format(exit_code, exit_reason)

    # format time_left
    line_output+= "\t{}".format(completed)
    line_output+= "\x1b[0m"
    print(line_output)


print("{} still pending, {} running, {} exited".format(pend_count, run_count, exit_count))
