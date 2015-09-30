#!/bin/bash
#
# This scripts helps convert e2guardian log generated files into
# squid format
# If no file is given has first parameter, default logfile will be used
# Returns name of converted file

# Get variables and source config file
WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\index.cgi//g)
WORKING_DIR=$(dirname $0)
cd $WORKING_DIR
#source $WORKING_DIR*config

[ ! "$1" = "" ] && {
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

# Converted logfile name includes "_convert2ls" before file extension
CONVERTEDLOGFILE="$LOGFILEPATH/$(basename $LOGFILENAME $LOGFILEEXT)_convert2ls$LOGFILEEXT"

# Read each line and convert it 
rm -Rf $CONVERTEDLOGFILE

# How many lines in original logfile
NBLINES=$(wc -l $LOGFILE | awk '{print $1}')
while read line
	do
	LINENUMBER=$((LINENUMBER+1))
	# What's logline type ?
	LOGLINETYPE=$(./command.cgi loglinetype $(echo $line | awk '{ printf "%s\n", $1 }' FPAT='([^,]+)|("[^"]+")'))
	# echoing percentage
	echo -ne "$LINENUMBER/$NBLINES : $(./command.cgi percent $NBLINES $LINENUMBER)\r"

	case "$LOGLINETYPE" in
		csv)
		# Exception to handle JSON parameters in URL
		JSON=`echo -ne $line | grep -o '{.*}'`
		[ ! "$JSON" = "" ] && {
			oldline=$line
			line=`echo -ne $oldline | sed 's/'$JSON'/##JSON##/g'`
		}
		# "TIME" field
		FIELD_01=`date -d "$(echo -ne $line | awk '{ printf "%s\n", $1 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g' | sed 's/\./-/g')" "+%s.000"`
#		FIELD_01=`date -d "$(echo $line | cut -d, -f1 | sed 's/\"//g' | sed 's/\./-/g')" "+%s.000"`
		# "DURATION" field, 6 chars long
		FIELD_02="\x20\x20\x20\x20\x20\x30" # hexdump value for "     0"
		# "CLIENT_ADDRESS" field
		FIELD_03=`echo -ne $line | awk '{ printf "%s\n", $3 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_03=`echo $line | cut -d, -f3 | sed 's/\"//g'`
		# "HITMISS" field
		FIELD_04=`echo -ne $line | awk '{ printf "%s\n", $11 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_04=`echo $line | cut -d, -f11 | sed 's/\"//g'`
		[ "$FIELD_04" = "403" ] && {
        		FIELD_04="TCP_DENIED/403";
			} || {
			FIELD_04="TCP_MISS/$FIELD_04"
		}
		# "SSIZE" field
		FIELD_05=`echo -ne $line | awk '{ printf "%s\n", $7 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_05=`echo $line | cut -d, -f7 | sed 's/\"//g'`
		# "HOW" field
		FIELD_06=`echo -ne $line | awk '{ printf "%s\n", $6 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_06=`echo $line | cut -d, -f6 | sed 's/\"//g'`
		# "WHERE" field
		FIELD_07=`echo -ne $line | awk '{ printf "%s\n", $4 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_07=`echo $line | cut -d, -f4 | sed 's/\"//g'`
		# "WHO" field
		FIELD_08=`echo -ne $line | awk '{ printf "%s\n", $2 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_08=`echo $line | cut -d, -f2 | sed 's/\"//g'`
		# "HIER" field
		FIELD_09="DEFAULT_PARENT/127.0.0.1"
		# "MIMETYPE" field
		FIELD_10=`echo -ne $line | awk '{ printf "%s\n", $12 }' FPAT='([^,]+)|("[^"]+")' | sed 's/\"//g'`
#		FIELD_10=`echo $line | cut -d, -f12 | sed 's/\"//g'`

		# Building line to include
		NEWLINE="$FIELD_01 $FIELD_02 $FIELD_03 $FIELD_04 $FIELD_05 $FIELD_06 $FIELD_07 $FIELD_08 $FIELD_09 $FIELD_10"
		[ ! "$JSON" = "" ] && NEWLINE=`sed 's/##JSON##/'$(./command.cgi sed_escape $JSON)'/g' <<< $NEWLINE`
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

