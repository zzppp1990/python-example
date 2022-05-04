#coding:utf-8


#要求：读取文件；去除所有标点符号和换行符，并把所有大写变成小写；合并相同的词，统计每个词出现的频率，并按照词频从大到小排序；将结果按行输出到文件 out.txt。

#代码：

import re

# 你不用太关心这个函数
def parse(text):
    # 使用正则表达式去除标点符号和换行符
    text = re.sub(r'[^\w ]', ' ', text)

    # 转为小写
    text = text.lower()

    # 生成所有单词的列表
    word_list = text.split(' ')

    # 去除空白单词
    word_list = filter(None, word_list)

    # 生成单词和词频的字典
    word_cnt = {}
    for word in word_list:
        if word not in word_cnt:
            word_cnt[word] = 0
        word_cnt[word] += 1

    # 按照词频排序
    sorted_word_cnt = sorted(word_cnt.items(), key=lambda kv: kv[1], reverse=True)

    return sorted_word_cnt

with open('in.txt', 'r') as fin:
    text = fin.read()

word_and_freq = parse(text)

with open('out.txt', 'w') as fout:
    for word, freq in word_and_freq:
        fout.write('{} {}\n'.format(word, freq))

"""
---输出(省略较长的中间结果)

and 15
be 13
will 11
to 11
the 10
of 10
a 8
we 8
day 6

...

old 1
negro 1
spiritual 1
thank 1
god 1
almighty 1
are 1
"""


