
## 项目说明
需要在主文件同级目录下，增加environ.py文件，内容示例如下：
```
import os

#这里我是用的是阿里百炼api，大概格式
os.environ["OPENAI_API_KEY"] = "xxxxxxx"
os.environ["OPENAI_API_BASE"] = "https://dashscope.aliyuncs.com/compatible-mode/v1/"
```

## powershell中，使用python的虚拟环境运行程序

1、用python新建一个虚拟环境
```
python -m venv myenv
```
2、激活虚拟环境
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# 必须要先运行这一句，否则会提示禁止运行脚本
myenv\Scripts\Activate
```
3、查看已经用pip安装了什么包库
```
pip list
```
4. 跳出虚拟环境
```
deactivate
```

## 项目进化路线
1.本地知识库连接<br/>
2.数据库连接<br/>
3.本地大模型<br/>
4.问答界面<br/>
5.增加记忆<br/>
6.multi-agent<br/>

