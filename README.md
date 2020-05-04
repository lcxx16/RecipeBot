## Module
* Heroku
  * Procfile
    * heroku で最初に呼び出されるモジュールを設定
  * requirements.txt
    * heroku でインストールするパッケージを設定
  * runtime.txt
    * herokuで実行するプログラム言語・バージョンを設定

* LineBot
  * callback.py
    * LineMessagingAPIからのWebHookを処理するモジュール
  * handler.py
    * callbackから受け取ったデータを処理し、observerを呼び出すモジュール
  * observer.py
    * handlerから受け取ったデータを利用しDB更新・メッセージ返信をするモジュール
  * push.py
    * 賞味期限切れレコードの削除と賞味期限通知を行うJobモジュール
  * setting.py
    * プログラムで使用する定数・設定を定義するモジュール
 
* Setup - DataBase
  * CREATE TABLE
    * createTable_user.sql
      * ユーザ情報を保持するテーブル
    * createTable_status.sql
      * 会話の位置を保持するテーブル
    * createTable_product.sql
      * 登録処理で記録する商品テーブル
    * createTable_product_archive.sql
      * 削除された商品を記録するテーブル
    * createTable_recipe.sql
      * 楽天レシピAPIから取得したレシピを保持するテーブル
    * createTable_inverted_index.sql
      * 検索用の転置インデックスを保持するテーブル
    * createTable_category.sql
      * 初期構築時に使用したレシピカテゴリーを保持するテーブル(ver1.0では使用しない)
    
  * CREATE TRIGGER
    * create_process_backup.sql
      * 商品がDELETEされた際にarchiveテーブルにINSERTするトリガ
  
  * INSERT
    * insert_recipe.sql
      * 楽天レシピAPIから取得したレシピデータ
    * insert_inverter_index.sql
      * 名詞形のみを抜粋した転置インデックス
    * insert_inverter_index_full.sql
      * 全品詞で作成した転置インデックス(ver1.0では使用しない)
    * insert_category.sql
      * 楽天レシピAPIから取得したカテゴリーデータ
  
* Setup - Script
  * collect_recipe.py
    * 楽天レシピAPIからレシピを取得するスクリプト
  * inverted_index_by_mecab.py
    * MeCabで転置インデックスを作成した際に使用したスクリプト
  * inverted_index_by_ngram.py
    * bi-gramで転置インデックスを作成した際に使用したスクリプト(ver1.0は形態素解析を採用したためNgramは使用しない)
  * collect_category.py
    * 楽天レシピAPIからカテゴリを取得した際に使用したスクリプト

## System
* Platform
  * Heroku
* Database
  * Heroku Postgres
* Scheduler
  * Heroku Scheduler
  

***
Author : d.matsumoto<br>
Release : 2020/05<br>
Update : 2020/05
***
