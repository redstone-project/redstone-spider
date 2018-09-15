## 1. 下发任务的格式

```python
task = {
    "feed_url": "url",
    "feed_id": 123,
    "feed_name": "name",
    "feed_config": {
        "use_proxy": True,
        # ...other config
    },
    "spider_name": "SpiderName"
}
```

## 2. 回复结果的格式

```python
spider_result = {
    "spider_result": {
        # 爬虫是否运行成功
        "success": False,
        # 错误消息，如果正常运行，则为空
        "error_message": "",
        # 错误stack消息，如果正常运行，则为空
        "error_stack_info": "",
        # items列表
        "results": [],  # type: List[Dict[str, str]]
    },
    "feed_id": 123,
    "feed_name": "feed name"
}

```
