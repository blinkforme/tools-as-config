#!/bin/bash

root="/opt/reserver"
config_path="${root}/config"
tool_path="${root}/tool/tool"
server_path="${root}game-server/${1}"
server_branch=${2}
config_dir="${config_path}/resource/${3}"
server_program=${4}

echo "进入脚本"
echo "更新服务器代码 start"
echo "目录：${server_path} 分支：${server_branch} 进程：${server_program}"
cd ${server_path}
git add .
git reset --hard HEAD
git checkout ${server_branch}
git status
git fetch
git pull
echo "更新服务器代码 over"
echo "##############################"
echo "git更新配表 start"
cd ${config_path}
git add .
git reset --hard HEAD
git status
git fetch
git pull
echo "git更新配表 over"
echo "##############################"
echo "导出配表 start"
echo "配表目录：${config_dir}"
cd ${tool_path}
python excel_export2.py ${config_dir}
echo "导出配表 over"
echo "##############################"
echo "推送代码 start"
cd ${server_path}
./deploy/deploy.sh ${server_program} stage2 restart
echo "推送代码 over"


# git fetch --all
# git reset --hard origin/master
# git pull