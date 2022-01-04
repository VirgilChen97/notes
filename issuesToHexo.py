import requests
import json
import time
import sys

class Article:
    def __init__(self):
        self.title = ''
        self.category = ''
        self.tags = []
        self.content = ''

def getIssues(owner, repo, page, size):
    url = str.format('https://api.github.com/repos/{}/{}/issues', owner, repo)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Time-Zone": "Asia/Shanghai"
    }
    params = {
        'page': page,
        'size': size
    }
    r = requests.get(url, headers=headers, params=params)
    return json.loads(r.content.decode('utf-8'))

def issueToArticle(owner, repo):
    page = 1
    size = 100
    articles = []

    while(True):
        pagedIssues = getIssues(owner, repo, page, size)
        if len(pagedIssues) == 0:
            break

        for issue in pagedIssues:
            article = Article()
            # 标题
            article.title = issue['title']
            # 分类
            if issue['milestone'] is not None:
                article.category = issue['milestone']['title']
            # 文章内容
            article.content = issue['body']
            # 日期
            timeArr = time.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            article.date = time.strftime("%Y-%m-%d %H:%M:%S", timeArr)
            for rawTags in issue['labels']:
                article.tags.append(rawTags['name'])
            articles.append(article)

        page+=1

    return articles

def articleToHexo(article, path):
    template = '''---
title: {}
date: {}
category: {}
tags:
{}
---

{}
'''
    tagStr = ''
    for tag in article.tags:
        tagStr += str.format('    - {}\n', tag)
    hexoContent = str.format(template, article.title, article.date, article.category, tagStr, article.content)
    with open(str.format("{}/({}){}.md", path, article.date, article.title).replace(' ','_'), 'w+') as f:
        f.write(hexoContent)

args = sys.argv
res = issueToArticle(args[1], args[2])
for article in res:
    articleToHexo(article, args[3])

