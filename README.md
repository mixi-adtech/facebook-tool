### 環境構築

[参考](https://python-guide-ja.readthedocs.org/en/latest/starting/install/osx/)

##### pythonとpipのインストール

```
$ brew install python --framework
```

#### git clone

```
$ git clone git@github.com:mixi-adtech/facebook-tool.git
$ cd facebook-tool
```

##### Virtualenvのインストール

```
$ pip install virtualenv
```

### 開発してみる

参考：[Flaskのドキュメント](http://flask-docs-ja.readthedocs.org/en/latest/)

#### 仮想環境を立ち上げるまで

仮想環境の構築
```
$ virtualenv env
```

仮想環境をアクティベートする
```
$ source env/bin/activate
```

必要なパッケージをまとめてインストール
```  
pip install -r config/requirements.txt
```

`config/config.json.example` に有効な値を入れる  

`config/config.json.example` を `config/config.json` にリネーム
```
$ mv config.json.example config.json
```

立ち上げる
```
$ python app.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 ...
```

`http://127.0.0.1:5000` にアクセスすると、管理ツールにアクセスできる。

##### 新しいライブラリを導入したら
`config/requirements.txt` を更新する。
```
pip freeze -l > config/requirements.txt
```
