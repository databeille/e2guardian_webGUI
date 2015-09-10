#!/bin/sh

# Sends content-type
echo "Content-type: text/html"
echo 

# Get variables
WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\index.cgi//g)

source $WORKING_DIR*config

echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />"
echo "<title>Filtre Web e2guardian</title>"
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"tinac.cgi?style/rendering.css\">"
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"tinac.cgi?style/side-menu.css\">"
echo "</head><body><div id=\"layout\">"

# Catch users group

# Catch HTTP GET values
OPTS=`echo $QUERY_STRING | sed 's/&/ /g'`
for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  eval "$NAME=\$VALUE"
done

# Define configuration files array
set -- weightedphraselist exceptionphraselist bannedsitelist greysitelist bannedsslsitelist greysslsitelist exceptionsitelist bannedurllist greyurllist exceptionurllist exceptionregexpurllist bannedregexpurllist picsfile contentregexplist urlregexplist refererexceptionsitelist refererexceptionurllist embededreferersitelist embededrefererurllist urlredirectregexplist

# Catch configuration files

FIRSTGROUP="$E2G_CONFDIR*/e2guardianf1.conf"
# Starting a menu
MENU="<div id=\"menu\"><div id=\"main_menu\" class=\"pure-menu\"><ul>"

while [ $# -gt 0 ]
do
	value=$(grep -i -e "^$1" $FIRSTGROUP | awk -F= '{print $2}' | sed "s/'//g")
	eval "$1=\$value"
	#Add menu
	MENU="$MENU<li><a href=\"?edit=$(echo "$1")\">$(eval echo '$1')</a></li>"
#	echo "\$$1"
#	echo "<br/>"
#	echo "<input type href=#$1>"
#	cat $(eval echo "\$$1")
#	echo "</a>"
        shift;
done

# Ending a menu
MENU="$MENU</ul></div></div>"

# Starting main
CONTENT="<div id=\"main\"><div id=\"wrapper\">"

# Starting content
CONTENT="$CONTENT<div id=\"content\">"

# Display message if any
[ ! "$message" = "" ] && CONTENT="$CONTENT<div id=\"message\">$message</div>"

# Starting <form>
CONTENT="$CONTENT<form name=\"edit\" method=\"POST\" action=\"post.cgi\">"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"case\" name=\"case\" value=\"edit\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filealone\" name=\"filealone\" value=\"$edit\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"hash\" name=\"hash\" value=\"$(eval md5sum \$$edit | awk '{print $1}')\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filename\" name=\"filename\" value=\"$(eval echo \$$edit)\"/>"
CONTENT="$CONTENT<textarea id=\"textarea\" name=\"textarea\" rows=\"30\" cols=\"80\">"
[ ! "$edit" = "" ] && CONTENT="$CONTENT$(eval cat \$$edit)"
CONTENT="$CONTENT</textarea>"
CONTENT="$CONTENT<input type=\"submit\" value=\"Envoyer\"></form>"
# Ending content
CONTENT="$CONTENT</div></div></div>"

#Display page
echo "$MENU"
echo "$CONTENT"
echo "</div></body></html>"
