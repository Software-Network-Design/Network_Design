## Protocal & Database

#### 消息格式

`(发送用户;接收用户;类型;消息内容)`

* 使用json组织
* utf-8编码

##### 类型

| 类型号 | 代表消息          |
| ------ | ----------------- |
| 1      | 登录消息          |完成z
| 2      | 服务器响应登录    |完成z
| 3      | 一对一消息        |完成z
| 4      | 群发消息          |完成z
| 5      | 注销消息          |完成z
| 6      | 发送文件开始/结束 |
| ~~7~~  | ~~请求用户ip~~    |暂无
| 8      | 好友上线提醒      |完成z
| 9      | 好友请求          |完成zl
| 10     | 好友回应          |完成zl
| 11     | 个人信息修改      |完成zl
| 12     | 发送图片开始/结束 |
| 13     | 注册请求         |完成z
| 14     | 响应注册         |完成z
| 15     | 个人信息修改回应  |完成zl
| 16     | 广播修改后的用户名|完成z

##### 用户

* 每个用户拥有一个号码（类似QQ号，'U' + 数字串）
* 每个群拥有一个群号（'G' + 数字串）

* 用户Num=用户id

#### 登录过程

```
1：登录请求
{
    // 用户id
    "send": "u123",
    "receive": "",
    "type": 1,
    "info": {
        "user_id": "u123",
        "user_pwd": "123"
    }
}
2：登陆响应返回示例
{
    "send": "server",
    "receive": "u123",
    "type": 2,
    "info": {
        "success": "登录成功",//或"无此用户"或"密码错误"
        "strangers": [],
        "friends": [
            {
                "user_id": "u234",
                "user_name": "xyz"
            }
        ]
    }
}
8：有人上线提醒
{
    "send": "server",
    //被提醒人id
    "receive": "u234",
    "type": 8,
    "info": {
        //上线人id
        "user_id": "u123",
        //上线人用户名
        "user_name": "zyx",
        //上线人与被提醒人关系
        "type": "friend" // 或"stranger"
    }
}
```

#### 注册过程

```
13：注册请求
{
    "send": "",
    "receive": "",
    "type": 13,
    "info": {
        "user_name": "xxxx",
        "user_pwd": "123321123"
    }
}
14：注册响应
{
    "send": "server",
    // 若成功，返回用户id，即账号；失败返回""
    "receive": "998551534",
    "type": 14,
    // 用户名
    "info": "xxxx"
}
```

#### 注销过程

```
5：注销消息
每个在线的用户都会收到注销账户发出的注销消息
{
    //注销账户id
    "send": "u123",
    //接收者id
    "receive": "u234",
    "type": 5,
    "info": "logout"
}
```



#### 聊天过程

##### 一对一聊天

```
3：私聊消息
{
    "send": "u123",
    "receive": "u234",
    "type": 3,
    "info": "私聊噢"
}
```

##### 群聊

```
4：群发消息
{
    "send": "u123",
    "receive": "",
    "type": 4,
    "info": "群聊噢"
}
```



#### 单独/群组发送文件

```
Client->Server
{
    "send": "u123",
    "receive": "u234",  #群发:""
    "type": 6,
    "info": "start sending"
}
"name|size"
content size = 1024

Server->Client(s)
{
    "send": "u123",
    "receive": "u234",  
    "type": 6,
    "info": "start sending"
}
"name|size"
content size = 1024
```

#### 单独/群组发送图片

```
Client->Server
{
    "send": "u123",
    "receive": "u234",  #群发:""
    "type": 12,
    "info": "start sending"
}
"name|size"
content size = 1024

Server->Client(s)
{
    "send": "u123",
    "receive": "u234",  
    "type": 12,
    "info": "start sending"
}
"name|size"
content size = 1024
```

#### 加好友

```
9:好友请求
{
    "send": "u123",
    "receive": "u234",
    "type": 9,
    "info": "好友请求"
}

10：好友请求回应
{
    "send": "u234",
    "receive": "u123",
    "type": 10,
    "info": True / False
}
```



#### 修改个人信息

```
11：修改个人信息
{
    "send": "u234",
    "receive": "server",
    "type": 11,
    "info": {
        //0：修改密码；1：修改用户名
        "PU": 0 / 1
        "NewInf": "123321"
    }
}
15：修改个人信息结果返回
{
    "send": "server",
    "receive": "u234",
    "type": 15,
    "info": {
        //0：修改密码；1：修改用户名
        "PU": 0 / 1
        "NewInf": "123321"
    }
}
16：广播修改后的用户名
{
    'send': 'server',
    'receive': 'u234',
    'type': 16,
    'info': {
        'user_id': user_id,
        'user_name': New_Inf
    }
}
```



#### 发送图片

```
(new port)
Client-->Server
(发送用户(用户Num);接受用户();类型(12);消息内容(开始发送))
file_name|file_size
文件传输(每次发送固定大小)
(发送用户(用户Num);接受用户();类型(12);消息内容(发送结束))

Server-->Client
(发送用户();接受用户(用户Num);类型(12);消息内容(开始发送))
file_name|file_size
文件传输(每次发送固定大小)
(发送用户();接受用户(用户Num);类型(12);消息内容(发送结束))
```





##### 发送表情实现方法

使用代码表示表情，如`/xyx`



### 数据库

##### E-R图

![聊天软件数据库.drawio](./media/聊天软件数据库.drawio.png)

User

| 属性         | 类型    | 主键 | 外键 |
| ------------ | ------- | ---- | ---- |
| 用户Num      | VARCHAR | √    | √    |
| 用户昵称     | VARCHAR |      |      |
| 用户ip地址   | VARCHAR |      |      |
| 是否在线     | bool    |      |      |
| 其他扩展信息 |         |      |      |

Group

| 属性  | 类型    | 主键 | 外键 |
| ----- | ------- | ---- | ---- |
| 群Num | VARCHAR | √    | √    |

User_Friends

| 属性     | 类型    | 主键 | 外键 |
| -------- | ------- | ---- | ---- |
| 用户1Num | VARCHAR | √    | √    |
| 用户2Num | VARCHAR | √    | √    |

User_Group

| 属性    | 类型    | 主键 | 外键 |
| ------- | ------- | ---- | ---- |
| 群Num   | VARCHAR | √    | √    |
| 用户Num | VARCHAR | √    | √    |