# 高専プロコン2022競技

## 学習環境 - セットアップ

Docker Desktop使ってる人は何もしなくて良い。

Nvidia Container Toolkitを使う。

Gentooでは

```
# emerge nvidia-container-toolkit
# rc-service docker restart
```

とする。

## 学習環境 - 使い方

docker runのときに`--gpus all`としてやる。

```
% docker build -t procon22 .
% docker run --rm -it --gpus all -v $(pwd)/train:/work/train procon22
```

## 学習環境 - デバッグ

```
% docker run -it --gpus all -v $(pwd)/src-training:/work -v $(pwd)/train:/work/train --entrypoint bash procon22
```

## 回答環境 - セットアップ

初回はだいぶ遅いかも。

```
% pip install -r requirements.txt
```

## 回答環境 - 使い方

`TOKEN`にトークンを設定して，`HOST`に競技用サーバーのホスト名を設定したら

```
% python3 main.py
```

で動く。

## 学習環境 - 掃除

```
% docker system prune
```

で掃除する

## ファイル転送の行い方(任意のローカルディレクトリで)

```bash
$ scp -r oooo@oo.oo.ooo.ooo:~/Desktop/Procon22-Solver/ ./fromA/
```

もしくは任意のディレクトリで相手のPCから移してきてもよいかもしれない

## バックアップするために必要なコマンド集
※procon-contがある前提
```
$ docker run --rm -v procon-cont:/work -v $(pwd)/backup:/backup alpine tar cvf /backup/backup.tar /work
```

### 展開する
```bash
$ tar -xvf ./backup/backup.tar
```

これでバックアップが完了する

### メモ
```bash
$ docker volume create procon-cont
```

