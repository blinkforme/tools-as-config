# PROTOBUF使用说明



### protoc

安装protoc编译器

install文件夹下protobuf-all-3.6.1.zip

或者自行到github下载
>https://github.com/protocolbuffers/protobuf


### python

PY2.X


## 使用说明

protobuf描述文件放置于proto文件夹下，文件以proto结尾
基本的概念自己网上熟悉一下。


脚本使用（类似导表工具）

> python proto.py [project_name]

完成后服务端导出abbey.pb的二进制描述文件。
客户端会导出对应的编解码代码。


配置项

```
# protobuf 服务端导出路径
PROTO_SERVER_PATHS = [
    "/Users/peterpuppy/code/server_qq/"
]

# protobuf 客户端导出路径
PROTO_AS_PATHS = [

]
```



# PROTO描述文件编写
###示例
```
message ItemData {
    required sint32 good_id = 1;
    required sint32 good_num = 2;
    optional ItemData data = 3;

}
//红点协议
message s2c_19006 {
    optional sint32 red_points = 1;
    optional string xxx = 2;
    repeated ItemData items = 3;
    optional float num = 4;
    map<string,ItemData> reward = 5;
}

```



目前支持并经过测试的类型：

* sint32 可变长INT，使用zigzag编码
* string utf编码
* float
* bool
* map

其他类型有待完善



# 调试

前端ENV consoleLog改为true

在chorme的console中可以根据日志等级来筛选前端拿到的协议内容。

协议内容日志等级为verbose



