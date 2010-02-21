#! /bin/bash
# Copyright 2006 Psyjo©
# Distributed under the terms of the GNU General Public License v3
#:begin_version
#Version 1.2.2-2
#:end_version
############################## tests ########################################
function checkvars()
{
  for item in "${SRCPATH}";do
    [[ ! -r ${item} ]] && echo "${BAD}${item} existiert nicht - editieren! (/etc/bmk.conf)${NORMAL}" && exit
  done
  for item in "${SRCPATH}" "${LINPATH}" "${IMGPATH}";do
    [[ -z ${item} ]] && echo -e "${BAD}fehlende Variable - editieren! (/etc/bmk.conf)\nSRCPATH\nLINPATH\nIMGPATH\nSORTAL\n${NORMAL}"&& exit
  done
  [[ `echo ${IMGPATH} | grep -i "<arch>"` != "" ]] && echo -e "${BAD}Architektur nicht angegeben - editieren! (/etc/bmk.conf)${NORMAL}" && exit
}
function pretest1()
{
  [[ $UID != 0 ]]                          && echo -e "\n$BAD\tNur root kann das Script benutzen!$NORMAL\n" && exit
  [[ ! -r /etc/gentoo-release ]]           && echo -e "\n$BAD\tNur für Gentoo geeignet!$NORMAL\n"           && exit
  [[ -z `ls -l /usr/src/ | grep gentoo` ]] && echo -e "\n$BAD\tGentoo-sources nicht installiert!$NORMAL\n"  && exit
}
############################## tests ########################################

if [[ -r /usr/lib/psytools.sh ]]
then
  source /usr/lib/psytools.sh
  pretest1
  jset_time full
else
  echo -e "${BAD}/usr/lib/psytools.sh nicht gefunden!\nAbbruch${NORMAL}"
  exit
fi

if [[ -r /etc/bmk.conf ]]
then
  source /etc/bmk.conf
  checkvars
  LINPATH=`echo ${LINPATH} | sed 's/\/*$//'`
else
  echo -e "${BAD}/etc/bmk.conf nicht gefunden!\nerstellen oder installieren!${NORMAL}"
  exit
fi

if [[ -r /usr/lib/bmk_functions.sh ]]
then
  source /usr/lib/bmk_functions.sh
else
  echo -e "${BAD}/usr/lib/bmk_functions.sh nicht gefunden!\nAbbruch${NORMAL}"
  exit
fi

if [[ -r ${USERFUNCT_DIR} ]]
then
  source "$USERFUNCT_DIR"
  USERFUNCT=1
else
  USERFUNCT=""
fi

##########################################  bis hier dateien einbinden
cd $SRCPATH || exit
pretest2 $*
prebegin
[[ $HELP ]] && _help
userfunct begin
testlink
cd $LINPATH || { jexit "konnte nicht nach ${LINPATH} wechseln"; }
prebuild
verset
jset_time
kbuild
jinfo "Bauzeit : `jget_time`"
[[ $NODRV_MORE ]] && verset
drv
userfunct end
jinfo "Laufzeit : `jget_time full`"
