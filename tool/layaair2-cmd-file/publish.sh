#!/bin/sh

#项目地址
projectPath="D:\gitAssetsDownload\client2\abbey";
#是否再次编译
compileAgain=true;
#发布平台|web|wxgame|bdgame|qqgame|xmgame|vivogame|oppogame
publishPlatform="web";





#if [ $projectPath == nil ] || [ $projectPath ==  ]

echo "-----------start-----------------"
echo
echo "projectPath $projectPath"
echo
echo "是否再次编译 $compileAgain"
echo "发布平台 $publishPlatform"
echo
#没有根据项目路径进行打包 （会在项目的.laya文件夹下寻找gulp）

if [ $compileAgain == true ]; then
layaair2-cmd compile -w $projectPath
fi


if [ $publishPlatform == "web" ] || [ $publishPlatform == "wxgame" ];then
layaair2-cmd publish -c $publishPlatform -w $projectPath
fi
