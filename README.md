## RecipeLineBot

#### 設定ファイル<br>
* Heroku
  * <details><summary>Procfile</summary> heroku で最初に呼び出されるモジュールを設定</details>
  * <details><summary>requirements.txt</summary> heroku でインストールするパッケージを設定</details>
  * <details><summary>runtime.txt</summary> herokuで実行するプログラム言語・バージョンを設定</details>

#### モジュール<br>
* Main
  * <details><summary>callback.py</summary> LineからのWebHookを処理するモジュール</details>

* Subject
  * <details><summary>abstract_handler.py</summary> callbackから受け取ったデータを処理し、observerを呼び出す抽象モジュール</details>
  * <details><summary>follow_handler.py</summary> Followイベントのハンドラー</details>
  * <details><summary>unfollow_handler.py</summary> UnFollowイベントのハンドラー</details>
  * <details><summary>register_handler.py</summary> 商品登録イベントのハンドラー</details>
  * <details><summary>return_handler.py</summary> 一覧、レシピ、webイベントのハンドラー</details>

* Observer
  * <details><summary>abstract_observer.py</summary> handlerから受け取ったデータをDB登録・メッセージ返信する抽象モジュール</details>
  * <details><summary>follow_observer.py</summary> Followイベントのオブザーバー</details>
  * <details><summary>unfollow_observer.py</summary> UnFollowイベントのオブザーバー</details>
  * <details><summary>register_observer.py</summary> 商品登録イベントのオブザーバー</details>
  * <details><summary>return_observer.py</summary> 一覧、レシピ、webイベントのオブザーバー</details>

* Database
  * <details><summary>setting.py</summary> SQLalchemyの設定モジュール</details>
  * <details><summary>dto.py</summary> SQLalchemyのテーブルクラス定義モジュール</details>

* Util
  * <details><summary>const.py</summary> プログラムの定数定義モジュール</details>

***
Author : d.matsumoto<br>
Release : 2020/04<br>
Update : 2020/04
