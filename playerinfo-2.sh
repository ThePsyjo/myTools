#!/bin/bash 
##############################
#        Playerinfo-2        #
#                            #
# Copyright 2009-2010 Psyjo© #
##############################
#
# Distributed under the terms of the GNU General Public License v2

[[ ! $1 ]] && set "\n" # set $1 to \n
fix() { ~/bin/fixname 3 0; }
#spl() { sed 's/[a-Z]*: \(.*\)/\1/'; }
spl() { awk -F: '{print $2}' | sed 's/^ //'; }
grp() { qdbus org.kde.amarok /Player GetMetadata | grep $1 | spl | fix; }
if [[ "$(qdbus org.kde.amarok /Player GetMetadata)" ]]
then
	Title="$(grp artist) - $(grp title)"
	Album="$(grp album)"
	echo -e "${Title:+-= now playing =-$1Title > ${Title}}${Album:+$1Album > ${Album}}"
else
	echo -e "-= silence =-"
fi
