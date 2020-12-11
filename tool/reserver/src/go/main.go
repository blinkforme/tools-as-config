package main

import (
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"strings"
	"time"
)

var port int = 2020
var portString string = fmt.Sprintf(":%d", port)
var prefix string = "===>"
var responseWriter http.ResponseWriter

type structServer struct {
	dir     string
	program string
	server  string
	branch  string
	desc    string
}

var serverSlice = []structServer{
	structServer{"abbey", "h5", "server", "develop", "         h5经典版      "},
    structServer{"unity_abbey_3d", "h5-test2", "server", "develop-unity", "         unity项目      "}}

func response(str string, args ...interface{}) {
	t := time.Now()
	msg := fmt.Sprintf("[%d-%d-%d %d:%d:%d] %s  %s\n", t.Year(), t.Month(), t.Day(), t.Hour(), t.Minute(), t.Second(), prefix, str)
	fmt.Fprintf(responseWriter, msg, args...)
	fmt.Printf("ResponseWriter: "+msg, args...)
}

func reserver(w http.ResponseWriter, r *http.Request) {
	responseWriter = w
	r.ParseForm()
	fmt.Println("path:", r.URL.Path, "scheme", r.URL.Scheme, r.Form)

	var key string = ""
	for k, v := range r.Form {
		fmt.Println("key:", k, "   val:", strings.Join(v, ""))
		if k == "name" {
			key = strings.Join(v, "")
		} else {
			key = k
		}
	}

	trueArgs := false
	var serverName string
	var serverBranch string
	var configDir string
	var serverProgram string

	for _, v := range serverSlice {
		if key == v.dir || key == v.program {
			trueArgs = true
			serverName = v.server
			serverBranch = v.branch
			configDir = v.dir
			serverProgram = v.program
		}
		response("配表路径参数：" + v.dir + v.desc + v.program)
	}
	if !trueArgs {
		fmt.Fprintf(responseWriter, "\n")
		fmt.Fprintf(responseWriter, "\n")
		response("请输入正确的参数 举例经典版")
		response("http://h5.git.com:2020/reserver?name=h5")
		response("或：http://h5.git.com:2020/reserver?name=abbey")
		response("或：http://h5.git.com:2020/reserver?h5")
		response("或：http://h5.git.com:2020/reserver?abbey")
		return
	}

	//更新服务器代码
	cmdUpdateServerCode := fmt.Sprintf("/opt/reserver/src/shell/updateServerCode.sh %s %s %s %s", serverName, serverBranch, configDir, serverProgram)

	cmd := exec.Command("/bin/bash", "-c", cmdUpdateServerCode)
	output, err := cmd.Output()
	if err != nil {
		response("Execute Shell:%s failed with error:%s", cmdUpdateServerCode, err.Error())
		return
	}
	response(string(output))
	response("Execute Shell:%s finished", cmdUpdateServerCode)
}

func main() {
	fmt.Println("server start prot:", port, "  time:", time.Now())
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		responseWriter = w
		response("请输入:http://h5.git.com:2020/reserver")
	})
	http.HandleFunc("/reserver", reserver)
	err := http.ListenAndServe(portString, nil) //设置监听的端口
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}

}
