#!/bin/bash

dspl()
{
        Out="$(set | egrep -v "^Out|^_" | egrep "from[0-9]*to[0-9*]" | sort -n -r -t '=' -k 2 | head -n 50)"

        if [[ "${varMap}" == "$(echo "${Out}" | awk -F= '{print $1}' | md5sum)" ]]
        then  tput cup 0 0
        else  clear
        fi
        varMap="$(echo -e "${Out}" | awk -F= '{print $1}' | md5sum)"
	echo -e "===\n${Out}\n==="
}

clear
while read l
do
        echo "$l"
        if [[ "$(echo $l | grep "^extents")" ]]
        then
                let $(echo "$l" | awk '{print "from"$3"to"$5}')++
                dspl
        else
                continue
        fi
done
echo
