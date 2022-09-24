# 高専プロコン2022競技

## 学習環境 - セットアップ

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
% docker run -it --gpus all -v $(pwd)/train:/work/train procon22
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
