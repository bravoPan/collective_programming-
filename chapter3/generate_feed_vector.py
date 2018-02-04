from chapter3.zhihu_zhuanlan import ArticleAnalyze
from pprint import pprint

feeder = ArticleAnalyze()
article_size = feeder.get_article_size()
article_list = feeder.get_article_analyze(n=article_size)

# apcount统计出现单词的博客数目
ap_count = {}
for feed_single_article in article_list:
    for word_tuple in feed_single_article["content"]:
        word = word_tuple[0]
        ap_count.setdefault(word, 1)
        if ap_count[word] >= 1:
            ap_count[word] += 1

# 选择介于10% - 50%之间的单词
word_list = []
for w, bc in ap_count.items():
    frac = float(bc) / article_size
    if frac > 0.1 and frac < 0.5:
        word_list.append(w)


# 保存矩阵，记录真对每个博客的所有单词统计情况
out_file = open("article_data.txt", "w", encoding="utf-8")
out_file.write("Article")
for word in word_list:
    out_file.write("\t{}".format(word))
out_file.write("\n")
for single_article in article_list:
    out_file.write(single_article["title"])
    single_article_contain_word_list = [i[0] for i in single_article["content"]]
    for word in word_list:
        if word in single_article_contain_word_list:
            word_frequency = [i[1] for i in single_article["content"] if i[0] == word]
            out_file.write("\t{}".format(word_frequency[0]))
        else:
            out_file.write("\t0")
    out_file.write("\n")
