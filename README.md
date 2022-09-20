# 高専プロコン2022競技

## セットアップ

初回はだいぶ遅いかも。

```
% pip install -r requirements.txt
```

## セットアップ : tensorflow

Nvidia Container Toolkitを使う。

Gentooでは

```
# emerge nvidia-container-toolkit
# rc-service docker restart
```

でおけ

docker runのときに`--gpus all`としてやる。

## 使い方

`$TOKEN`にトークンを設定して

```
% python3 main.py
```

とすれば動きます。
