# ApacheCN 文档一键部署

## 部署手册

### 第一步：检查系统版本

一键部署工具可能不止支持一个系统，但目前只在 CentOS7 上有过部署。

因此这个手册的所有命令都假定是 CentOS7。

执行以下命令来查看是否是 CentOS7：

```
# cat /etc/centos-release
CentOS Linux release 7.7.1908 (Core)
```

【如果运维人员在其它系统部署成功，更新这个手册。】

### 第二步：检查 Python3 和 Git

CentOS7 应该带这两个东西，无需安装。

（自带的 Python3 应该是 3.6，不过没关系，3.6 以及更新版本都可以。）

执行以下命令来查看是否安装：

```
# python3 --version
Python 3.6.8
# git --version
git version 1.8.3.1
```

### 第三步：检查 Docker

先检查是否安装了 Docker，如果有就跳过安装步骤：

```
# docker --version
Docker version 20.10.6, build 370c289
```

或者：

```
# rpm -q docker-ce
docker-ce-20.10.6-3.el7.x86_64
```

### 第四步：安装 Docker

如果已安装，可以跳过。

（1）通过脚本

```
curl -sSL https://get.daocloud.io/docker | sh
```

（2）通过包管理器

```
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io
```

### 第五步：启动 Docker

启动 Docker 服务：

```
# systemctl  start docker.service
```

查看 Docker 服务情况：

```
# systemctl  status docker.service
● docker.service - Docker Application Container Engine
   Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
   Active: active (running) since Thu 2021-04-29 13:15:32 CST; 8 months 8 days ago
     Docs: https://docs.docker.com
 Main PID: 29885 (dockerd)
    Tasks: 30
   Memory: 182.8M'
...
```

运行 HelloWorld 容器来校验：

```
# docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
2db29710123e: Pull complete
Digest: sha256:2498fce14358aa50ead0cc6c19990fc6ff866ce72aeb5546e1d59caac3d0d60f
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```


## `config.json`配置项说明

+	`name`：Docker Nginx 容器名称
+	`port`：HTTP 端口号
+	`secPort`：HTTPS 端口号
+	`dataDir`：站点数据目录
+	`sslDir`：证书目录
+	`conf`：Nginx 配置文件名称，在`asset/conf/${conf}.conf`
+	`clean`：如果为真，每次重新克隆文档仓库
+	`cnzz`：CNZZ 统计后台 ID
+	`bdStat`：百度统计后台 ID
+	`icp`：备案号
+	`title`：导航页面标题
+	`menus`：导航页面菜单
	+	`name`：文本
	+	`link`：链接
+	`announce`：导航页面公告
	+	`text`：文本
	+	`link`：链接
+	`members`：成员信息
	+	`name`：名称，例如`飞龙`
	+	`desc`：描述，例如`iBooker组织创始人和ApacheCN文档翻译负责人`
	+	`link`：链接，例如`https://github.com/wizardforcel`
	+	`logo`：头像，在`asset/site_asset/avatar/${logo}.png`
+	`links`：友情链接
	+	`name`：文本
	+	`link`：链接
+	`cates`：在页面显示的分类，有序
+	`docs`：文档列表
	+	`name`：目录名称，将保存到`${dataDir}/html/${name}`
	+	`nameCn`：显示名称
	+	`desc`：描述
	+	`link`：站外文档的链接，如果设定了该属性，优先在导航页显示
	+	`repo`：文档的 Git 仓库地址，如果不设定，则不拉取
	+	`cate`：类别，注意如果不是`cates`中的值，则不显示在页面上
	+	`logo`：图标，在`asset/site_asset/icon/${logo}.png`
	+	`hidden`：如果为真，则不在页面上显示
