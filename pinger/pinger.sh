#!/bin/bash
# Copyright 2006-2008 Psyjo®
# Distributed under the terms of the GNU General Public License v2
#:begin_version
#Version 1.4.5-3
#:end_version
#:begin_args
#-i+ | --interval+:	INTERVAL
#-h | --help:		HELP
#-d+ | --destination+:	ADD
#-r+ | --runs+:		RUNS
#-l++ | --log++:	LOG=pinger_defaut.log
#-n | --nocolor:	NOCOLOR
#-z++ | --zeige_vor++:	RECENT=5
#-q | --quiet:		QUIET
#-s | --show_session:	SESSIONID
#-a | --arpcheck:	ARPCHECK
#-V | --version:	Version
#-D | --deleteoldlog:	Rmtemp
#-L | --listoldlog:	Listlog
#:end_args
PingerWorkdir=`dirname $0`
source /usr/lib/psytools.sh selftest # req.:psytools-1.2.3
tt ping,sleep,tee,tr,sed,dirname || exit

[[ "$(get_ver /usr/lib/psytools.sh | cut -d " " -f 3)" < "1.2.7" ]] && { jerror "$(get_ver /usr/lib/psytools.sh) too old to use this script."; jexit "update at least to Version 1.2.7"; }
if [[ ! $* ]]
then HELP=help
else getArgs $0 "$@" || HELP=help
fi

