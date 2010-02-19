#!/bin/bash

#########################################################################
# fixkh.sh								#
# Copyright (C) 2010  Psyjo						#
#                                                                       #
# This program is free software; you can redistribute it and/or modify  # 
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation; either version 3 of the License,        #
# or (at your option) any later version.                                #
#                                                                       #
# This program is distributed in the hope that it will be useful, but   #
# WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  #
# See the GNU General Public License for more details.                  #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program; if not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

khFile="${HOME}/.ssh/known_hosts"

mkargs()
{
	while [[ $# -gt 0 ]]
	do
		echo -n "($1)"
		[[ $# -gt 1 ]] && echo -n "|"
		shift
	done
	echo
}

Data="$(egrep "$(mkargs "$@")" ${khFile})"
sedStr='s/\(.\{80\}\).*\(.\{20\}\)$/\1[...]\2/p'
line="-----------------------------------------------------------------------------------------------------------------"

while : ;
do

	echo -e "zu ignorierende zeilen angeben, keine eingabe: ausfuehren\n${line}"
	echo "${Data}" | sed -n "${sedStr}" | cat -n
	echo "${line}"
	read toDel

	if [[ ${toDel} ]]
	then
		for n in $(echo ${toDel} | tr " " "\n" | sort -nr | tr "\n" " ")
		do
			Data=$(echo "${Data}" | sed "${n}d")
		done
	else break
	fi
	unset toDel
done

[[ ! ${Data} ]] && exit 0

echo -e "\nloesche folgende...\n"

IFS=$'\n'
for l in ${Data}
do
	echo "${l}" | sed -n "${sedStr}"
	sed -i "$(grep -n "${l}" ${khFile} | awk -F: '{print $1}')d" ${khFile}
done
