#!/bin/sh
#
# This scripts helps convert e2guardian log generated files into
# squid format
# If no file is given has first parameter, default logfile will be used
# Returns name of converted file

# Get variables and source config file
#WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\index.cgi//g)
#source $WORKING_DIR*config

[ ! "$1" == "" ] && {
LOGFILE="$1"
} || {
# Catch logfile info
LOGFILE="$(./command.cgi e2config loglocation)"
}
# What is logfile path ?
LOGFILEPATH="$(dirname $LOGFILE)"

# What is logfile name ?
LOGFILENAME=$(basename $LOGFILE)

#What is logfile suffix ?
LOGFILEEXT=$(./command.cgi fileext $LOGFILENAME)

# Converted logfile name includes "_C2LS" before file extension
CONVERTEDLOGFILE="$LOGFILEPATH/$(basename $LOGFILENAME $LOGFILEEXT)_C2LS$LOGFILEEXT"

# Read each line and convert it 
rm -Rf $CONVERTEDLOGFILE

# How many lines in original logfile
NBLINES=$(wc -l $LOGFILE | awk '{print $1}')
while read line
	do
	LINENUMBER=$((LINENUMBER+1))
	# What's logline type ?
	LOGLINETYPE=$(./command.cgi loglinetype $(echo $line | cut -d" " -f1))
	PERCENT=$(./command.cgi percent $NBLINES $LINENUMBER)
	echo -ne "$PERCENT\r"
	case "$LOGLINETYPE" in
		csv)
		# "TIME" field
		FIELD_01=`date -d "$(echo $line | cut -d, -f1 | sed 's/\"//g' | sed 's/\./-/g')" "+%s.000"`
		# "DURATION" field, 6 chars long
		FIELD_02="     0"
		# "CLIENT_ADDRESS" field
		FIELD_03=`echo $line | cut -d, -f3 | sed 's/\"//g'`
		# "HITMISS" field
		FIELD_04=`echo $line | cut -d, -f11 | sed 's/\"//g'`
		[ "$FIELD_04" = "403" ] && {
        		FIELD_04="TCP_DENIED/403";
			} || {
			FIELD_04="TCP_MISS/$FIELD_04"
		}
		# "SSIZE" field
		FIELD_05=`echo $line | cut -d, -f7 | sed 's/\"//g'`
		# "HOW" field
		FIELD_06=`echo $line | cut -d, -f6 | sed 's/\"//g'`
		# "WHERE" field
		FIELD_07=`echo $line | cut -d, -f4 | sed 's/\"//g'`
		# "WHO" field
		FIELD_08=`echo $line | cut -d, -f2 | sed 's/\"//g'`
		# "HIER" field
		FIELD_09="DEFAULT_PARENT/127.0.0.1"
		# "MIMETYPE" field
		FIELD_10=`echo $line | cut -d, -f12 | sed 's/\"//g'`

		# Building line to include
		NEWLINE="$FIELD_01 $FIELD_02 $FIELD_03 $FIELD_04 $FIELD_05 $FIELD_06 $FIELD_07 $FIELD_08 $FIELD_09 $FIELD_10"
		;;
		squid)
		NEWLINE="$line"		
		;;
		*)
		echo "$LOGLINETYPE = not known - keep it"
		NEWLINE="$line"
		;;
	esac	
	echo -ne "$NEWLINE\n" >> $CONVERTEDLOGFILE
	shift;
done < $LOGFILE

# Returns name of the file
echo "$CONVERTEDLOGFILE"

