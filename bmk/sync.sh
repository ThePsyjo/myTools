#!/bin/bash
#:begin_version
#1.3
#:end_version
#:begin_args
# -w | --web	 : WEB		# webupdate
# -l | --local	 : LOCAL	# nur lokal kopieren
# -v | --verbose : VERBOSE	# mehr Ausgaben
# -i | --install : Install	# bmk installieren
# -h | --help	: Help # diese Hilfe anzeigen
#:end_args
Src="http://github.com/ThePsyjo/myTools/raw/master"
. /usr/lib/psytools.sh || . psytools.sh || {
	echo "kann psytools nicht finden - lade herunter..."
	wget ${Src}/psytools.sh -O ./psytools.sh && . psytools.sh || { echo "herunterladen von psytools.sh fehlgeschlagen - breche ab"; exit; }
}
getArgs $0 "$@"
[[ ${Help} ]] && { genarghelp $0 ; exit ; }
[[ ! ${VERBOSE} ]] && OPTS="-q"
[[ ${WEB} ]]&&{
  jbegin "Daten herunterladen"
    for File in bmk.sh bmk_functions.sh install.sh bmk.conf.example userfuncts.sh.vanilla
    do
	    wget ${OPTS} ${Src}/bmk/${File} -O ./${File}
    done
  jend
    [[ ${UID} == 0 ]] && [[ ${Install} ]] && {
    chmod +x install.sh
    jinfo "install..."
    ./install.sh
    }
}

[[ ${LOCAL} ]]&&{
jbegin "Daten kopieren"
  cp ${VERBOSE} /usr/lib/psytools.sh ./
  cp ${VERBOSE} /usr/bin/bmk.sh ./
  cp ${VERBOSE} /usr/lib/bmk_functions.sh ./
jend
}
