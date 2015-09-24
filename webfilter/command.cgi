#!/bin/sh
#
# Various hard coded commands to switch fonctionalities and retrieve values

[ "$1" = "" ] && exit 1
ACTION="$1"

# Get variables and source config file
WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\index.cgi//g)
source $WORKING_DIR*config

case "$ACTION" in
	e2config)
		# returns E2Guardian config file path if $2 is not set
		# returns E2Guardian config file value if $2 is set
		E2GCONFIG="$E2G_CONFDIR/e2guardian.conf"
		[ "$2" == "" ] && {
			echo "$E2GCONFIG"
		} || {
			echo "$(grep -i -e "$2 = " $E2GCONFIG | awk -F= '{print $2}' |  sed "s/ //g")"
		}
	;;
	e2fconfig)
		# returns E2Guardian group config file path
		# group 1 is default if $2 is not set
		GROUPNUM="$2"
		[ "$2" = "" ] && GROUPNUM="1"
		echo "$E2G_CONFDIR/e2guardianf$GROUPNUM.conf"
	;;
	loglinetype)
		# returns detected e2guardian's logtype dependending of first field given
		# takes the value of the "first field" as a parameter
		[ "$2" = "" ] && exit 1
		# Seems to be a timestamp line = squid
		[ ! "$(echo $2 | grep -Eo '^[0-9]{10}[.][0-9]{3}')" = "" ] && { echo "squid" ; exit 0 ; }
		# Seems to be a e2guardian csv
		[ ! "$(echo $2 | grep -Eo '^\"[0-9]{4}[.][0-9]{1,2}[.][0-9]{1,2}')" = "" ] && { echo "csv" ; exit 0 ; }
	;;
	sablier)
		# returns a char to display work in progress
		# takes number of lines as parameter $2
		# takes current line number as parameter $3
		PERCENT=`expr $3 \* 100 / $2`
		[ "$PERCENT" -le "9" ] && PERCENT="0$PERCENT"
		echo "$PERCENT%"
	;;
	*)
		echo "Unknown command"
	;;
esac

