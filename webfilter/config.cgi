#!/bin/bash
#
# Configuration file for e2guardian webGUI
# This config file will be called with "source"

# Set DEBUG to "1"
DEBUG="0"
#
[ "$DEBUG" = "1" ] && { 
	INPUTTYPE="text" ;
	} || {
	INPUTTYPE="hidden" ;	
}

# Do we use uci (for example, openWRT) ?
which uci > /dev/null
[ "$?" = 0 ] && { UCI=1 ;} || { UCI=0 ;}
# Uncomment below to disable use of uci, otherwise it is autoconfigurated
#UCI=1

# Where are stored backup files ?
BACKUP="/mnt/share/e2guardian/backup"
# Create backup directory
mkdir -p $BACKUP

# Where are stored e2guardian configuration files ?
E2G_CONFDIR="/etc/e2guardian"


