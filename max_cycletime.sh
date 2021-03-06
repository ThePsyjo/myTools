#!/bin/bash
#########################################################################
# max_cycletime.sh                                                      #
# Copyright (C) 2010  Psyjo                                             #
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

eexit()
{
	Ret=$1
	shift
	echo "$*"
	exit ${Ret}
}

doHelp()
{
	echo -e "Usage: ./$0 <destination IP>"
}

[[ $# -eq 1 ]] || { doHelp; eexit 1 "Argumentcount does not match"; }
Ip=$(echo $1 | egrep -o "([0-9]{1,3}\.){3}[0-9]{1,3}")
[[ ${Ip} ]] || { doHelp; eexit 1 "Argument is not an IP"; }
echo -n "checking host...  "
ping -c3 $Ip >/dev/null || eexit 0 "Host unreachable" && echo OK

d_p() { ping -c1 $Ip | sed -n '2p' | awk '{print $7}' | cut -d = -f 2; }

echo "Hit Ctrl+C to exit"
val_old=0
while :
do
	val=$(d_p)
	if [[ ${val} ]]
	then
		[[ $(echo "${val} < ${val_old}" | bc) -eq 1 ]] && val=$val_old
		val_old=$val
	else
		val_old=0
		val="not reachable"
	fi

	[[ "$val" != "$last_echo" ]] && echo $val
	last_echo=$val
	sleep 1
done
