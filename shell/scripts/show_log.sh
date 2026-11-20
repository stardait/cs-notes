#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    printf '用法：bash %s 日志路径\n' "$0" >&2
    exit 2
fi

log=$1
printf '日志路径：%s\n' "$log"
head -n 3 < "$log"