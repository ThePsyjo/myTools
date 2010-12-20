# Copyright 2006 Psyjo©
# Distributed under the terms of the GNU General Public License v3
#:begin_version
#Version 1.2.5-1
#:end_version

#:begin_jpara
#--help | -h		:	HELP
#-k | --kinstall	:	INSTALL
#-M | --Modinstall	:	MODINSTALL
#-f | --force		:	FORCE
#-C | --CLEAN		:	CLEAN
#-L | --link		:	LINK
#-m | --menu		:	MENU
#-b | --build		:	BUILD
#-c | --confcopy	:	CONF
#-g | --graphic		:	VGA
#-o | --ohne		:	NODRV
#-O | --wirklichohne	:	NODRV_MORE
#-r | --ram		:	RAM
#-v | --verbose		:	VERBOSE
#-V | --version		:	VERSION
#--s1			:	SPEZIAL1
#--s2			:	SPEZIAL2
#--s3			:	SPEZIAL3
#--s4			:	SPEZIAL4
#--s5			:	SPEZIAL5
#:end_jpara

unset HELP INSTALL FORCE CLEAN LINK MENU BUILD CONF VGA NODRV NODRV_MORE RAM VERBOSE VERSION SPEZIAL1 SPEZIAL2 SPEZIAL3 SPEZIAL4 SPEZIAL5

menu() { inline "Menü bauen"; make -s $OPTS  menuconfig; jend; } #irgendwie klar
by()   { echo -e "BMK - BuildMyKernel by Psyjo"; }
force(){ echo -e "\n=== Erneuerung der Module und Treiber erzwungen ===\n"; }
verset(){ [[ -f $IMGPATH ]] && VER=`ls -l $IMGPATH`; }
userfunct(){ [[ $USERFUNCT ]] && _userfunct $1; }

_help()
{
  [[ "$1" == "by" ]] && by
  echo -e "\nverwendung : $0 PARAMETER1 PARAMETER2 ...\n"
  echo -e "\t-b, --build\t\tKernel bauen"
  echo -e "\t-M, --Modinstall\tModule installieren (+[-f] neu bauen)"
  echo -e "\t-v, --verbose\t\talle Ausgaben anzeigen"
  echo -e "\t-r, --ram\t\tKernel in einem Ramdrive bauen (nur bei Neubau empfohlen)"
  echo -e "\t-f, --force\t\terneuerung der Module und Treiber erzwingen"
  echo -e "\t-C, --CLEAN\t\tkompletter Kernel-Neubau (clean)"
  echo -e "\t-k, --kinstall\t\tnur bzImage kopieren"
  echo -e "\t-g, --graphic\t\tnur den Grafiktreiber erneuern"
  echo -e "\t-L, --link\t\taktuellste Kernelquellen verlinken"
  echo -e "\t-m, --menu\t\tMenuconfig"
  echo -e "\t-c, --confcopy\t\t.config zu den neuen Quellen kopieren\n\t\t\t\t (nur in Kombination mit -L)"
  echo -e "\t-o, --ohne\t\tzusätzliche Treiber NICHT mit erstellen [!ACHTUNG!]"
  echo -e "\t-O, --wirklichohne\taußschließlich bzImage erstellen [!ACHTUNG!]"
  echo -e "\t--s1 - --s5\t\tSpezialparameter"
  echo -e "\t-h, --help\t\tdiese Hilfe anzeigen"
  echo -e "\t-V, --version\t\tVersion anzeigen"
  echo 
[[ $USERFUNCT ]] && userhelp && echo
exit
}

kinstall_intern()
{
  if [[ -z `mount | grep "/boot type"` ]];then
    mount -v /boot
    MOUNTED=1
  fi

  cp -v $IMGPATH /boot/
  [[ -e /sbin/lilo ]] && lilo

  [[ $MOUNTED ]] && umount -v /boot
}

