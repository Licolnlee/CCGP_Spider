# CCGP_Spider
CCGP_Spider is specified for CCGP Goverment project to acquire information.

1.Install requirement depends.
---
  - Run these commands through Pycharm Terminal which is under beneath.
    >+ __cd proxy_pool__
    >+ **pip install -r requirements.txt**
 
2.Install redis database && graphic manager.
--- 
  - Install redis.exe and redisDesktopManager.exe which contain in software folder.
    >+ __installation all using default setting.__
    >+ **DesktopManager->Connect to Redis Server->Connection**
       >>* __Name:localhost__
       >>* __Host:localhost__
       >>* __Port:6379(default)__
       >>* __Auth:default__
    >+ **Do not forget to test Connection.

3.Go to csv2redis.py in order to get data into redis.
---
  - Right click csv2redis.py to run python program.
 
4.Run proxy_pool backgroud.
---
  - Run these commands through Pycharm Terminal which is under beneath.
    >+ __cd proxy_pool/cli__
    >+ **python proxyPool.py schedule**
    >+ **python proxyPool.py webserver**

5.Run uuid_req.py to require uuid download link.
---
  - Right click csv2redis.py to run python program.


6.Run downloader.py to require file.(Please run this before uuid_req.py)
---
  - Right click csv2redis.py to run python program.

 