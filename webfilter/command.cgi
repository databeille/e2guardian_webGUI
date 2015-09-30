#!/bin/sh
#
# Various hard coded commands to switch fonctionalities and retrieve values
PWD="$PWD"

[ "$1" = "" ] && exit 1
ACTION="$1"

# Get variables and source config file
#WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\command.cgi//g)
[ "$WORKING_DIR" = "" ] && WORKING_DIR="$(dirname $0)"
CONFIG="config"
cd $WORKING_DIR
. $CONFIG

make_ip_user () {
	# OPENWRT: Create realname.cfg file to be used by LightSquid
	REALNAME_FILE="$(dirname $(./command.cgi lsconf))/realname.cfg"
	a=0
	while [ $a -ge 0 ]
	do
		REALNAME_NAME=$(uci get dhcp.@host[$a].name)
		REALNAME_IP=$(uci get dhcp.@host[$a].ip)
	        sed -i "/^$/d" $REALNAME_FILE
	        sed -i "/"$REALNAME_IP"/d" $REALNAME_FILE
		echo -ne "$REALNAME_IP\x09$REALNAME_NAME\n" >> $REALNAME_FILE
		a=`expr $a + 1`
		[ ! "$(uci -q get dhcp.@host[$a])" = "host" ] && break
	done
}

sed_escape () {
	# Helps escape string to comply with sed rewriting
	shift
	DATA=$*
	# Escaping "\"
	DATA=$(echo $DATA | sed 's~\\~\\\\~g')
	# Escaping "/"
	DATA=$(echo $DATA | sed 's~\/~\\\/~g')
	# Escaping "$"
	DATA=$(echo $DATA | sed 's~\$~\\\$~g')
	# Escaping "."
	DATA=$(echo $DATA | sed 's~\.~\\\.~g')
	# Escaping "*"
	DATA=$(echo $DATA | sed 's~\*~\\\*~g')
	# Escaping "["
	DATA=$(echo $DATA | sed 's~\[~\\\[~g')
	# Escaping "]"
	DATA=$(echo $DATA | sed 's~\]~\\\]~g')
	# Escaping "^"
	DATA=$(echo $DATA | sed 's~\^~\\\^~g')
	# Escaping "&"
	DATA=$(echo $DATA | sed 's~\&~\\\&~g')
	echo -ne $DATA
}

