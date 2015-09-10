#!/bin/sh
#
# TINAC stands for "This Is Not A CGI"
# It helps display file content for cgi-bin purpose

#Document working directory
WORK_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\.cgi//g)

#Entering directory
cd $WORK_DIR

#Sends Content-type
echo "Content-type: text/plain"
echo 
echo "$(cat $QUERY_STRING)"
