##############################
#          PsyTools          #
#                            #
# Copyright 2006-2008 Psyjo© #
##############################
#
# Parts by Gentoo Foundation
#
# Distributed under the terms of the GNU General Public License v2
#:begin_version
#Version 1.2.9
#:end_version
#!begin_version
#Version 1.2.9
#!end_version

#Variablen:
#
# VERBOSE	- grosszuegige Ausgaben der Psytools aktivieren
# Jrun_Debug	- Debugmodus von jrun aktivieren
# JRUN_PARAMETER- Argumente bei dem Aufruf der tmp-Funktion in jrun
# FORCE		- Erzwingt das Ueberschreiben von Dateien in jinstall
#
# monochrom is bloed ;)
# deswegen hier ein paar Farben by Gentoo
GOOD=$'\e[32;01m'
GREEN=$'\e[32;01m'

WARN=$'\e[33;01m'
YELOW=$'\e[33;01m'

BAD=$'\e[31;01m'
RED=$'\e[31;01m'

HILITE=$'\e[36;01m'
HIBLUE=$'\e[36;01m'

BRACKET=$'\e[34;01m'
BLUE=$'\e[34;01m'

NORMAL=$'\e[0m'

jline() # Linie ueber volle Shellbreite | $1 leerzeile vor line, $2 leerzeile nach line
{
  getcols
  [[ $1 ]] && echo
   for (( n = 0; n < ${COLS}; n++ )); do echo -n -; done; echo
  [[ $2 ]] && echo
}

inline() # beginnt einen vorgang in Linien | anzeige wenn $VERBOSE
{
  [[ $VERBOSE ]] && jline "x" 
  jbegin "$*"
  [[ $VERBOSE ]] && jline "" "x"
}

still() # fuehrt  $* &> /dev/null  aus | anzeige wenn $VERBOSE
{
  if [ $VERBOSE ] || [ ${Jrun_Debug} ]
  then eval "$*"
  else eval "$*" &> /dev/null
  fi
}

jinfo() # original by Gentoo Foundation modded by Psyjo
{
  jinfon "$*\n"
  LAST_CMD="jinfo"
  return 0
}

jinfon()# original by Gentoo Foundation modded by Psyjo
{
  [[ ${LAST_CMD} == "jbegin" ]] && echo
  echo -ne " ${GOOD}*${NORMAL} $*"
  LAST_CMD="jinfon"
  return 0
}

jwarn()# original by Gentoo Foundation modded by Psyjo
{
  [[ ${LAST_CMD} == "jbegin" ]] && echo
  echo -e " ${WARN}*${NORMAL} $*"
  LAST_CMD="jwarn"
  return 0
}

jerror()# original by Gentoo Foundation modded by Psyjo
{
  [[ ${LAST_CMD} == "jbegin" ]] && echo
  echo -e " ${BAD}*${NORMAL} $*"
  return 0
}

jexit()
{
  jerror "$*"
  exit
}

jbegin() #beginnt einen Vorgang # original by Gentoo Foundation modded by Psyjo
{
   msg="$* ..."

  jinfon "${msg}"
  echo

  LAST_LEN="$(( 3 + ${#msg} ))"
  LAST_CMD="jbegin"
  return 0
}
       # private
_end() ## original by Gentoo Foundation modded by Psyjo
{
  getcols
  local retval="${1:-0}" efunc="${2:-eerror}" msg
  shift 2

  if [[ ${retval} == "0" ]] ; then
    msg="${BRACKET}[ ${GOOD}ok${BRACKET} ]${NORMAL}"
  else
    if [[ -n $* ]] ; then
      ${efunc} "$*"
    fi
      msg="${BRACKET}[ ${BAD}!!${BRACKET} ]${NORMAL}"
  fi

  echo -e "${ENDLN}  ${msg}"
  return ${retval}
}
        # less private
_jend() # beendet einen Vorgang # original by Gentoo Foundation modded by Psyjo
{
  local retval="${1:-0}"
  shift
  _end "${retval}" jerror "$*"
  LAST_CMD="jend"
  return ${retval}
}