#cd `dirname $0`
[[ ${Version} ]] && { get_ver $0 /usr/lib/psytools.sh; exit; }
[[ ${Listlog} ]] && { ls -l ${PingerWorkdir}/*[0-9]*.log; exit; }
[[ ${Rmtemp} ]]  && { rm -v ${PingerWorkdir}/*[0-9]*.log; exit; }

if [[ ! ${HELP} ]]
then
  [[ ${NOCOLOR} ]] && unset GOOD BAD NORMAL HIBLUE WARN BLUE BRACKET
  [[ "${ADD}" == "-d" ]] || [[ "${ADD}" == "--destination" ]] || [[ ! ${ADD} ]] && { jwarn "Ziel vergessen ?    ${ADD}"; HELP=help; }
  [[ "${INTERVAL}" == "-i" ]] || [[ "${INTERVAL}" == "--interval" ]] 		&& { jwarn "${INTERVAL}: Interval vergessen ?"; HELP=help; }
  [[ "${RUNS}" == "-r" ]] || [[ "${RUNS}" == "--runs" ]] 			&& { jwarn "${RUNS}: numerische Eingabe erforderlich"; HELP=help; }
  [[ ${ARPCHECK} ]]								&& { tt arp,arping || HELP=help; } 
  [[ ${QUIET} ]] && [[ ! ${LOG} ]]						&& { jwarn "${QUIET}: Kein Log zum speichern angegeben."; HELP=help; }
  [[ ${RECENT} ]] && [[ ! ${LOG} ]] 						&& { LOG="${PingerWorkdir}/pinger_${ADD}_$$.log"; echo > ${LOG}; }
  [[ "${LOG}" == "-l" ]] || [[ "${LOG}" == "--log" ]] 				&& LOG="${PingerWorkdir}/pinger_${ADD}.log"
  #[[ ${RECENT} ]] && [[ ! ${LOG} ]] 						&& { LOG="pinger_${ADD}_$$.log"; echo > ${LOG}; }
  #[[ "${LOG}" == "-l" ]] || [[ "${LOG}" == "--log" ]] 				&& LOG="pinger_${ADD}.log"
  [[ "${RECENT}" == "-z" ]] || [[ "${RECENT}" == "--zeige_vor" ]] 		&& RECENT=5
  [[ "${SESSIONID}" == "-s" ]] || [[ "${SESSIONID}" == "--show_session" ]]	&& SESSIONID="${BLUE}$$${NORMAL} - "
  [[ ! $INTERVAL ]] 								&& INTERVAL=60s
  [[ ! ${RUNS} ]]   								&& RUNS=0
else
  echo -e "Pinger $(jextract version $0 -print)\n$(jgetline 2 $0 | sed 's/^ *# *//g' )"
fi

[[ $HELP ]] && {
  jline
  echo -e "\nVerwendung : $0 -d <IP-Addresse/Name[,...]> [-i <interval(s,m,h...)>] [-r <runs>] [-l [<logfile>] [-q]] [-z [<zeilen>]] [-n] [-s] [-a]."
  jline x
  echo -e "  -d, --destination\tZielrechner"
  echo -e "  -a, --arpcheck\tARP pruefen"
  echo -e "  -i, --interval\tInterval"
  echo -e "  -r, --runs\t\tAnzahl der Laeufe"
  echo -e "  -l, --log\t\tsitzung loggen"
  echo -e "  -n, --nocolor\t\tkeine Farben anzeigen"
  echo -e "  -z, --zeige_vor\tZeige vorherige Durchlaeufe an"
  echo -e "  -s, --show_session\tZeige SessionID an"
  echo -e "  -q, --quiet\t\tkeine Ausgaben anzeigen"
  jline
  echo -e "  -D, --deleteoldlog\tloescht alte Logfiles"
  echo -e "  -L, --listoldlog\talte temporaere Logfiles anzeigen"
  echo -e "  -h, --help\t\tzeigt diese Hilfe"
  echo -e "  -V, --version\t\tVersion anzeigen"
  jline
  exit
}

arpcheck()
{
  [[ ${ARPCHECK} ]] && {
    echo -n " arpcheck: "
    arp -d ${TMPADD} &> /dev/null
    arping -c 1 ${TMPADD} &> /dev/null
    if [[ `arp -a | grep ${TMPADD} | grep ..:..:..:..:..:..` ]]; then kaysig; else warnsig; fi
  }; test
}

startmsg() { echo -e "\t####################\n\t[`date +%F_%X`]  Pinger `jgetline 5 $0 | sed 's/^ *#* *//'` started\n\tHost/s: ${ADD}\n\t${ARPCHECK} ${QUIET}"; }

startmsg >> ${PingerWorkdir}/pinger_all.log

[[ ${LOG} ]] && {
  startmsg >> ${LOG}
  echo -e "\tLogfile: ${LOG}\n" >> ${PingerWorkdir}/pinger_all.log
}

#count:schleifenzaehler;av:available;nav:not_available
COUNT=0;AV=0;NAV=0
jset_time $$

while : ; do
  COUNT=$(($COUNT+1))
  [[ ! ${QUIET} ]] && echo -e "\n Versuch $COUNT...\n"

  for TMPADD in `echo ${ADD} | tr "," "\n"`; do

    ACHECK="`arpcheck`"
    AMSG="${GOOD}Host $TMPADD erreichbar.${NORMAL}${ACHECK}"
    NAMSG="${BAD}Host $TMPADD nicht erreichbar.${NORMAL}${ACHECK}"

    ping -c 3 ${TMPADD} >> /dev/null

    if [[ $? == 0 ]]
    then
      AV=$(($AV+1));   [[ ! ${QUIET} ]]&&{  echo -e ${AMSG}; };MSG=${AMSG}
    else
      NAV=$(($NAV+1)); [[ ! ${QUIET} ]]&&{  echo -e ${NAMSG};};MSG=${NAMSG}
    fi

    [[ ${LOG} ]] && echo -e "${SESSIONID}${HIBLUE}`date +%F_%X`${WARN} - `jget_time $$` - ${NORMAL} -> ${MSG}" >> ${LOG}
  done

  clear

  [[ ! ${QUIET} ]] && {
    [[ ${RECENT} ]] && { tail ${LOG} -n ${RECENT}; }
	    echo -e "(${GOOD} ${AV} ${NORMAL})(${BAD} ${NAV} ${NORMAL})"
  }
  [[ ${RUNS} != 0 ]] && { [[ ${COUNT} = ${RUNS} ]] && break; }
  sleep $INTERVAL
done
#[[ -e tmp.log ]] && rm tmp.log
echo "Gesamtlaufzeit: `jget_time $$`"

