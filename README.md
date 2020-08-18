# narou-scraping
djangoで小説家になろうのスクレイピングをする

## init
動かすにはsettings.pyの秘密鍵を生成する必要がある([ここ](https://qiita.com/haessal/items/abaef7ee4fdbd3b218f5)の受け売り)  
ルートディレクトリで以下を実行
```zsh
python gen_secretkey.py > narou_scraping/local_settings.py
```
また、scrapy用にtwistd.pidという名前の空ファイルをルートディレクトリに作る必要がある(初回のみ)

## deploy(raspi)
### nginx
インストール
[ここ](https://emc-craft.xyz/raspberrypi/nginx-inst03/)の通りにやる
設定
```zsh
sudo ln -sfv ~/narou-scraping/deploy/nginx.conf /etc/nginx/nginx.conf
```

### ddclient
[ここ](https://qiita.com/gorohash/items/8287738ffe47ab52a36f)の通りにやる

### certbot
インストール＆設定
```zsh
sudo apt install certbot
sudo certbot certonly --standalone --agree-tos -d narou.chinokafu.dev -d scrapy.chinokafu.dev
```
更新テスト
```zsh
sudo certbot renew --dry-run
```

### 環境変数
```zsh
vim ~/.profile
```
以下を追記
```~/.profile
BASE_URL="https://narou.chinokafu.dev/"
```
再読み込み
```zsh
source ~/.profile
```

### django
インストール
```zsh
pip install -r requirements.txt
```
本番用に書き換え
```zsh
vim narou_scraping/local_settings.py
vim narou_scraping/settings.py
```
実行
```zsh
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
```
```
sudo ln -sfv ~/narou-scraping/deploy/django.service /etc/systemd/system/django.service
sudo systemctl enable django
sudo systemctl start django
```

### scrapy
```
sudo ln -sfv ~/narou-scraping/deploy/scrapyd.service /etc/systemd/system/scrapyd.service
sudo systemctl enable scrapyd
sudo systemctl start scrapyd
scrapyd-deploy
```

### node
インストール  
[ここ](https://github.com/nodesource/distributions)の通りにやる  
```zsh
npm install
npm run build
```
