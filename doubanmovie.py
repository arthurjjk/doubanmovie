from urllib import request
from bs4 import BeautifulSoup as bs
import re

#首先通过request获取网页数据并读取出来
response=request.urlopen('https://movie.douban.com/cinema/nowplaying/shenzhen/')
html_data=response.read().decode('utf-8')

#将获得的网页数据通过beautifulsoup解析
data_bs=bs(html_data,'lxml')

#找到我们想要的数据，即影片信息列表
nowplaying_movie=data_bs.find_all('div',id='nowplaying')
nowplaying_movie_list=nowplaying_movie[0].find_all('li',class_='list-item')

nowplaying_list=[]
#循环提取中每部电影的id和name，存入nowplaying_list
for item in nowplaying_movie_list:
    nowplaying_dict={}
    nowplaying_dict['id']=item['data-subject']
    for tag_img_item in item.find_all('img'):
        nowplaying_dict['name']=tag_img_item['alt']
        nowplaying_list.append(nowplaying_dict)

#构造第一篇电影短评页面的url
requrl='http://movie.douban.com/subject/'+nowplaying_list[0]['id']+'/comments?status=P'

#获得网页数据并通过bs解析
cmt_data=request.urlopen(requrl).read().decode('utf-8')
cmt_bsdata=bs(cmt_data,'lxml')

#提取短评部分
comment_div_list=cmt_bsdata.find_all('div',class_='comment')
eachCommentList=[]
for item in comment_div_list:
    if item.find_all('p')[0].string is not None:
        eachCommentList.append(item.find_all('p')[0].string)

#将短评列表合并成字符串并去掉空白字符
comments=re.sub('\s','',''.join(eachCommentList))
#去掉标点符号
pattern=re.compile(r'[\u4e00-\u9fa5]')
filterdata=re.findall(pattern,comments)
cleaned_comments=''.join(filterdata)

import jieba
import pandas as pd
#分词
segment=jieba.lcut(cleaned_comments)
words_df=pd.DataFrame({'segment':segment})

#过滤高频词
stopwords=pd.read_csv('chineseStopWords.txt',index_col=False,quoting=3,sep='\t',names=['stopword'],encoding='gbk')
words_df=words_df[~words_df.segment.isin(stopwords.stopword)]

import numpy    #numpy计算包
words_stat=words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
words_stat=words_stat.reset_index().sort_values(by=["计数"],ascending=False)

#用词云将数据可视化
import matplotlib.pyplot as plt

import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
from wordcloud import WordCloud#词云包
 
wordcloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=80) #指定字体类型、字体大小和字体颜色
word_frequence = {x[0]:x[1] for x in words_stat.head(1000).values}
word_frequence_list = []
for key in word_frequence:
    temp = (key,word_frequence[key])
    word_frequence_list.append(temp)
 
wordcloud=wordcloud.fit_words(dict(word_frequence_list))
plt.savefig('result.jpg')
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

        

