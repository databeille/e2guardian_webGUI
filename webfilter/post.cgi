#!/bin/sh
#

if [ "$REQUEST_METHOD" = "POST" ]; then
	read -n $CONTENT_LENGTH POST_STRING
fi

# Get variables and source config file
WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\post.cgi//g)
CONFIG="config"
cd "$WORKING_DIR"
. $CONFIG

OPTS=`echo $POST_STRING | sed 's/&/ /g'`
for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  eval "$NAME=\$VALUE"
done

# POST CASES

CASE=$(echo -ne $(uhttpd -d "$case"))

case "$CASE" in
  edit)
	HASH=$(echo -ne $(uhttpd -d "$hash"))
	FILEALONE=$(echo -ne $(uhttpd -d "$filealone"))
	FILENAME=$(echo -ne $(uhttpd -d "$filename"))
	TEXTAREA=$(echo -ne $(uhttpd -d "$textarea"))
	
	# Check MD5 of the file
	[ ! "$(md5sum $FILENAME | awk '{print $1}')" = "$HASH" ] && { RETURN="Erreur de somme de controle" ;
	} || {

		# Create backup directory
		mkdir -p $BACKUP$(echo "$FILENAME" | sed 's/'"$FILEALONE"'//g')
		[ ! "$?" = "0" ] && { RETURN="Impossible de créer le répertoire de backup" ;
		} || {

			#Create file backup
			
			cp $FILENAME $BACKUP$FILENAME.$(date | sed 's/ /_/g' | sed 's/:/./g')
			[ ! "$?" = "0" ] && { RETURN="Impossible de créer le fichier de backup" ;
			} || {

				#Modify file
				echo "$TEXTAREA" > "$FILENAME"
				[ ! "$?" = "0" ] && { RETURN="Impossible de modifier le fichier de configuration" ;
				} || {
					#All is fine
					RETURN="OK"
				}
			}
		}
	}
# Write content

echo "Content-type: text/html"
echo ""

# URL to redirect user

OPTS=`echo "$HTTP_REFERER" | cut -d'?' -f1- | sed 's/&/ /g'`
for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  eval "$NAME=\$VALUE"
done

[ ! "$message" = "" ] && { REDIRECTURL=$(echo $HTTP_REFERER | sed 's/'"message=$message"'/'"message=$RETURN"'/g') ; } || { REDIRECTURL="$HTTP_REFERER&message=$RETURN" ; }

echo "<!DOCTYPE HTML>"
echo "<html><head>"
echo "<meta charset=\"UTF-8\">"
echo "<meta http-equiv=\"refresh\" content=\"1;url=$REDIRECTURL\">"
echo "<script type=\"text/javascript\">window.location.href = \"$REDIRECTURL\"</script>"
echo "<title>Page Redirection</title>"
echo "</head>"
echo "<body>
        <!-- Note: don't tell people to `click` the link, just tell them that it is a link. -->
        If you are not redirected automatically, follow the <a href='$REDIRECTURL'>link to example</a>"

[ "$DEBUG" = "1" ] && {
echo "REQUEST_METHOD = $REQUEST_METHOD" ;
echo "CONTENT_TYPE = $CONTENT_TYPE" ;
echo "CONTENT_LENGTH = $CONTENT_LENGTH" ;
echo "REMOTE_HOST = $REMOTE_HOST" ;
echo "QUERY_STRING = $QUERY_STRING" ;
echo "POST_STRING = $POST_STRING" ;
echo "DOCUMENT_ROOT = $DOCUMENT_ROOT" ;
echo "HTTP_COOKIE = $HTTP_COOKIE" ;
echo "HTTP_HOST = $HTTP_HOST" ;
echo "HTTP_REFERER = $HTTP_REFERER" ;
echo "HTTP_USER_AGENT = $HTTP_USER_AGENT" ;
echo "HTTPS = $HTTPS" ;
echo "PATH = $PATH" ;
echo "REMOTE_ADDR = $REMOTE_ADDR" ;
echo "REMOTE_HOST = $REMOTE_HOST" ;
echo "REMOTE_PORT = $REMOTE_PORT" ;
echo "REMOTE_USER = $REMOTE_USER" ;
echo "REQUEST_URI = $REQUEST_URI" ;
echo "SCRIPT_FILENAME = $SCRIPT_FILENAME" ;
echo "SCRIPT_NAME = $SCRIPT_NAME" ;
echo "SERVER_ADMIN = $SERVER_ADMIN" ;
echo "SERVER_NAME = $SERVER_NAME" ;
echo "SERVER_PORT = $SERVER_PORT" ;
echo "SERVER_SOFTWARE = $SERVER_SOFTWARE" ;
}

echo "</body></html>"

        ;;
  logs)
	HASH=$(echo -ne $(uhttpd -d "$hash"))
	FILEALONE=$(echo -ne $(uhttpd -d "$filealone"))
	FILENAME=$(echo -ne $(uhttpd -d "$filename"))
	TEXTAREA=$(echo -ne $(uhttpd -d "$textarea"))

	echo "Content-Type: text/plain"
	echo "Content-Disposition: attachment; filename=\"$FILEALONE\""
	echo ""
	echo -ne "$(hexdump -v -e '"\\\x" 1/1 "%02x"' $(echo $FILENAME | sed 's/=//g'))"
	;;
  *)
        exit 1
esac
