#!/bin/bash
#########################################################################
# dlgbo.sh								#
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
#-h|--help : Help # show this
#-o+|--outdir+ : Outprefix # output directory
#-b+|--begin+ : cnt # start with <begin>
#-m+|--max+ : MaxCnt # donwnload up to this quote
#:end_args
. /usr/lib/psytools.sh
getArgs $0 "$@"
tt dos2unix,iconv,wget || help=1
[[ ${Help} ]] && { genarghelp $0; exit; }
[[ ! ${Outprefix} ]] && Outprefix="."
[[ ! ${cnt} ]] && cnt="2"

[[ ! -e ${Outprefix} ]] && mkdir -pv ${Outprefix}

while [[ ${cnt} -le ${MaxCnt} ]]
do
	jbegin "processing #${cnt}"
	  Data="$(curl -s http://german-bash.org/${cnt})"
	  [[ $( printf "%s" "${Data}" | grep 'span class="quote_zeile"') ]] && printf "%s" "${Data}" > "${Outprefix}/${cnt}" || false
	jend
	  
	let "cnt++"
done
