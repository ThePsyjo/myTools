#!/bin/bash
#:begin_version
#1.2-1
#:end_version
 [[ ! -e psytools.sh ]] && echo -e "\tkonnte psytools nicht finden!\n" && exit
   source psytools.sh || exit
 [[ $UID != 0 ]] && jerror -e "\n$BAD\tNur root kann das Script benutzen!$NORMAL\n" && exit
 [[ ! -r /etc/gentoo-release ]] && jerror -e "\n$BAD\tNur f�r Gentoo geeignet!$NORMAL\n" && exit
 [[ ! -r bmk_functions.sh ]] && jerror -e "\n$BAD\tbmk_functions.sh f�r Installation ben�tigt!$NORMAL\n" && exit
 [[ ! -r bmk.sh ]] && jerror -e "\n$BAD\tbmk.sh f�r Installation ben�tigt!$NORMAL\n" && exit
# [[ ! -r bmk.conf ]] && jerror -e "\n$BAD\tbmk.conf f�r Installation ben�tigt!$NORMAL\n" && exit

#:begin_args
# -f | --force : FORCE # force install
# -c | --conf : CONF # install config
# -jrd : Jrun_Debug # debug output
# -v : VERBOSE # run verbose
# -u | --uninstall : UNINST # uninstall bmk
# -h | --help : Help # show this
#:end_args

getArgs $0 "$@"

[[ ${Help} ]] && { genarghelp $0; exit; }

if [[ $UNINST ]]
then
  juninstall /usr/bin/bmk.sh /usr/bin/bmk /usr/lib/bmk_functions.sh /etc/bmk.conf
else
  jinstall PsyTools psytools.sh /usr/lib/psytools.sh
  jinstall Funktionen bmk_functions.sh /usr/lib/bmk_functions.sh
  jinstall bmk bmk.sh /usr/bin/bmk.sh
fi

[[ ${CONF} ]]||[[ ! -r /etc/bmk.conf ]]&&{
  jinfo "Config"
    [[ -r /etc/bmk.conf ]] && jwarn "lokale bmk.conf �berschreiben ?"
    cp -i bmk.conf.example /etc/bmk.conf
  jend
}

if [[ $UNINST ]]
then
  echo -e "UnInstallation beendet.\n"
else
  jbegin "User-Funktionen"
    [[ ! -d ~/.bmk ]] && mkdir ~/.bmk
      cp userfuncts.sh.vanilla ~/.bmk/ && jinfo "userfuncts.sh.vanilla copied to ~/.bmk/; you may want to edit it"
  jend

  chmod +x /usr/bin/bmk.sh
  ln -sf /usr/bin/bmk.sh /usr/bin/bmk

  echo -e "Installation beendet.\n"
fi

