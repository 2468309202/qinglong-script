<h1 id="L9K9D">写在前沿</h1>
青龙是什么？
加QQ群：978659787
<font style="color:rgb(33, 53, 71);">答：支持 Python3、JavaScript、Shell、Typescript 的定时任务管理平台</font>

<h2 id="功能特性"><font style="color:rgb(33, 53, 71);">功能特性</font>[<font style="color:rgb(0, 149, 255);">#</font>](https://qinglong.online/guide/introduction#%E5%8A%9F%E8%83%BD%E7%89%B9%E6%80%A7)</h2>
+ <font style="color:rgb(33, 53, 71);">支持多种脚本语言（python3、javaScript、shell、typescript）</font>
+ <font style="color:rgb(33, 53, 71);">支持在线管理脚本、环境变量、配置文件</font>
+ <font style="color:rgb(33, 53, 71);">支持在线查看任务日志</font>
+ <font style="color:rgb(33, 53, 71);">支持秒级任务设置</font>
+ <font style="color:rgb(33, 53, 71);">支持系统级通知</font>
+ <font style="color:rgb(33, 53, 71);">支持暗黑模式</font>
+ <font style="color:rgb(33, 53, 71);">支持手机端操作</font>



<h3 id="vRYPF">需要准备的事项</h3>
一台支持docker的服务器、飞牛、玩客云等等

话不多说，接下来进入安装教程[https://qinglong.online/](https://qinglong.online/)

官网首页已经写的很清楚了，推荐大家用docker compose部署更方便管理

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696027305-c780dd9d-b278-4668-8901-ab310eef1df0.png)

这里博主是一个阿里云的 ubuntu 系统的服务器--需要安装docker 如果不会安装的话 那么可以阿里云服务器实例界面去安装 它是免费的，不花钱，还是不行的话网上搜一下教程这里就不多扩展了。

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696289467-638ce743-3667-4e77-837c-93126cb528d1.png)

安装完之后我们可以敲一下这个命令 <font style="color:#000000;">systemctl status docker  看docker是否有启动成功</font>

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696415867-5ccf335f-13a1-4b75-a0fd-a156f51ca00f.png)

然后按照青龙面板的教程去 安装即可

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696466333-14e3c586-6ddd-4879-bcf2-b503c41671b1.png)

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696513889-25af84e8-0464-48b3-8f3a-3ed246d47a58.png)

题外话：

如果端口不想用默认5700 是可以修改的。

安装完成之后 docker ps-a 看到青龙面板在容器内的情况了

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696613740-39d57dd8-4d9b-44a3-8e7f-2a1098db34b2.png)

然后我们 公网ip+5700端口可以访问。 

<h2 id="LOYGj">青龙面板配置教程</h2>
<h3 id="STYMK">订阅管理</h3>
讲一下怎么拉库，订阅管理里面。拉取faker仓库

目前github上很火的库就2个。faker2 和faker3 [https://github.com/shufflewzc/faker2](https://github.com/shufflewzc/faker2) 

复制这一串代码 到青龙面板--<font style="color:#DF2A3F;">订阅管理里面。定时规则随便写 我是。0 9 * * *（意思就是每天九点运行，但是一般订阅的一些脚本 定时任务都是写好了的。不用在单独设置）</font>

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696853315-acdbd0dc-1729-4d47-8cf5-8f402b91c6b3.png) ![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757696913029-85b15df4-40ad-4ff1-9847-8cb9ff386ddc.png)

拉取完可以看到很多的jd任务了

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757697038572-df71c088-78ea-479e-95a0-484ebc0908fd.png)

<h3 id="PCpMw">配置jd的变量</h3>
创建变量 名称要写 JD_COOKIE

值：pt_key=AAJoxxxxxxxxxxU7hhPCbYJwzqYiYEFY;pt_pin=1xxxxxxxxxx; 这部分是登陆京东抓包来的，可参考 [https://blog.csdn.net/onewlife/article/details/120294492](https://blog.csdn.net/onewlife/article/details/120294492) 

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1757697096368-d7205906-d8b7-4c92-92a0-3c4b904213ac.png)

<h3 id="XwnCw">自动脚本的安装与使用（进阶玩法，重要）</h3>
示例图

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1760317017480-f86908db-d91b-477f-8a88-2c6a7b416c42.png)

<h4 id="wfQmk">添加脚本文件</h4>
![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1760317088395-19745c16-a5d9-47f1-9712-7ae8079e207e.png)

<h4 id="YmhpW">添加定时任务</h4>
```bash
task readhub_daily_bot.py ##task xxxx.py
```

![](https://cdn.nlark.com/yuque/0/2025/png/27160655/1760317200643-50cbf860-a366-41e7-87c1-6e962fda4a25.png)

<h3 id="DwWxu">依赖的安装</h3>
最全依赖参考这个博主的 node.js有个依赖需要单独装一下

[Node.js与Python3依赖库及Linux系统必备组件-CSDN博客](https://blog.csdn.net/weixin_40453992/article/details/130522262?ops_request_misc=%257B%2522request%255Fid%2522%253A%25226f528f148e7b881cd8a3a8bd18a15778%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=6f528f148e7b881cd8a3a8bd18a15778&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-130522262-null-null.142^v102^pc_search_result_base2&utm_term=%E9%9D%92%E9%BE%99%E9%9D%A2%E6%9D%BF%E4%BE%9D%E8%B5%96&spm=1018.2226.3001.4187)

<font style="color:#DF2A3F;">node.js有个依赖需要单独装一下</font>

<font style="color:#DF2A3F;">创建的时候 node里面输入</font><font style="color:rgba(0, 0, 0, 0.85);background-color:rgb(250, 250, 250);">got@11 即可</font>

<font style="color:rgba(0, 0, 0, 0.85);background-color:rgb(250, 250, 250);">然后就可以愉快的自动的跑脚本了</font>

<h3 id="wappy"><font style="color:rgba(0, 0, 0, 0.85);background-color:rgb(250, 250, 250);">分享几个可用的青龙脚本库。</font></h3>
[https://script.345yun.cn/](https://script.345yun.cn/)

