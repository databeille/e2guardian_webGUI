#!/bin/sh
#
# TINAC stands for "This Is Not A CGI"
# It helps display file content for cgi-bin purpose

([ "$QUERY_STRING" = "" ] && [ "$*" = "" ]) && exit 1

#Commandline script
#Document working directory
WORKING_DIR="$PWD"
[ "$QUERY_STRING" = "" ] && QUERY_STRING="$*"

#Online script
[ ! "$DOCUMENT_ROOT" = "" ] && WORKING_DIR="$(dirname $DOCUMENT_ROOT$SCRIPT_NAME)"


OPTS=`echo $QUERY_STRING | sed 's/&/ /g'`

for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  [ ! "$VALUE" == "" ] && eval "$NAME=\$VALUE"
done

[ ! "$png" = "" ] && { EXT="png" ; IMAGE="$png" ; }
[ ! "$gif" = "" ] && { EXT="gif" ; IMAGE="$gif" ; }
[ ! "$jpg" = "" ] && { EXT="jpg" ; IMAGE="$jpg" ; }

case "$EXT" in
	png|gif|jpg)
	#Entering directory
	cd $WORKING_DIR
	CONTENTTYPE="image/$EXT"
	DATA=$(./lightsquid/get.cgi $EXT=$IMAGE | tail -n +3 | hexdump -v -e '"\\\x" 1/1 "%02x"')
#	CONTENTLENGTH=$(echo $DATA | awk '{print length($0)}')
	;;
	*)
	#Entering directory
	cd $WORKING_DIR/tinac
	CONTENTTYPE="text/plain"
	DATA="$(cat $(echo $QUERY_STRING | sed 's/=//g'))"
	;;
esac
echo "Content-Type: $CONTENTTYPE"
[ ! "$CONTENTLENGTH" = "" ] && echo "Content-Length: $CONTENTLENGTH"
echo ""
echo -ne "$DATA"
