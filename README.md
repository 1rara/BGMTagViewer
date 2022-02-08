# 班固米用户标签可视化～☆
讨论贴：https://bgm.tv/group/topic/367557

内置两个scrapy爬虫，分别抓取条目索引和用户标签。
### How to build:
依次运行以下代码以获取最新数据：
```
python py/indexCrawler.py
python py/subjectCrawler.py <access_token>
python py/filter.py
```
access_token为用户授权信息，[从这里](https://bgm.tv/oauth/authorize?client_id=bgm212861ca758473c3d&response_type=code)获取。
