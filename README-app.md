# [misalignVis](https://github.com/nehcx/misalignVis)

This repository was created to present clues to access the connotation
of classical poetic Japanese vocabulary, a.k.a. words used in *Waka*
和歌, by using contemporary Japanese translation words misaligned with
IBM Model 2.

The repository provides the training data, process and several
visualization tools for the above purposes.



## Data



### *Kokin Wakashū* 古今和歌集

The *Kokin Wakashū* (ca. 905) is an anthology of classical Japanese
poetry. The *Kokin Wakashū* dataset is obtained from
[the *Hachidaishū* dataset](https://github.com/yamagen/hachidaishu).

The data format follows so-called [hachidai.db database format](https://github.com/idiig/misalignment2connotation/tree/master/data/hachidaishu).



### 10 contemporary Japanese translations

The complete list of the contemporary Japanese translations of *Kokin
Wakashū* used in the repository can be found in
[raw\_data.bib](https://github.com/nehcx/misalignVis/blob/master/data/translations/raw_data.bib).

All texts were tokenized with the same format with [the *Hachidaishū*
dataset](https://github.com/yamagen/hachidaishu). Part of raw data was stripped off for not infringing the full
texts' copyright. All raw data related to the replication was
remained.


## Alignment models

The repository used IBM Model 2 inplemented in [NLTK](https://www.nltk.org/) to align bitexts
from source texts to target texts and from target texts to source
texts.


## References
  1. Hodošček, B., &; Yamamoto, H. (2022). Development of datasets of the Hachidaish\\=u and tools for the understanding of the characteristics and historical evolution of classical Japanese poetic vocabulary.: ADHO 2022 - Tokyo.
  2. 久曽神 昇. (1979). 古今和歌集 全注釈: Vols. 1–5. 講談社.
  3. 奥村 恆哉. (1978). 古今和歌集. 新潮社.
  4. 小島 憲之, &; 新井 栄蔵. (1989). 古今和歌集. 岩波書店.
  5. 小沢 正夫. (1971). 古今和歌集 (Thirteenth). 小学館.
  6. 小町谷 照彦. (1982). 古今和歌集：現代語訳対照. 旺文社.
  7. 松田 武夫. (1968). 新釈古今和歌集: Vol. 上下. 風間書房.
  8. 片桐 洋一. (1998). 古今和歌集全評釈: Vol. 上中下. 講談社.
  9. 窪田 空穂. (1960). 古今和歌集評釈: Vol. 上中下. 東京堂.
  10. 竹岡 正夫. (1976). 古今和歌集全評釈: 古注七種集成: Vol. 上下. 右文書院.
  11. 金子 元臣. (1933). 古今和歌集評釈: 昭和新版. 明治書院.

