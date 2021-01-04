#!/bin/sh
if [ "${1}" == "pre" ]; then
    rmmod brcmfmac
elif [ "${1}" == "post" ]; then
    modprobe brcmfmac
fi
