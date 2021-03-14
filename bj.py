#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import re
import os
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


screen = curses.initscr()
screen.nodelay(1)

# Update the buffer, adding text at different locations
curses.curs_set(0)
curses.noecho()
curses.start_color()
curses.use_default_colors()
screen.keypad(1)
curses.mousemask(1)


# curses.init_pair(1,-1,curses.COLOR_BLUE) # blue bg
curses.init_pair(1,245,-1) # blue bg
curses.init_pair(2,curses.COLOR_YELLOW,-1) # yellow
curses.init_pair(3,197,-1) # Red
curses.init_pair(4,248,-1) # Grey
curses.init_pair(5,28,-1) # Green
screen_refresh_it = 0
email_scheduled = False

while True:
    screen_refresh_it = screen_refresh_it + 1
    bjobs_json = subprocess.check_output(['bjobs', '-a', '-json', '-o', 'jobid stat queue kill_reason dependency exit_reason time_left %complete run_time max_mem memlimit nthreads hrusage exit_code'])
    bjobs_json = bjobs_json.decode(sys.stdout.encoding)
    bjobs_json = json.loads(bjobs_json)

    # parse information to display
    jobsrunning = bjobs_json['JOBS']

    pend_count = 0
    run_count = 0
    exit_count = 0
    done_count = 0

    height,width = screen.getmaxyx()
    stopHeight = int(height)-2


    # screen.addstr(0, 0, "MENU GOES HERE : {}".format(screen_refresh_it),curses.color_pair(1))
    header = "JOB ID\tSTATUS\tQUEUE\t\tRAM USAGE\tTIMELIMIT"
    screen.addstr(0, 0, header,curses.color_pair(2))

    i = 1
    jobid_set = set()
    for listnb in range(1,len(bjobs_json['RECORDS'])):
        jobid = bjobs_json['RECORDS'][listnb]['JOBID']
        jobid_set.add(jobid)
        stats = bjobs_json['RECORDS'][listnb]['STAT']
        if stats == "PEND":
            pend_count = pend_count + 1
            continue
        queue = bjobs_json['RECORDS'][listnb]['QUEUE']
        time_left = bjobs_json['RECORDS'][listnb]['TIME_LEFT']
        completed = bjobs_json['RECORDS'][listnb]['%COMPLETE'].replace(" L","")


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
        else:
            line_output+= "\t\t\t"


        exit_reason = bjobs_json['RECORDS'][listnb]['EXIT_REASON']
        if exit_reason != None and exit_reason != "":
            line_output+= "\t{}".format(exit_reason)

        # format time_left
        if stats == "RUN":
            line_output+= "\t{}".format(completed)

        if stats == "DONE":
            done_count = done_count + 1
        elif stats == "RUN":
            run_count = run_count + 1
        elif stats == "EXIT":
            exit_count = exit_count + 1

        # generate result line to display with color based on status
        if i < stopHeight-1:
            if stats == "DONE":
                # $(tput setaf 28)
                screen.addstr(i, 1, line_output, curses.color_pair(5))
            elif stats == "RUN":
                # $(tput setaf 248)
                screen.addstr(i, 1, line_output, curses.color_pair(4))
            elif stats == "EXIT":
                # $(tput setaf 197)
                screen.addstr(i, 1, line_output, curses.color_pair(3))
            else:
                screen.addstr(i, 1, line_output)
            i = i + 1


    status = "{} still pending, {} running, {} exited".format(pend_count, run_count, exit_count)
    screen.addstr(stopHeight, 1, status)

    if email_scheduled is True:
        screen.addstr(stopHeight+1, 0, "Exit [q] | " ,curses.color_pair(1))
        screen.addstr(stopHeight+1, 11, "Email Scheduled", curses.color_pair(5))
        screen.addstr(stopHeight+1, 26, " | Killall [k]", curses.color_pair(1))
    else:
        screen.addstr(stopHeight+1, 0, "Exit [q] | Email [e] | Killall [k]" ,curses.color_pair(1))

    screen.refresh()
    screen.timeout(5000)


    ch = screen.getch()
    if ch == ord('q'): break
    if ch == curses.KEY_MOUSE:
        _, mx, my, _, _ = curses.getmouse()
        y, x = screen.getyx()
        screen.addstr(0, 0, "{} : {}".format(my, mx))
    if ch  == ord('e'):
        email_scheduled = True
        bwait_cmd = ') && ended('.join(jobid_set)
        bwait_cmd = 'ended(' + bwait_cmd + ')'
        bwait_cmd = "bwait -w '" + bwait_cmd + "'"
        os.system("{} && printf '\n\nThis is an automated email from better-bjobs on ending of all jobs' | mail -s '[BBJ] Farm Jobs Ended' $USER@sanger.ac.uk & \n echo $! > $HOME/.better-bjobs.bgtasks.txt".format(bwait_cmd))


curses.endwin()
