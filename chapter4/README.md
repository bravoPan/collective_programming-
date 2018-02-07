### 基于内容排名

以下为查询`samurai`这个关键词所得到的两种结果,最大权重均为1.0

#### 根据单词频度查询相关度
```text
1.000000	http://www.theshogunshouse.com/
0.746988	http://forums.samurai-archives.com
0.253012	http://www.samurai-archives.com
0.192771	https://www.nakasendoway.com/themes/religion/
0.192771	https://www.nakasendoway.com/themes/transport/
0.180723	https://www.nakasendoway.com/themes/administration/
0.168675	http://www.samuraipodcast.com
0.108434	https://hu.wikipedia.org/wiki/Szekigaharai_csata
0.096386	https://en.wikipedia.org/w/index.php?title=Battle_of_Sekigahara&oldid=823400351
0.096386	https://ca.wikipedia.org/wiki/Batalla_de_Sekigahara
``` 

#### 根据文档位置查询相关度
```text
1.000000	http://www.samuraipodcast.com
0.100000	http://www.samurai-archives.com
0.071429	http://www.samurai-archives.com/searchst.html
0.052632	http://forums.samurai-archives.com
0.003817	http://www.jcastle.info/castle/profile/266-Tanabe-Castle
0.001453	https://sr.wikipedia.org/wiki/%D0%9E%D0%BF%D1%81%D0%B0%D0%B4%D0%B0_%D0%9E%D0%B4%D0%B0%D0%B2%D0%B0%D1%80%D0%B5
0.001205	https://id.wikipedia.org/wiki/Pengepungan_Odawara_(1590)
0.001157	https://mk.wikipedia.org/wiki/%D0%9E%D0%BF%D1%81%D0%B0%D0%B4%D0%B0_%D0%BD%D0%B0_%D0%9E%D0%B4%D0%B0%D0%B2%D0%B0%D1%80%D0%B0_(1590)
0.001135	https://en.wikipedia.org/wiki/Siege_of_Odawara_(1590)
0.001119	https://es.wikipedia.org/wiki/Sitio_de_Odawara_(1590)
```

#### 基于pagerank,以上两个标准共同制定权重
> 每一种衡量标准的最大权重都是1，所以3种最大的权重就是3，3代表最相关的网页;比如说基于单词频度的查询中`www.theshogunshouse`排名
第一，基于文档位置中`samuraipodcast`排名第一，但是基于位置种`theshogunshouse`已经找不到了，因为根据位置排名
他的权重已经不在前10之内了(这里只取了前10的结果)；再来看pagerank加上上面两种权重的综合排名，这里`samuraipodcast`排名第一，`theshogunshouse`
排名第二，无疑很可靠，综合了以上的权重，所以综合所有权重能得到更准确的结果。

```text
2.168675	http://www.samuraipodcast.com
2.000679	http://www.theshogunshouse.com/
1.799620	http://forums.samurai-archives.com
1.353012	http://www.samurai-archives.com
1.193665	https://www.nakasendoway.com/themes/transport/
1.193320	https://www.nakasendoway.com/themes/religion/
1.181272	https://www.nakasendoway.com/themes/administration/
1.119621	http://www.samurai-archives.com/searchst.html
1.108600	https://hu.wikipedia.org/wiki/Szekigaharai_csata
1.096639	https://en.wikipedia.org/wiki/Battle_of_Sekigahara
```