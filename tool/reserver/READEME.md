##构建基础目录
cd workspace
git clone ssh://git@h5.git.com:54322/abbey/server.git game-server/server
git clone ssh://git@h5.git.com:54322/soo/tool.git tool tool
git clone ssh://git@h5.git.com:54322/overseas/tool.git config

##修改 excel_export2.py
resource_path = sys.argv[1]

##build 应用
go build -o bin/run src/go/main.go

##会话中启动
screen -ls
./bin/run

