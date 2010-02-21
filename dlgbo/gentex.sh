#!/bin/bash
#########################################################################
# gentex.sh								#
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
#:begin_args
#-i+|--indir+ : Indir # input directory
#-o+|--outdir+ : Outdir # output directory
#-h|--help : Help # show this
#:end_args

. /usr/lib/psytools.sh
tt html2latex || exit
jtestpara $0 "$@" || exit

[[ ${Help} ]] && { genarghelp $0; exit; }
[[ ! ${Outdir} ]] && Outdir="./out/"
[[ ! ${Indir} ]] && Indir="./in/"

Fx=0
Cnt=0
IFS=$'\n'

Up(){ echo -en "\e[A"; }

SKey=$(echo "${Indir}" | grep -o \/ | wc -c)
let 'SKey/=2'
let 'SKey+=1'

for file in $(find ${Indir} | sort -ns -t "/" -k ${SKey} | tail -n +2)
do
	echo -en "processing ${file} ..."

	echo "<html><body>"		> ${file}.html 
	for line in $(cat $file)
	do
		{ echo -n "$line"| sed -e 's/</\&#060;/' -e 's/>/\&#062;/' ; echo "<br>"; } >> ${file}.html 
	done
	echo "</body></html>"  		>> ${file}.html    # generate html

	html2latex ${file}.html &>/dev/null
	rm ${file}.html

	echo "\\gboquote{$(basename ${file})}{" >> ${Outdir}/all_data${Fx}.tex
	sed -n '/\\begin{document}/,/\\end{document}/p' ${file}.tex | head -n -1 | tail -n +2 >> ${Outdir}/all_data${Fx}.tex
	echo "}" >> ${Outdir}/all_data${Fx}.tex
	rm ${file}.tex

	printf "%3d, %3d - done\n" ${Fx} ${Cnt}
	Up

	let 'Cnt++'
	[[ ${Cnt} -gt 500 ]] && { let 'Fx++'; Cnt=0; echo; }
done
