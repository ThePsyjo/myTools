#!/bin/bash

#########################################################################
# runapp.sh								#
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

. /usr/lib/psytools.sh || exit

#:begin_args
#-w+ | --winecmd+ : WineCmd # use this command
#-r | --reg : Reg # run Reg
#-c | --conf : Conf # winecfg
#-p+ | --prefix+ : WINEPREFIX # ! wine should work here
#-B+ | --bindir+ : Bindir # ! binary is here
#-i+ | --install+ : Setupfile # install this
#-v | --verbose : Verbose # show all errors
#-b+ | --binfile+ : Binfile # ! run this binfile
#-a+ | --args+ : Exeargs # Arguments for executable
#-g | --gfxsetup : GraphicSetup # do load graphic settings
#-l+ | --log+ : Log # log into this file
#-o+ | --other+ : Other # run other stuff
#-h | --help : Help # show this help
#-V | --version : Version # Show version
#:end_args

#:begin_version
#version 1.4.3-2
#:end_version

dohelp(){ genarghelp $0; }
dohelpx(){ dohelp; exit 1; }
doerror(){ dohelp; jexit "$1"; }

getArgs $0 "$@" || dohelpx
[[ ${Version} ]] && { get_ver /usr/lib/psytools.sh $0; exit 0;  }
[[ ${Help} ]] && dohelpx
[[ ! ${WineCmd} ]] && WineCmd=wine
[[ ! ${WINEPREFIX} ]] && doerror "--prefix not set"
export WINEPREFIX
[[ ! -e "${WINEPREFIX}" ]] && mkdir -p ${WINEPREFIX}

[[ ! ${Log} ]] && Log=/dev/null
doexec()
{
	if [[ ${Verbose} ]]
	then
		echo "logging to ${Log}"
		echo "pwd > $(pwd)"
		echo "exec > ${WineCmd} \"$*\" \"${Exeargs}\""
		${WineCmd} $* ${Exeargs} | tee ${Log}
	else
		${WineCmd} $* ${Exeargs} &> ${Log} 
	fi
}

[[ "${Setupfile}" ]] && { jbegin "starting install"; doexec ${Setupfile}; jend; exit; }; 

if [[ ${Conf} || ${Reg} || ${Other} ]]
then
	[[ ${Reg} ]] && regedit
	[[ ${Conf} ]]  && winecfg
	[[ ${WINEPREFIX} ]] && cd "${WINEPREFIX}/${Bindir}"
	[[ "${Other}" ]] && { eval "${Other}"; }
else
	[[ ! ${Bindir} ]] && doerror "--bindir not set"
	cd "${WINEPREFIX}/${Bindir}" || jexit "unable to change to bindir"
	[[ ! ${Binfile} ]] && doerror "--binfile not set"
	
	[[ ${GraphicSetup} ]] && jdo "activate graphic settings" "nvidia-settings -l -a InitialPixmapPlacement=2 -a GlyphCache=1"
	jbegin "run"
		doexec ${Binfile}
	jend
fi