klink()  # verlinkt den letzten String (größter) nach linux
{
  cd ../
  [[ $CONF ]] && cp $LINPATH/.config ./
  FILE=$(ls -dx1 /usr/src/* | grep "$(ls -dx1 /usr/src/*  | sed -n 's/.*-\(2\.6\.[0-9]*\)-.*-r\([0-9]*\)/\1.\2/p' | sort  -n | sed -n '$s/\(2\.6\.[0-9]*\)\.\([0-9]*\)/\.*\1\.*\2/p')")

  inline "$GOOD$LINPATH -> $FILE$NORMAL"
    rm ${LINPATH}
    ln -s $FILE $LINPATH
  jend

  if [ $CONF ];then
    inline "$.conf -> $FILE/.conf"
      mv ./.config $LINPATH/
    jend
  fi

  cd $LINPATH || exit
  make oldconfig
}

graphic()
{
  if [ -n $GRAFIKTREIBER ];then
    inline "Grafiktreiber erneuern"
     still "${PkgMgr} $GRAFIKTREIBER"
    jend
  fi
}

mkramdrv()
{
  mkdir /usr/src/ram/
  mount -v -t ramfs none /usr/src/ram/
 jbegin "\tDaten in Ramdrive kopieren"
  cd $LINPATH
  cp -arf ./ /usr/src/ram/
 jend
  cd /usr/src/ram/
}

rmramdrv()
{
 jbegin "\tDaten nach ../linux/ kopieren"
  cd /usr/src/ram/
  cp -arf ./ $LINPATH/
 jend
  cd $LINPATH
  umount -v /usr/src/ram/
  rm -r /usr/src/ram/
}

show_version()
{
  get_ver /usr/bin/bmk.sh /usr/lib/bmk_functions.sh /usr/lib/psytools.sh
  exit
}

#==============================^INTERN^==========================================
#==============================vEXTERNv==========================================

pretest2()
{
  [[ -z $* ]] && HELP=1       # wenn kein Parameter dann Hilfe

  jtestpara /usr/lib/bmk_functions.sh "$@"
  if [[ $? != 0 ]]; then HELP=1; fi

  if [ -z $HELP ];then  #######################################
#Parameterkombinationen prüfen; evtl noch setzen oder hilfe
    if [ $FORCE ] && [ $VGA ]; then HELP=1; echo -e "\n$BAD\tEntweder -g oder -f !$NORMAL"; fi  # -g -f  aussortieren
    if [ $CONF ] && [ -z $LINK ]; then HELP=1; echo -e "\n$BAD\tnur in Kombination mit -L möglic (-L -c)$NORMAL"; fi
    if [ $LINK ]; then
      if [ $INSTALL ]; then HELP=1; fi                 # -L -k aussortieren
    fi
    if [ -z $BUILD ];then
      if [ $CLEAN ]; then echo -e "\n$BAD\tnur in Kombination mit -b möglich (-b -F)$NORMAL"; HELP=1; fi
      if [ $RAM ]; then   echo -e "\n$BAD\tnur in Kombination mit -b möglich (-b -r)$NORMAL"; HELP=1; fi
    fi

  fi # if [ -z $HELP ]  #######################################

}

prebegin()
{
  [[ $VERSION ]] && { show_version; exit; }
  [[ ${HELP} ]]&&[[ "$HELP" != "1" ]] && { _help "by"; exit; }
}

testlink()
{
  if [ -L $LINPATH ];then
  LINKDEST=`ls -l $LINPATH | rev | cut -d " " -f 1 | rev`
  fi
  
  jbegin "Link prüfen"
  if [[ -L $LINPATH ]] && [[ -n `ls -dx1 $LINPATH* | grep $LINKDEST` ]];then
    echo -e "$LINPATH -> $LINKDEST"
    _jend 0
    echo 
  else
    _jend 1
    jbegin "$BAD linux zeigt auf nicht vorhandene Kernelquellen oder existiert nicht; neu verlinken$NORMAL";
      klink
    jend 
  fi
}

kinstall() # mountet evtl. boot, kopiert das bzimage, führt lilo aus
{
  inline "Kernel installieren"

  if [ -f $IMGPATH ];then
    still "kinstall_intern"
    jend
  else
    _jend 1
    echo -e "$BAD\t$IMGPATH nicht vorhanden!\n\tbmk -b ausführen!\n$NORMAL"
  fi
}

mods()
{
  if [[ "$1" == "full" ]];then
    make $OPTS modules modules_install
  else
    make $OPTS modules_install
  fi
}

makeall()
{
  inline "Module installieren"
    still "mods"
  jend

  [[ -z $NODRV ]] && graphic

  userfunct drv

  [[ $BUILD ]] && kinstall

echo -e "\n=============== alles erledigt ===============\n"
}

prebuild()
{
  [[ $LINK ]] && klink
  [[ $MENU ]] && menu

  if [ -z $BUILD ]; then

    if [ $FORCE ]; then
      if [ $MODINSTALL ];then # f M
        inline "Module bauen und installieren"
          still "mods full"
        jend
      else # f !M
        force
	makeall
      fi
    else
      if [ $MODINSTALL ];then # !f M
        inline "Module installieren"
         still "mods"
        jend
      fi
    fi

    [[ $VGA ]] && graphic
    [[ $INSTALL ]] && kinstall

    userfunct sub

  exit  ####wenn nicht build , beende hier####
  fi # [ -z $BUILD ]
}

kbuild()
{
  inline "Kernel bauen"
  if [ $CLEAN ];then inline "cleaning"; still "make clean"; jend; fi
  if [ $RAM ];then
    mkramdrv
    still "make $OPTS"
    rmramdrv

  else
   still "make $OPTS"
  fi
  jend
}

drv()
{
  if [[ `ls -l $IMGPATH` == $VER ]]; then
    echo -e "\nkeine Erneuerung der der Treiber notwendig.\n"

    [[ $FORCE ]]&&{
      force
      makeall
    }

  else
    makeall
  fi
}
