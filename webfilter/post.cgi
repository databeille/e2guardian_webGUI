#!/bin/sh
#

if [ "$REQUEST_METHOD" = POST ]; then
	read -n $CONTENT_LENGTH QUERY_STRING
fi

echo "Content-type: text/plain"
echo ""
echo "REQUEST_METHOD = $REQUEST_METHOD"
echo "CONTENT_TYPE = $CONTENT_TYPE"
echo "CONTENT_LENGTH = $CONTENT_LENGTH"
echo "REMOTE_HOST = $REMOTE_HOST"
echo "QUERY_STRING = $QUERY_STRING"
echo "DOCUMENT_ROOT = $DOCUMENT_ROOT"
echo "HTTP_COOKIE = $HTTP_COOKIE"
echo "HTTP_HOST = $HTTP_HOST"
echo "HTTP_REFERER = $HTTP_REFERER"
echo "HTTP_USER_AGENT = $HTTP_USER_AGENT"
echo "HTTPS = $HTTPS"
echo "PATH = $PATH"
echo "REMOTE_ADDR = $REMOTE_ADDR"
echo "REMOTE_HOST = $REMOTE_HOST"
echo "REMOTE_PORT = $REMOTE_PORT"
echo "REMOTE_USER = $REMOTE_USER"
echo "REQUEST_URI = $REQUEST_URI"
echo "SCRIPT_FILENAME = $SCRIPT_FILENAME"
echo "SCRIPT_NAME = $SCRIPT_NAME"
echo "SERVER_ADMIN = $SERVER_ADMIN"
echo "SERVER_NAME = $SERVER_NAME"
echo "SERVER_PORT = $SERVER_PORT"
echo "SERVER_SOFTWARE = $SERVER_SOFTWARE"

OPTS=`echo $QUERY_STRING | sed 's/&/ /g'`
for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  eval "$NAME=\$VALUE"
done

echo -n -e $(uhttpd -d "$textarea")