jend(){ _jend $?; } # beendet einen Vorgang mit stderr-auswertung

jwend()# original by Gentoo Foundation modded by Psyjo
{
  local retval="${1:-0}"
  shift
  _end "${retval}" jwarn "$*"
  LAST_CMD="jwend"
  return ${retval}
}

############  selftest ####
tt()
{
  for Tool in `echo $* | tr "," "\n"`; do
    if ! which "${Tool}" &> /dev/null
      then
        jwarn "${BAD} tt: Tool \"${Tool}\" nicht gefunden !${NORMAL}"
        _TT_ERROR=1
    fi
  done
  return ${_TT_ERROR}
}

# sicherstellen das FreeBSD GNU Getopt benutzt
[[ "$(uname -s)" == "FreeBSD" ]] && getopt() { /usr/local/bin/getopt "$@"; }

[[ "$1" == "selftest" ]]&&{
  which echo &> /dev/null || jexit "error loading PsyTools (cannot find echo)"
  which tr   &> /dev/null || jexit "error loading PsyTools (cannot find tr)"
  [[ "$(getopt 2> /dev/null)" == " --" ]] && jexit "error loading PsyTools (cannot find GNU getopt)"
  tt cat,tail,head,stty,grep,sed,rm,wc,cp,chmod,date,printf || jexit "unable to locate neccesary files, exit"
}
############  /selftest ####

tab() { echo -en "\t"; }
warnsig() { echo -e "${BRACKET}[ ${BAD}!!${BRACKET} ]${NORMAL}"; }
kaysig() { echo -e "${BRACKET}[ ${GOOD}OK${BRACKET} ]${NORMAL}"; }

jgetline() # <int> <file/vari>
{
[[ ! `echo $1 | sed 's/^[^0-9]*$//g'` ]] && jerror "Zielennummer muss ${BAD}integer${NORMAL} sein" && return 1
  if [[ -r $2 ]];then
    sed -n "$1p" $2
  else
    echo -e "$2" | sed "$2p" || echo -e "${BAD}jgetline: fixme!${NORMAL}"
  fi
unset FILE
}

