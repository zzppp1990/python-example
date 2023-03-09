1. 安装redis  
sudo apt install redis-server  

2. 查看状态  
sudo systemctl status redis-server  

3. 连接redis  
redis-cli -a 123456  
redis-cli -h 172.21.0.44 -p 6379  
输入密码：auth 123456  

4. import redis失败  
pip install redis  

5. 查看redis记录  
keys *  
HGETALL hash_key  
HVALS hash_key  
列表： LRANGE 'mp4Info' 0 -1  


参考：  
[Redis在Ubuntu安装配置](https://zhuanlan.zhihu.com/p/28101275)