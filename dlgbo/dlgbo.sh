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
#:end_args
. /usr/lib/psytools.sh
getArgs $0 "$@"
tt dos2unix,iconv,wget || help=1
[[ ${Help} ]] && { genarghelp $0; exit; }
[[ ! ${Outprefix} ]] && Outprefix="."
[[ ! ${cnt} ]] && cnt="2"

extract()
{
  dos2unix -q "$1"

  iconv -f utf-8 -t latin1 "$1" |\
	sed -n '/<div class="zitat">/,/<\/div>/p' |\
	head -n -1 | tail -n +2 |\
	sed 	's/<[ a-z="_]*>//g;
		s/<\/span>//g;
		s/&lt;/</g;
		s/&gt;/>/g;
		s/^\t*//g;
		s/^ *//g;
		s/^\t*//g;
		s/^ *//g;
		s/^$//g;' > /tmp/$$


  mv /tmp/$$ "$1"
}

while true
do
	jbegin "processing #${cnt}"
	  wget -q http://german-bash.org/${cnt} -O "${Outprefix}/${cnt}"
	  extract "${Outprefix}/${cnt}"
	  if [[ $(du -b "${Outprefix}/${cnt}"|cut -f 1) -eq 0 ]]
	  then rm "${Outprefix}/${cnt}"; false
	  else true
	  fi
	jend
#	  [[ $(du -b "${Outprefix}/${cnt}"|cut -f 1) -eq 0 ]] && {
#	  	tab; jwarn "file is empty"
#		rm "${Outprefix}/${cnt}"
#	  }
	  
	let "cnt++"
done