fex() # <file> <comment>   # fehler wenn datei nicht vorhanden
{
if [[ ! -e $1 ]]
  then
    jerror "$2 Datei $1 existiert nicht!"
    return 1
  else
    return 0
fi
}
xor() # return 0 wenn 1 parameter uebergeben wird z.B. <leer> <!leer> <leer>
{
  if [ $# -eq 1 ]
    then return 0;else return 1;
  fi
}
xnor() # return 0 wenn nicht 1 parameter uebergeben wird z.B. <leer> <!leer> <!leer>
{
  if [ $# -ne 1 ]
    then return 0;else return 1;
  fi
}

getcols() # Shellbreite in $COLS; Escapesequenz ENDLN (an zeilenende -8 springen) 
{
COLS="${COLUMNS:-0}"		# bash's internal COLUMNS variable
(( COLS == 0 )) && COLS="$(set -- `stty size 2>/dev/null` ; echo "$2")"
(( COLS > 0 )) || (( COLS = 80 ))	# width of [ ok ] == 7

ENDLN=$'\e[A\e['$(( COLS - 8 ))'C'
ENDLNs=$'\e[A\e['80'C'
}
getcols

###################################################
# needed for deprecated jtestpara
_jtestpara_list() # private
{
  JTestparameter=`echo "$1" | sed 's/^-//'`                                             #
  JTestparaAmount=`echo "${JTestparameter}" | wc -c`                                    #
  JTestparaCount=1                                                                      #
  while [ ${JTestparaCount} -lt ${JTestparaAmount} ]; do                # ...  listen           #
    JTestparaTmp=`echo "${JTestparameter}" | head -c ${JTestparaCount} | tail --bytes=1`        #  parameter vereinzeln 
    JTestparameterListed=`echo -e "${JTestparameterListed} -${JTestparaTmp}"`           #
    let JTestparaCount++                                             #
  done
} 

_jtestpara_split() # private
{       
  unset JTestparaTmp JTestparameter JTestparaTmp JTestparaItem JTestparaCount JTestparaAmount
  for JTestparaItem
  do
  if [[ `echo ${JTestparaItem} | grep ^-` ]]
  then
    if [[ `echo ${JTestparaItem} | grep ^--` ]]
    then
      [[ `echo ${JTestparaItem}` == "--" ]] && { JTestparameterListed=`echo -e $JTestparameterListed $@`; break; }
      JTestparameterListed=`echo -e "$JTestparameterListed ${JTestparaItem}"`
    else
      _jtestpara_list "${JTestparaItem}"
    fi
  else
    JTestparameterListed=`echo -e "$JTestparameterListed \"${JTestparaItem}\""`
  fi
  shift
  done
}

########################################
#####   deprecated - use getArgs insted
jtestpara() # <file> <"$@">  addinfo in script 
{
local JTestparameterListed JTestParaResults JTestParaResultsLine  OLD_IFS
# erwartete Notation(kommentiert notieren!):
#:begin_jpara
# <eingabe> [| <eingabe>]... : <variable> # <info>
# ...
# ex: 
#-v | --verbose : VERBOSE # auskunftsfreudig
#:end_jpara
  fex ${1} "jtestpara:" || return 1
  jextract jpara ${1}
  [[ ! ${JExtracted} ]] && jerror "${BAD}nichts extrahiert!${NORMAL}"
  shift

# extrahierte elemente fuer case zuschneiden
# #-v | --verbose       :       VERBOSE #       auskunftsfreudig
# zu
#-v|--verbose)[[ ! `printf %s "$2" | grep ^-` ]]&&[[ $# > 1 ]]&&shift;echo "VERBOSE=\"$1\"";;

  JExtracted="`echo -e "${JExtracted}" |\
               cut -d "#" -f 1 | tr -d "\t" | tr -d " " |\
               sed -e 's/:/)[[ ! \`printf %s \"$2\" | grep ^-\` ]]\&\&[[ $# > 1 ]]\&\&shift;echo \"/'      -e 's/$/=\\\\\"\$1\\\\\"\";;/';`"

# geklumpte parameter als einzelne splitten
  _jtestpara_split "$@"  #  hier wird $TestparameterListed gesetzt
# eingegebene Parameter die jrun nutzen soll
  JRUN_PARAMETER=$JTestparameterListed

#den ganzen gelump in einer subshell ausfuehren und die ergebnisse in einer variablen speichern
  JTestParaResults=$(jrun "while [[ \$#  -gt 0 ]]
			   do
			     case \${1} in
			     ${JExtracted}
			     --) break;;
			     *) echo \"JParaErrorUnknownArgument \${1}\";;
			     esac;
			   shift
			   done")

#die ergebnisse auswerten uns anwenden
  OLD_IFS=${IFS}
  IFS=$'\012'
  for JTestParaResultsLine in `echo -e "$JTestParaResults"`
  do
    [[ `printf "%s" "${JTestParaResultsLine}" | grep JParaErrorUnknownArgument` ]] &&
    {
      echo "${BAD}ungueltiges Argument - `printf "%s" "${JTestParaResultsLine}"|cut -d " " -f 2`${NORMAL}"
      Jtestpara_Error=1
      continue
    }
    eval ${JTestParaResultsLine}
  done
  IFS=${OLD_IFS}

return ${Jtestpara_Error}
}

getArgs() # file "$@"
{
local ArgLine Args Longargs Opts Error Default Var Opt

Name=$1
jextract args $1
shift

for ArgLine in $(printf "%s" "${JExtracted}" | cut -d : -f 1 | tr "|" "\n")
do
        if [[ $(printf "%s" "${ArgLine}" | grep -o ^--) ]]
        then
                Longargs="${Longargs},$(printf "%s" "${ArgLine}" | sed 's/^--//' | tr "+" ":")"
        else
                Args="${Args}$(printf "%s" "${ArgLine}" | sed 's/^-//' | tr "+" ":" )"
        fi
done

Opts=$(getopt -n getArgs -o "${Args}" -l "${Longargs}" -- "$@")
Error=$?

set -- $Opts

while [[ $# > 0 ]]
do
#	printf "%s\n" "$*"
	[[ "$1" == "--" ]] && break

	Var="$(printf "%s" "${JExtracted}"  | sed 's/^/|/;s/ *//g' | grep -- "|$1" | cut -d : -f 2 | cut -d "#" -f 1 )"
	Default=$(printf "%s" "${Var}" | cut -d "=" -f 2)
	Var=$(printf "%s" "${Var}" | cut -d "=" -f 1)

        if [[ $(printf "%s" "$2" | grep "'") ]]
        then
		shift # shift Var away
#		printf "\$1 = %s\n" "$1"
		if [[ "$1" != "''" ]]
		then
			Opt=""
			while [[ ! $(printf "%s" "${Opt}" | egrep -o "'$") ]]
			do
#				echo -- "loop: $1"
				Opt="${Opt} $1"
				shift
			done
		else 
			Opt=""
			shift
		fi
		Opt=$(printf "%s" "${Opt}" | sed 's/^ *//g')
#	        printf "===\n${Var}=${Opt:=${Default}}\nDefault = ${Default}\n===\n"
                eval "${Var}=${Opt:=${Default}}"
        else
#                echo "${Var}=$1"
                eval "${Var}=$1"
		shift
        fi

done

unset JExtracted
return ${Error}
}

jextract() # <keyword> <file> [-print]  addinfo in script
{
# erwartete Notation(kommentiert notieren!):
#:begin_<keyword>
# ...<whatever>...
#:end_<keyword>
unset JExtracted
local ExtractFile
#local JExtractTMP
#local JExtractCapture
local ExtractKeyword
local JExtractPrint
#local OLD_IFS

  ExtractKeyword=$1
  shift
  ExtractFile=${1}
  fex ${ExtractFile} "jextract:" || return 1
  shift
  [[ "${1}" == "-print" ]] && JExtractPrint=1
  shift
  [[ $* ]] && jerror "jextract: zu viele Parameter!" && return 1

#  OLD_IFS=${IFS}
#  IFS=$'\n'
#  for JExtractTMP in `cat ${ExtractFile} | grep ^#`
#  do
#    [[ "${JExtractTMP}" == "#:end_${ExtractKeyword}" ]] && unset JExtractCapture
#    [[  ${JExtractCapture} ]]&& { JExtractTMP=`echo "$JExtractTMP" | sed 's/^#*//'`;JExtracted=`echo "${JExtracted}\n${JExtractTMP}"`; }
#    [[ "${JExtractTMP}" == "#:begin_${ExtractKeyword}" ]] && JExtractCapture="1"
#  done
#  IFS=${OLD_IFS}

JExtracted="$(sed -n "/^#:begin_${ExtractKeyword}/,/^#:end_${ExtractKeyword}/p" ${ExtractFile})"
JExtracted=$(echo "${JExtracted}" | sed '$d;1d')	# delete first and last line
JExtracted=$(echo "${JExtracted}" | sed 's/^#//')	# and remove the leading '#'

  if [ ${JExtractPrint} ]
  then
    echo "${JExtracted}"
    unset JExtracted
  else
    export JExtracted
  fi
}

get_ver()  #<file> [<file>]... - extrahiert dateinamen und version notation : #!begin_version\n#<datei-version>\n#!end_version
{
local FillLen File Flist
 
  FillLen=$(longest_string $(
    for File in $*
    do
      [[ -f ${File} ]] && basename ${File}
    done
  ))
  Flist=$(
    for File in $*
    do
      [[ -f ${File} ]] && echo ${File}
    done
  )

  for File in ${Flist}
  do
      jextract version ${File}
      [[ ${JExtracted} ]] &&{		# ignore files with no version
        printf "%-${FillLen}s: %s\n" "$(basename ${File})" "${JExtracted}"
      }
      unset JExtracted
  done
}

jrun() #<cmd[/s]> fuehrt $* aus einer subshell aus | Parameter fuer die tmpfkt in JRUN_PARAMETER angeben !
{
  [[  ${Jrun_Debug} ]] &&
  {
    jline		1>&2 
    echo "  Debug_jrun"	1>&2 
    jline		1>&2 
    echo -e "\nParameter: $JRUN_PARAMETER\n" 1>&2 
    echo -e "tmpfunc()\n{\n$*\nreturn \$?\n}\ntmpfunc ${JRUN_PARAMETER}\n" 1>&2 
    jline 		1>&2 
    echo "  /Debug_jrun"1>&2
    jline 		1>&2 
    read
  }
  echo -e "tmpfunc()\n{\n$*\nreturn \$?\n}\ntmpfunc ${JRUN_PARAMETER}" | bash
  return $?
}

juninstall() # <datei1> [<datei2> ...]
{
  for juninstall_item in $*
  do
    jbegin "loesche ${juninstall_item}"
      rm ${juninstall_item}
    jend
  done
unset juninstall_item
}

_get_version_strings() # private
{
unset jinstall_update
jextract version `echo ${1} | sed 's/.*\///'` && jinstall_installed_ver=${JExtracted}
if [ ! -e ${1} ]
then
  unset jinstall_local_ver
else
  jextract version     ${1}                   && jinstall_local_ver=${JExtracted}
  jinstall_update=1
fi
}

_jinstall_do() # private
{
  if [ ${jinstall_update} ]
  then
    jbegin "update ${1}   ${jinstall_local_ver} -> ${jinstall_installed_ver} "
  else
    jbegin "installiere $1 ${jinstall_installed_ver}"
  fi
  cp $2 $3
  jend
}

_jinstall_inf() # private
{
  if [ $FORCE ]
  then
    jwarn "${1}   ${jinstall_local_ver} ueberschreiben mit ${jinstall_installed_ver}"
    cp $2 $3
    jend
  else
    jwarn "$1 ${jinstall_local_ver} bereits aktuell"
  fi
}

jinstall() # <Anzeigename> <QuellDatei> <InstallationsDatei>  // FORCE erzwingt dasueberschreiben
{
  _get_version_strings "$3"
  jinstall_destination=`echo $3 | grep -o '^.*/'` # Zielpfad ermitteln
  if [[ ${jinstall_installed_ver} > ${jinstall_local_ver} ]]
  then
    _jinstall_do $1 $2 ${jinstall_destination}
  else
    _jinstall_inf $1 $2 ${jinstall_destination}
  fi
  chmod 644 $3
unset jinstall_update jinstall_installed_ver jinstall_local_ver jinstall_destination
}

jset_time() # <name> setzt die zeit in einer variablen + den bezeichner
{
  eval "JTime_$1=`date +%s`"
}

jget_time() # <name> holt die zeit aus der variablen + den bezeichner
{
  date -u -d @$(( `date +%s` - `eval echo  \$\{JTime_$1\}` )) +%T
}

_jdo()
{
local TmpVerbose
  JdoError=0
  [[ $# < 1 ]] && { jerror "_jdo: zu wenige Parameter angegeben!"; return 1; }
  jrun "$*"
#  { $* ; }  # better ?
#  ( $* )  # better ?
  if [[ $? -eq 0 ]] ; then JdoError=0; else JdoError=1; fi

  [[ ${VERBOSE} ]] && TmpVerbose=${VERBOSE}
  unset VERBOSE

  _jend ${JdoError}

  [[ ${TmpVerbose} ]] && VERBOSE=${TmpVerbose}
  unset TmpVerbose
  return ${JdoError}
}

jdo() # <bezeichner> <2do>
{
  jbegin "$1"
  shift
  _jdo "$*"
}

jido() # <bezeichner> <2do>
{
  jinfo "$1"
  shift
  _jdo "$*"
}

jldo () # <bezeichner> <2do> # verbose if VERBOSE!=""
{
  inline "$1"
  shift
  _jdo "$*"
}

humanreadable() # <int[Ext][,int[Ext]...]>
{
	local Value Ext InExt Cnt
	while [[ $# -gt 0 ]]
	do
		Value=$1
		InExt=$(echo ${Value} | tr -d "[0-9]*")
		Value=$(echo ${Value} | tr -d "[BKMGTPEZYbkmgtpezy]*")
		InExt=$(echo ${InExt} | sed 'y/kmgtpezy/KMGTPEZY/') # uppercase input
		[[ ! ${InExt} ]] && InExt="B"

		for Ext in B K M G T P E Z Y
		do
			[[ "${Ext}" == "${InExt}" ]] && break
			let Cnt++
		done

		for Ext in B K M G T P E Z Y
		do
			[[ ${Cnt} -gt 0 ]] && { let Cnt--; continue; }
			if [[ $(echo ${Value} | awk -F. '{print $1}') -lt 1024 ]]
			then
				break 1
			else
#				let 'Value/=1024'
				Value=$(echo "scale=3; ${Value} / 1024" | bc -l)
			fi
		done
		echo "${Value}${Ext}"
		shift
	done
}

revhumanreadable() # <size[Ext] [-o <OExt>] [size[Ext] [-o OExt]]>
{
	local Value Ext InExt Trgr OExt
	while [[ $# -gt 0 ]]
	do
		unset Trgr
		Value=$1
		[[ "$2" == "-o" ]] && { OExt=$3; shift 2; }
		InExt=$(echo ${Value} | tr -d "[0-9]*")
		InExt=$(echo ${InExt} | sed 'y/bkmgtpezy/BKMGTPEZY/') # uppercase input
		OExt=$(echo ${OExt} | sed 'y/bkmgtpezy/BKMGTPEZY/') # uppercase output
		Value=$(echo ${Value} | tr -d "[BKMGTPEZYbkmgtpezy]*")
		
		[[ ! ${InExt} ]] && InExt="B"
		[[ ! ${OExt} ]] && OExt="B"

		for Ext in Y Z E P T G M K B
		do
			[[ ${Trgr} ]] && {
				let 'Value*=1024'
			}
			[[ ${InExt} == ${Ext} ]] && Trgr=1
			[[ ${Ext} == ${OExt} ]] && break
		done
		echo "${Value}${Ext}"
		shift
	done
}

genarghelp() # <File to extract from> # generate HelpText from Argumentdeclaration (jtestpara)
{
  local OLD_IFS Len1 FillLen
  jextract "args" $1
  [[ ! "${JExtracted}" ]] && jextract "jpara" $1

  OLD_IFS=${IFS}
  IFS=$'\012'

  FillLen=$(longest_string $(echo -e "${JExtracted}" | cut -d : -f 1 | tr -d " " | tr -d "\t" | sed 's/|/  /g'))

  for Line in ${JExtracted}
  do
    printf "%-${FillLen}s " "$(echo ${Line} | cut -d : -f 1 | tr -d " " | tr -d "\t" | sed 's/|/, /g')"
    if [[ $(echo ${Line} | grep "#") ]]	##
    then				#
      echo ${Line} | cut -d "#" -f 2	# print info if available
    else				#
      echo				#
    fi					##
  done					#

  IFS=${OLD_IFS}
}

longest_string()
{
  local TmpLineLen MaxLen
  while [ $# -gt 0 ]
  do
    TmpLineLen=$(echo $1 | wc -c)
    [[ ${TmpLineLen} -gt ${MaxLen} ]] && MaxLen=${TmpLineLen}
    shift
  done
  echo $(( ${MaxLen} - 1 ))
}

sec2hms(){
local Itm h m s
for Itm in $*
do
	h=$(echo "${Itm} / 3600" | bc )
	m=$(echo "( ${Itm} - $h * 3600 ) / 60" | bc )
	s=$(echo "( ${Itm} - $h * 3600 - $m * 60 )" | bc )
	echo "$h h, $m m, $s s."
done
}

doCmd()
{
if [[ $Dbg ]]
then    echo "Debug: $*"
else    eval "$*"
fi
}
