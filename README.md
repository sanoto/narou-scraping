# narou-scraping
djangoで小説家になろうのスクレイピングをする

## init
動かすにはsettings.pyの秘密鍵を生成する必要がある([ここ](https://qiita.com/haessal/items/abaef7ee4fdbd3b218f5)の受け売り)  
ルートディレクトリで以下を実行
```zsh
python gen_secretkey.py > narou_scraping/local_settings.py
```
また、scrapy用にtwistd.pidという名前の空ファイルをルートディレクトリに作る必要がある(初回のみ)
