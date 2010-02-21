#!/bin/bash
#########################################################################
# boincwatch.sh								#
# Copyright (C) 2009  Psyjo						#
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

#:begin_version
#version 1.4.2-3
#:end_version

umask 177

LogFile=logs/boincwatch.log
ConfigFile=/etc/conf.d/boincwatch.conf
Me=$(basename $0)
Pid=$(echo $$)

now(){ date '+[ %Y-%m-%d %T ]'; }
tolog(){ echo "$(now) $*" >> ${LogFile}; } #log on
#tolog(){ echo "$*" >> /dev/null; } #log off

Op()
{
	for Proj in ${Projects}
	do
		tolog "  $1 ${Proj}"
		boinc_cmd --project ${Proj} $1
		State="$1"
	done
}

exitfunc()
{
	echo -e "$(now) == shutdown == (${Pid})" >> ${LogFile}
	Op suspend
	kill ${SleepPid}
	exit 0
}
trap 'exitfunc' 2 6 9 15

Running=$(ps -A | grep ${Me} | grep -v $$ | grep -v "pts/" | cut -d ? -f 1)
[[ "${Running}" ]] && { echo "${Me} (${Running}) already running"; exit 0; } #exit if running

getconfig(){ . ${ConfigFile} || tolog "== WARNING: configfile not specified"; [[ ! ${MaxTemp} ]] && MaxTemp=40; }

echo -e "\n$(now) == boincwatch started == (${Pid})" >> ${LogFile}

getconfig
	
sleep 160s &	 #
SleepPid=$!	 #
wait ${SleepPid} # waiting for boinc to settle

while :
do
	Temp=$(GetCpuTemp) # muss in der config angegeben sein
### fuer statische verwendung :
#	Temp=$(sensors | grep "CPU Temp" | sed 's/.*\(^.*(\).*/\1/; s/.*+\([0-9]\+\).*/\1/')
#	Temp=$(sensors | grep "CPU Temp" | grep -o "[0-9]*\." | sed 's/.$//')
###	Temp=$(sensors | grep "CPU Temp" | sed 's/.*: *+//;s/°.*//;s/\..//') # funt im script nicht !!
	
	if [[ ${Temp} -lt ${MaxTemp} ]]
	then
		[[ "${State}" != "resume" ]] && {
			tolog "${Temp} -lt ${MaxTemp}"
			Op resume
		}
	else
		[[ "${State}" != "suspend" ]] && {
			tolog "${Temp} -gt ${MaxTemp}"
			Op suspend
		}
	fi
	if [[ ${Cnt} -lt 30 ]]		#
	then				#
		let Cnt++		# config alle 5 minuten laden
	else				#
		Cnt=0			#
		MaxTempBuf=${MaxTemp}	#
		getconfig			#
		[[ ${MaxTempBuf} -ne ${MaxTemp} ]] && tolog "== max Temp set to ${MaxTemp}" # bei aenderung loggen
	fi				#
	sleep 10s &
	SleepPid=$!
	wait ${SleepPid}
done
