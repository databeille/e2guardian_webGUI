#!/bin/sh

# Get variables and source config file
WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\index.cgi//g)
cd "$WORKING_DIR"
source config

# Catch HTTP GET values and set variables
OPTS=`echo $QUERY_STRING | sed 's/&/ /g'`
for opt in $OPTS
do
  NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
  VALUE=`echo $opt | sed 's/=/ /g' | awk '{print $2}' |  sed 's,%,\\\x,g' | sed 's/+/ /g'`
  eval "$NAME=\$VALUE"
done
reformat_lightsquid() {
	LSCGI=$1
	[ -f "$WORKING_DIR*lightsquid/$LSCGI.cgi" ] &&  {
		echo "La page demandée n'existe pas."
	} || {
		LSCONTENT=$($WORKING_DIR*lightsquid/$LSCGI.cgi | tail -n +4)
#		LSCONTENT=$(echo $LSCONTENT)

		## replaces references to "index.cgi"
		LSCONTENT=`echo "$LSCONTENT" | sed 's/index.cgi/index.cgi?logs=stats/g'`
		
		## replaces references to a direct cgi script
		set -- topsites month_detail year_detail whousesite day_detail group_detail user_detail user_month user_year bigfiles graph user_time get
		while [ $# -gt 0 ]
			do
			[ "$1" = "get" ] && 
			{	
				## replaces references to "get.cgi"	
				LSCONTENT=`echo "$LSCONTENT" | sed 's/get.cgi/tinac.cgi/g'`
			} || {
				LSCONTENT=`echo "$LSCONTENT" | sed 's/'$1'.cgi?/index.cgi?logs=stats\&page='$1'\&/g'`
			}
			shift;
		done
	}
	echo "$LSCONTENT"
}



# Catch users group
# Catch configuration files
E2GCONFIG="$(./command.cgi e2config)"
FIRSTGROUP="$(./command.cgi e2fconfig 1)"

# What is the logfile ?
LOGFILE="$(grep -i -e 'loglocation = ' $E2GCONFIG | awk -F= '{print $2}' | sed "s/'//g")"
LOGFILEDIRNAME="$(dirname $LOGFILE)"

# Define configuration files array
set -- weightedphraselist exceptionphraselist bannedsitelist greysitelist bannedsslsitelist greysslsitelist exceptionsitelist bannedurllist greyurllist exceptionurllist exceptionregexpurllist bannedregexpurllist picsfile contentregexplist urlregexplist refererexceptionsitelist refererexceptionurllist embededreferersitelist embededrefererurllist urlredirectregexplist

# Starting list of configuration files
E2GF1="<li class=\"dropdown\"><a class=\"menu\" href=\"#\">Groupe 1</a><ul class=\"dropdown-menu\">"
while [ $# -gt 0 ]
do
	value=$(grep -i -e "^$1" $FIRSTGROUP | awk -F= '{print $2}' | sed "s/'//g")
	eval "$1=\$value"
	#Add menu
	E2GF1="$E2GF1<li><a href=\"?edit=$(echo "$1")\">$(eval echo '$1')</a></li>"
#	echo "\$$1"
#	echo "<br/>"
#	echo "<input type href=#$1>"
#	cat $(eval echo "\$$1")
#	echo "</a>"
        shift;
done
E2GF1="$E2GF1</ul></li>"

# Menu for log files
LOGS="<li class=\"dropdown\"><a class=\"menu\" href=\"?logs=config\">Logs</a><ul class=\"dropdown-menu\">"
LOGS="$LOGS<li><a href=\"?logs=config\">Configuration</a></li>"
LOGS="$LOGS<li><a href=\"?logs=$(echo $LOGFILE | sed "s@$LOGFILEDIRNAME/@@g")\">View</a></li>"
LOGS="$LOGS<li><a href=\"?logs=stats\">Statistics</a></li>"

LOGS="$LOGS</ul></li>"

# Starting a menu
MENU="<div id=\"menu\"><div id=\"main_menu\" class=\"pure-menu\"><ul>"

MENU="$MENU*$E2GF1"
# Ending a menu
MENU="$MENU</ul></div></div>"

# Starting main
CONTENT="<div id=\"main\"><div id=\"wrapper\">"

# Starting content
CONTENT="$CONTENT<div id=\"content\">"

# Display message if any
[ ! "$message" = "" ] && CONTENT="$CONTENT<div id=\"message\">$message</div>"

### Edition of a file
[ ! "$edit" = "" ] && {
# Starting <form>
CONTENT="$CONTENT<form name=\"edit\" method=\"POST\" action=\"post.cgi\">"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"case\" name=\"case\" value=\"edit\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filealone\" name=\"filealone\" value=\"$edit\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"hash\" name=\"hash\" value=\"$(eval md5sum \$$edit | awk '{print $1}')\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filename\" name=\"filename\" value=\"$(eval echo \$$edit)\"/>"
CONTENT="$CONTENT<textarea id=\"textarea\" name=\"textarea\" rows=\"30\" cols=\"80\">"
CONTENT="$CONTENT$(eval cat \$$edit)"
CONTENT="$CONTENT</textarea>"
CONTENT="$CONTENT<input type=\"submit\" value=\"Envoyer\"></form>"
}

### View and download of a file
[ ! "$view" = "" ] && {
# Starting <form>
CONTENT="$CONTENT<form name=\"view\" method=\"POST\" action=\"post.cgi\">"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"case\" name=\"case\" value=\"view\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filealone\" name=\"filealone\" value=\"$view\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"hash\" name=\"hash\" value=\"$(eval md5sum \$$view | awk '{print $1}')\"/>"
CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filename\" name=\"filename\" value=\"$(eval echo \$$view)\"/>"
CONTENT="$CONTENT<textarea id=\"textarea\" name=\"textarea\" rows=\"30\" cols=\"80\">"
CONTENT="$CONTENT$(eval cat \$$view)"
CONTENT="$CONTENT</textarea>"
CONTENT="$CONTENT<input type=\"submit\" value=\"Envoyer\"></form>"
}

### Manage logs
[ ! "$logs" = "" ] && {

# What is the logfile ?
LOGFILE="$(grep -i -e 'loglocation = ' $E2GCONFIG | awk -F= '{print $2}' | sed "s/'//g")"

set -- loglevel logexceptionhits logfileformat maxlogitemlength anonymizelogs logsyslog loglocation 
# Load log configuration
while [ $# -gt 0 ]
	do
        value="$(grep -i -e "$1 = " $E2GCONFIG | awk -F= '{print $2}' |  sed "s/ //g")"
       	eval "$1=\$value"
       	shift;
done


case "$logs" in
	config)
	# Display log configuration
	set -- loglevel logexceptionhits logfileformat maxlogitemlength anonymizelogs logsyslog loglocation 
	while [ $# -gt 0 ]
		do
		CONTENT="$CONTENT<div class=\"cbi-tabcontainer\"><div class=\"cbi-value\" id=\"e2gconfig_$1\"><label class=\"cbi-value-title\">$1</label>"
		CONTENT="$CONTENT<div class=\"cbi-value-field\">"
		CONTENT="$CONTENT<input type=\"text\" value=\"$(eval echo \$$1)\"/>"
		CONTENT="$CONTENT</div></div></div>"
	        #Add menu
	#       echo "\$$1"
	#       echo "<br/>"
	#       echo "<input type href=#$1>"
	#       cat $(eval echo "\$$1")
	#       echo "</a>"
        	shift;
		done
	;;
	stats)
	# Display stats tables
	[ "$page" == "" ] && page="index"
	CONTENT="$CONTENT$(reformat_lightsquid $page)"
	;;
	*)
	([ "$LOGFILE" = "" ] || [ "$loglevel" = "0" ]) && CONTENT="$CONTENT logging is disabled"
#	CONTENT="$CONTENT<textarea id=\"textarea\" name=\"textarea\" rows=\"30\" cols=\"80\">"
#	CONTENT="$CONTENT$(eval cat $(dirname $LOGFILE)/$logs)"
#	CONTENT="$CONTENT</textarea>"
	# Starting <form>
	CONTENT="$CONTENT<form name=\"logs\" method=\"POST\" action=\"post.cgi\">"
	CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"case\" name=\"case\" value=\"logs\"/>"
	CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filealone\" name=\"filealone\" value=\"$logs\"/>"
	CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"hash\" name=\"hash\" value=\"$(md5sum $(dirname $LOGFILE)/$logs | awk '{print $1}')\"/>"
	CONTENT="$CONTENT<input type=\"$INPUTTYPE\" id=\"filename\" name=\"filename\" value=\"$(dirname $LOGFILE)/$logs\"/>"
	CONTENT="$CONTENT$(ls -1c $(dirname $LOGFILE) | while read line
						do
						echo "<div><a href=\"?logs=$line\">"
						[ "$logs" = "$line" ] && echo ">>> "
						echo "$line</a><br/></div>"
						shift;
					done)"
	CONTENT="$CONTENT<input type=\"submit\" value=\"Télécharger\"></form>"
	;;
esac
	
}
echo "Content-type: text/html"
echo 

#echo "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">"
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />"
echo "<title>Filtre Web e2guardian</title>"
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"tinac.cgi?style/rendering.css\" />"
echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"tinac.cgi?style/side-menu.css\" />"
echo "</head><body>"
echo "<header>"
echo "<div class=\"fill\">"
echo "<div class=\"container\">"
echo "<a class=\"brand\" href=\"#\">E2Guardian</a>"
echo "<ul class=\"nav\">"
echo "$E2GF1"
echo "$LOGS"
echo "</ul>"
echo "</div>"
echo "</div>"
echo "</header>"
echo "<div id=\"layout\" class=\"container\">"


#Display page
#echo "$MENU"
echo "$CONTENT</div></div></div>"

echo "</div></body></html>"
