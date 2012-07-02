#!/bin/bash

confirm() {
    echo -n "$1"
    echo -n "OK [Y/n]?"
    read ANSWER
    if [ "$ANSWER" == "y" ] || [ "$ANSWER" == "Y" ] || [ -z "$ANSWER" ]
    then
        eval $1
        echo "... parameter set"
    else
        echo "... parameter NOT set"
    fi
}

if [ -z "$1" ]
then
    echo -n "Name of VM [l for list]: "
    read VM
else
    VM="$1"
fi

if [ "$VM" == "l" ] || [ "$VM" == "L" ]
then
    xe vm-list | grep name-label | grep -v "Control domain"
    exit
fi

echo ""
echo "Looking up UUID for VM $VM"

UUID=$(xe vm-list name-label="$VM" params=uuid --minimal)
if [ -z $UUID ]
then
    echo "No UUID found for $VM."
    exit 0
fi

echo ""
echo "UUID=$UUID"
echo ""
echo "Setting parameters for VM $VM"
confirm "xe vm-param-clear uuid=$UUID param-name=HVM-boot-params"
confirm "xe vm-param-clear uuid=$UUID param-name=HVM-boot-policy"
confirm "xe vm-param-clear uuid=$UUID param-name=PV-bootloader-args"
confirm "xe vm-param-set uuid=$UUID PV-bootloader=pygrub"
confirm "xe vm-param-set uuid=$UUID PV-args='-- quiet console=hvc0'"

echo ""
echo "List of disks for VM $VM"
xe vm-disk-list uuid=$UUID

echo ""
echo "Looking up UUID for VBD of VM $VM"
VBD=$(xe vm-disk-list uuid=$UUID | grep -A1 VBD | tail -n 1 | cut -f2 -d: | sed "s/ *//g")
if [ -z $VBD ]
then
    echo "No VBD UUID found for $VBD."
    exit 0
fi

echo "VBD UUID=$VBD"
echo ""
echo "Setting parameters for VBD $VBD"
confirm "xe vbd-param-set uuid=$VBD bootable=true"
exit 0
