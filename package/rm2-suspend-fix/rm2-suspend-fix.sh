#!/usr/bin/env bash
# Inspired by https://blog.christophersmart.com/2016/05/11/running-scripts-before-and-after-suspend-with-systemd/comment-page-1/

if [[ "${1}" == "pre" ]]; then
    rmmod brcmfmac
elif [[ "${1}" == "post" ]]; then
    modprobe brcmfmac
fi
