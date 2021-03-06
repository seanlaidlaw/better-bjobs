# better-bjobs
a curses based wrapper script for LSF BJOBS command to improve on design and increase usefulness

## Why ?

Standard bjobs output is not interactive, is not color highlighted, and is not information dense.
better-bjobs aims to provide a wrapper to extract the useful information from bjobs and discard the rest.

The best way to understand this is to compare the outputs of both:

### Standard Bjobs Output
![STDOUT of normal LSF Bjobs command](img/bjobs_output.svg)


### Better-Bjobs Output
![STDOUT of better-bjobs output](img/bj_output.svg)


## Installation

To install better-bjobs you simply need to download the python script bj.py and place it in your
PATH.
For ease of use I reccomend adding an alias to run the script.

```
mkdir -p $HOME/.local/bin  # create bin folder in home if not exists
curl -L https://raw.githubusercontent.com/seanlaidlaw/better-bjobs/master/bj.py --output $HOME/.local/bin/bj.py
echo "alias bj='python $HOME/.local/bin/bj.py'" >> $HOME/.bashrc
```

## Usage

Unlike the standard bjobs command better-bjobs as an interactive terminal user interface, supports multiple options for managing all currently running jobs.
### Enabling Email Notifications
By pressing the 'e' key, a scheduled email will be submitted once all job ids have finished running (regardless of exit status).

![interface of better-bjobs with email option](img/not_scheduled.svg)

Enabling this option will turn the button green

![interface of better-bjobs with activated email option](img/scheduled.svg)
