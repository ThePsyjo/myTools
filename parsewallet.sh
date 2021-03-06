#!/bin/bash
##############################
#       parsewallet.sh       #
#                            #
# 	      2008 by Psyjo© #
##############################
# Distributed under the terms of the GNU General Public License v2

#:begin_version
#Version 1.2.3
#:end_version

. /usr/lib/psytools.sh

#:begin_args
#-f+ | --file+ : File # file to use
#-s+ | --fs+ | --fieldseperator+ : deli # use costum fieldseperator
#-n | --nocolor : Nocolor # disable color output
#-t | --tabs : Tab # tab-output
#-h | --help : Help # display this help
#:end_args

getArgs $0 "$@" || Help=set

[[ ${Nocolor} ]] && unset YELOW HIBLUE BLUE GREEN RED WARN ERROR GOOD
dsplhelp() { get_ver $0 /usr/lib/psytools.sh;echo; genarghelp $0; exit; }
[[ ${Help} ]] && dsplhelp
[[ ${Tab} ]] && { [[ ${deli} ]] && deli=","; }
[[ ! ${deli} ]] && deli="," # default seperator

[[ ! ${File} ]] && dsplhelp
[[ $(fex ${File}) ]] && { jerror "file \"${File}\" not found, abort"; dsplhelp; }

[[ $(head -1 ${File} | grep "date,refID,refType,ownerName1,ownerName2,argName1,amount,balance,reason") ]] && { jinfo "using journal mode\n"; Journal=1; }
[[ $(head -1 ${File} | grep "date,transID,quantity,type,price,clientName,stationName,transactionType,transactionFor") ]] && { jinfo "using transaction mode\n"; Trans=1; }
[[ ! ${Journal} && ! ${Trans} ]] && jerror "file unknown, exiting..."

cu()
{ echo "$1" | cut -d , -f $2; }

getcols
Wid=$(((${COLS} -30 ) / 4))

IFS=$'\n'
[[ ${Trans} ]] && {
	for line in $(cat ${File})
	do
		[[ "$(echo "$line" | grep -o "^date")"  == "date" ]] && 
			{ echo -e "${BLUE}$(cu "${line}" 1)	${HIBLUE}$(cu "${line}" 4)	${YELOW}$(cu "${line}" 3)	${GREEN}$(cu "${line}" 5)"; continue;}
		if [ $(cu "${line}" 8 | grep "Sell" ) ]
		then 
			Col="${GREEN}+"
		else
			Col="${RED}-"
		fi

		if [[ ${Tab} ]]
		then
			Output1="${BLUE}$(cu "${line}" 1)"
			Output2="${HIBLUE}$(cu "${line}" 4)"
			Output3="${YELOW}$(cu "${line}" 3)"
			Output4="${Col}$(printf "%'.2f" $(cu "${line}" 5 | tr "." ","))"
			Output5="${Col}$(printf "%'.2f" $(echo "$(cu "${line}" 3)*$(cu "${line}" 5)" | bc -l | tr "." "," ))"
			printf "%-30s %-${Wid}s %-${Wid}s %-${Wid}s %-${Wid}s\n" ${Output1} ${Output2} ${Output3} ${Output4} ${Output5}
		else
			echo -e "${BLUE}$(cu "${line}" 1)${deli}${HIBLUE}$(cu "${line}" 4)${deli}${YELOW}$(cu "${line}" 3)${deli}${Col}$(cu "${line}" 5)$(echo "$(cu "${line}" 3)*$(cu "${line}" 5)" | bc -l)"
		fi
	done
}

[[ ${Journal} ]] && {
	for line in $(cat ${File})
	do
		[[ "$(echo "$line" | grep -o "^date")"  == "date" ]] && 
			{ echo -e "${BLUE}$(cu "${line}" 1)	${HIBLUE}$(cu "${line}" 3)	${GREEN}$(cu "${line}" 7)	${YELOW}$(cu "${line}" 8)"; continue;}
		if [ $(cu "${line}" 7 | grep "^-" ) ]
		then 
			Col="${RED}"
		else
			Col="${GREEN}"
		fi
		
		if [[ ${Tab} ]]
		then
			Output1="${BLUE}$(cu "${line}" 1)"
			Output2="${HIBLUE}$(cu "${line}" 3)"
			Output3="${Col}$(printf "%'.2f" $(cu "${line}" 7 | tr "." ","))"
			Output4="${YELOW}$(printf "%'.2f" $(cu "${line}" 8 | tr "." ","))"
			printf "%-30s %-${Wid}s %-${Wid}s %-${Wid}s\n" ${Output1} ${Output2} ${Output3} ${Output4}
		else
			echo -e "${BLUE}$(cu "${line}" 1)${deli}${HIBLUE}$(cu "${line}" 3)${deli}${Col}$(cu "${line}" 7)${deli}${YELOW}$(cu "${line}" 8)"
		fi
	done
}
