#!/bin/bash
# Ver: 0 ;  Dec 30 /2019 -- inital script
# Ver: 0.1 ;  Jan 4/2020 -- added password free sudo
# Ver: 0.2 ; Feb 23/2020 -- set hostname using raspiconfig command line
#
# to do, replace the password setup with an ssh key copy. This could be a two step process,
# copy key, then spin password to random crap

# Be nice check if there is a group before mashing it all in and raising errors.
grep -i devop /etc/group 2>&1> /dev/null
if [ $? -eq 1 ] ; then
        groupadd DevOpsInf
        groupadd DevOpsApp
else
        echo "Devops groups appear to be created"
fi
sleep 3
grep -i aadams /etc/passwd 2>&1> /dev/null
if [ $? -eq 1 ] ; then
        useradd -m -d /home/aadams -c "Devops admin" -s /bin/bash aadams
        usermod -G DevOpsInf,DevOpsApp aadams
else
        echo "Ansible User account appears to be created"
        #exit 1 premature exit 
fi
#Create password free sudo option for DevOpsInf group, this way we don't affect normal admins
grep -i devop /etc/sudoers 2>&1> /dev/null
if [ $? -eq 1 ] ; then
        echo "#Enable password free sudo for DevOps automation" >> /etc/sudoers
        echo "%DevOpsInf ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
else
        echo "DevOpsInf is already in sudoers, confirm it's correct"
        grep -i devop /etc/sudoers
fi

sleep 3
# create creds for the ansible user
read -p "please input ansible user's password: " acred
echo -e "${acred}\n${acred}" | passwd aadams

# Uncomment below if you are building PI boxes
## you need to set the hostname for each PI
sleep 2
echo `/bin/hostname`
read -p "please input this device's hostname: " hname
/usr/bin/raspi-config nonint do_hostname ${hname}
sleep 2
echo `cat /etc/hostname`
echo 'cat /etc/hosts'
#
locale=en_US.UTF-8
layout=us
/usr/bin/raspi-config nonint do_change_locale $locale
/usr/bin/raspi-config nonint do_configure_keyboard $layout