case "$ACTION" in
	fixlogformat)
		# Check log format allows us to generate stats
		# Fix log format and logfile
		# Stores and compresses old missformated logfile
 		# Takes file to fix as first parameter, default logfile otherwise
		#[ ! "$(./command.cgi e2config logfileformat)" = "3" ] && {
			/etc/init.d/e2guardian stop
			uci set e2guardian.e2guardian.logfileformat=3
			uci commit
			cd /www/cgi-bin/webfilter
			DEFAULTLOG="$(./command.cgi e2config loglocation)"
			LOGLOCATION="$DEFAULTLOG"
			[ ! "$2" = "" ] && LOGLOCATION="$2"
			LOGROTATED="$(./command.cgi logrotate $LOGLOCATION nozip)"
			/etc/init.d/e2guardian start
			CONVERTEDLOG=$(./convertlog.cgi $LOGROTATED)
			LOGLOCATIONEXT="$(./command.cgi fileext $LOGROTATED)"
			cp -f $LOGLOCATION $LOGLOCATION.$(date "+%Y%m%d%H%M")
			chown nobody:nogroup $LOGLOCATION.$(date "+%Y%m%d%H%M")
			gzip $LOGLOCATION.$(date "+%Y%m%d%H%M")
			cp -f $CONVERTEDLOG $LOGLOCATION
			chown nobody:nogroup $LOGLOCATION
			rm -f $CONVERTEDLOG
			[ "$LOGLOCATION" = "$DEFAULTLOG" ] && {
				/etc/init.d/e2guardian stop
				cat $DEFAULTLOG >> $LOGLOCATION
				rm -Rf $DEFAULTLOG
				mv $LOGLOCATION $DEFAULTLOG
				/etc/init.d/e2guardian start
			}
		#}
	;;
	e2config)
		# returns E2Guardian config file path if $2 is not set
		# returns E2Guardian config file value if $2 is set
		E2GCONFIG="$E2G_CONFDIR/e2guardian.conf"
		[ "$2" = "" ] && {
			echo "$E2GCONFIG"
		} || {
			echo "$(grep -i -e "$2 = " $E2GCONFIG | \
			awk -F= '{print $2}' |  sed "s/[' ]//g")"
		}
	;;
	e2fconfig)
		# returns E2Guardian group config file path
		# group 1 is default if $2 is not set
		GROUPNUM="$2"
		[ "$2" = "" ] && GROUPNUM="1"
		echo "$E2G_CONFDIR/e2guardianf$GROUPNUM.conf"
	;;
	fileext)
		# returns file extension of the filename given
		y=${2%.*}
		echo $(basename $2) | sed 's@'${y##*/}'@@'
	;;
	lsconf)
		# returns LightSquid config file path if $2 is not set
		# returns LightSquid config file value if $2 is set
		LSCONFIG="$LS_CONFDIR/lightsquid.cfg"
		[ "$2" = "" ] && {
			echo "$LSCONFIG"
		} || {
			echo "$(grep -i -e "\$$2.*=" $LSCONFIG | \
			awk -F= '{print $2}' |  sed "s/[\"; ]//g")"
		}
	;;
	loglinetype)
		# returns detected e2guardian's logtype dependending of first field given
		# takes the value of the "first field" as a parameter
		[ "$2" = "" ] && exit 1
		shift
		# Seems to be a timestamp line = squid
		[ ! "$(echo $* | grep -Eo '^[0-9]{10}[.][0-9]{3}')" = "" ] \
		&& { echo "squid" ; exit 0 ; }
		# Seems to be a e2guardian csv
		[ ! "$(echo $* | grep -Eo '^\"[0-9]{4}[.][0-9]{1,2}[.][0-9]{1,2}')" = "" ] \
		&& { echo "csv" ; exit 0 ; }
		# Seems to be a dansguardian logfile
		[ ! "$(echo $* | grep -Eo '^[0-9]{4}[.][0-9]{1,2}[.][0-9]{1,2}')" = "" ] \
		&& { echo "dansguardian" ; exit 0 ; }
	;;
	logrotate)
		# Rotate and compress last current log
		# Includes time of action into filename
		# Provides a new empty logfile and restart e2guardian
		# Returns name of rotated logfile
		# Takes file to rotate as first parameter, default logfile otherwise
		# If second parameter is set to "nozip", file will not be gzipped 
		[ "$3" = "nozip" ] && { GZIP="" ; } || { GZIP=".gz"; }
		[ ! "$2" = "" ] && {
		LOGFILE="$2"
		} || {
		LOGFILE="$(./command.cgi e2config loglocation)"
		}
		FILEEXT="$(./command.cgi fileext $(basename $LOGFILE))"
		RKVLOGFILE="$(echo $LOGFILE | sed 's/'$FILEEXT'$/_'$(date "+%Y%m%d%H%M")$FILEEXT'/')"
		# Copy logfile
		mv $LOGFILE $RKVLOGFILE
		[ ! "$GZIP" = "" ] && gzip $RKVLOGFILE
		chown nobody:nogroup $RKVLOGFILE$GZIP
		> $LOGFILE
		chown nobody:nogroup $LOGFILE
		[ "$(ps | grep [e]2guardian)" = "" ] && /etc/init.d/e2guardian restart
		echo "$RKVLOGFILE$GZIP"
	;;
	make_ip_user)
		$1
	;;

	percent)
		# returns the percentage of a work in progress
		# takes total amount of work to process as parameter $2
		# takes current amount of work already processed as parameter $3
		PERCENT=`expr $3 \* 100 / $2`
		[ "$PERCENT" -le "9" ] && PERCENT="0$PERCENT"
		echo "$PERCENT%"
	;;
	version)
		# returns version of the program
		echo "$(opkg list-installed | grep DTB_WebFilter)"
	;;
	send_file)
		# returns hexdump of file a content
		# takes filename as first parameter
		echo "$(hexdump -v -e '"\\\x" 1/1 "%02x"' $(echo $2 | sed 's/=//g'))"
	;;
	sed_escape)
		$1 $*
	;;
	*)
		echo "Unknown command"
	;;
esac

cd $PWD
