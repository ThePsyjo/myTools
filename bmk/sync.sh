#!/bin/bash
#:begin_version
#1.2.1
#:end_version
#:begin_jpara
# -w | --web	:WEB	# webupdate
# -l | --local	:LOCAL	# nur lokal kopieren
# -v | --verbose:VERBOSE
# -i | --install:Install
#:end_jpara
UHOST=psyjo.terranet.org
source /usr/lib/psytools.sh
jtestpara $0 "$@"
[[ ! ${VERBOSE} ]] && OPTS="-q"
[[ ${WEB} ]]&&{
  wget ${OPTS} http://$UHOST/Files/Bash/psytools.sh -O ./psytools.sh
  source psytools.sh
  jbegin "Daten herunterladen"
    for File in bmk.sh bmk_functions.sh install.sh bmk.conf.example userfuncts.sh.vanilla
    do
	    wget ${OPTS} http://$UHOST/Files/Bash/bmk/${File} -O ./${File}
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
