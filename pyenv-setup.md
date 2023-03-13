# pyenv安装

ubuntu : 
apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

centos : 
yum -y install gcc git zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel
yum -y install  git

wget https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tar.xz  -P ~/.pyenv/cache
pyenv install 3.8.8 -v


wget https://www.python.org/ftp/python/3.10.6/Python-3.10.6.tar.xz  -P ~/.pyenv/cache
pyenv install 3.10.6 -v

```
Pyenv安装
安装依赖
yum -y install gcc git zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel
下载pyenv源代码
git clone git://github.com/yyuu/pyenv.git ~/.pyenv
添加环境变量
cat << "EOF" >> ~/.bashrc
export PYENV_ROOT="${HOME}/.pyenv"

if [ -d "${PYENV_ROOT}" ]; then
  export PATH="${PYENV_ROOT}/bin:${PATH}"
  eval "$(pyenv init -)"
fi
EOF

source ~/.bashrc
Done
安装指定Python版本(以Python 3.6.3为例)
从国内镜像源下载Python指定版本
wget http://mirrors.sohu.com/python/3.6.3/Python-3.6.3.tar.xz  -P ~/.pyenv/cache
安装指定Python版本(-v表示显示安装过程，可省略)
pyenv install 3.6.3 -v
切换pip镜像源为国内镜像
pyenv在安装python的时候，已经自动将pip安装好了
mkdir ~/.pip

cat << "EOF" >> ~/.pip/pip.conf
[global]
timeout = 6000
index-url = https://pypi.douban.com/simple
trusted-host = pypi.douban.com
EOF
Done
Pyenv常用命令
查询所有可以安装的版本
pyenv install --list
安装指定版本
建议按照上面的步骤，先从国内镜像下载然后再安装，否则会非常慢甚至中断
pyenv install 3.6.3
卸载指定版本
pyenv uninstall 2.7.13
显示已安装的所有版本
最前面带*的表示当前生效的版本
pyenv versions
显示当前生效的版本
pyenv version
设置全局(整个系统生效)Python版本
pyenv global 3.6.3
设置多个全局(整个系统生效)Python版本
后面的版本号排序有先后，在前表示默认版本
# 方案1
pyenv global 3.6.3 2.7.13

# 方案1效果如下
python --version
Python 3.6.3

python3.6 --version
Python 3.6.3

python2.7 --version
Python 2.7.13

# 方案2
pyenv global 2.7.13 3.6.3

# 方案2效果如下
python --version
Python 2.7.13

python3.6 --version
Python 3.6.3

python2.7 --version
Python 2.7.13
设置局部(当前目录生效)Python版本
pyenv local 3.6.3
设置多个局部(当前目录生效)Python版本
后面的版本号排序有先后，在前表示默认版本
# 方案1
pyenv local 3.6.3 2.7.13

# 方案1效果如下
python --version
Python 3.6.3

python3.6 --version
Python 3.6.3

python2.7 --version
Python 2.7.13

# 方案2
pyenv local 2.7.13 3.6.3

# 方案2效果如下
python --version
Python 2.7.13

python3.6 --version
Python 3.6.3

python2.7 --version
Python 2.7.13
取消设置局部(当前目录生效)Python版本
pyenv local --unset
pyenv-virtualenv(Pyenv插件)介绍
可以为不同的项目创建不同的虚拟环境
设置环境变量后，可进入指定目录自动激活虚拟环境
pyenv-virtualenv安装
下载pyenv-virtualenv源代码
git clone git://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

source ~/.bashrc
添加环境变量(进入指定目录自动激活虚拟环境)
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc
pyenv-virtualenv常用命令
基于指定版本创建虚拟环境(推荐)
pyenv virtualenv 3.6.3 venv_name
基于当前版本创建虚拟环境(不推荐)
pyenv virtualenv venv_name
设置当前目录的虚拟环境(推荐)
若按照之前的步骤设置了环境变量，则会在进入目录后自动激活虚拟环境
pyenv local venv_name
取消设置当前目录的虚拟环境(推荐)
pyenv local --unset
手动激活虚拟环境(不推荐)
pyenv activate venv_name
手动停用虚拟环境(不推荐)
pyenv deactivate venv_name
显示所有已创建的虚拟环境
不一定已在当前目录激活
一个虚拟环境会显示两条记录
pyenv virtualenvs
博客更新地址
```


yum -y install zlib-devel 
yum -y install bzip2 
yum -y install bzip2-devel 
yum -y install readline-devel 
yum -y install sqlite 
yum -y install sqlite-devel 
yum -y install openssl-devel 
yum -y install xz 
yum -y install xz-devel

git clone git://github.com/yyuu/pyenv.git ~/.pyenv

git clone https://github.com/pyenv/pyenv.git ~/.pyenv

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

wget https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tar.xz  -P ~/.pyenv/cache  

pyenv install 3.8.0  

pyenv global 3.8.0  

pip3 install numpy -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com  
pip3 install reportlab -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com  
pip3 install xmlrunner -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com  


参考：
https://zhuanlan.zhihu.com/p/31194682
https://einverne.github.io/post/2017/04/pyenv.html




