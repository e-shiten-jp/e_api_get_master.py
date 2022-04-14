# -*- coding: utf-8 -*-

# Copyright (c) 2022 Tachibana Securities Co., Ltd. All rights reserved.
# 2022.04.12, yo.

# Python 3.6.8 / centos7.4
# API V4r2で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして、マスターをダウンロードし、ログアウトします。
#
# ご注意 ===============================
# マスターダウンロードは、非常に負荷のかかる処理です。
# なるべく立ち会時間以外の運用をお願い致します。
# ======================================

import urllib3
import datetime
import json
import time


# システム時刻を"p_sd_date"の書式の文字列で返す。
# 書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.int_p_no = 0           # request通番
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        
    def set_property(self, my_sUrlRequest, my_sUrlEvent, my_sZyoutoekiKazeiC, my_sSecondPassword):
        self.sUrlRequest = my_sUrlRequest     # request用仮想URL
        self.sUrlEvent = my_sUrlEvent         # event用仮想URL
        self.sZyoutoekiKazeiC = my_sZyoutoekiKazeiC          # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = my_sSecondPassword    # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照



# URLエンコード文字の変換
#
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： request文字列を作成し返す。
# 戻り値： 文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された'sUrlRequest'の値（仮想url）をセット。
# 第３引数： requestを投げるとき1カウントアップする。参照渡しで値を引き継ぐため、配列として受け取る。
# 第４引数： 'p_no'、'p_sd_date'以外の要求項目がセットされている必要がある。クラスの配列として受取る。
def func_make_url_request(auth_flg, url_target, class_cust_property, work_class_req) :
    class_cust_property.int_p_no += 1
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
    
    work_url = url_target
    if auth_flg == True :
        work_url = work_url + 'auth/'
    
    work_url = work_url + '?{\n\t'
    work_url = work_url + '"p_no":' + func_check_json_dquat(str(class_cust_property.int_p_no)) + ',\n\t'
    work_url = work_url + '"p_sd_date":' + func_check_json_dquat(str_p_sd_date) + ',\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            work_url = work_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    work_url = work_url[:-3] + '\n}'
    return work_url



# 機能： 通常のrequest用。APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された'sUrlRequest'の値（仮想url）をセット。
# 第３引数： requestを投げるときは、1カウントアップする（func_make_url_request関数内で実行）。参照渡しで値を引き継ぐため、配列として受け取る。
# 第４引数： 'p_no'、'p_sd_date'以外の要求項目がセットされている必要がある。クラスの配列として受取る。
def func_api_req(auth_flg, url_target, class_cust_property, work_class_req):
    work_url = func_make_url_request(auth_flg, url_target, class_cust_property, work_class_req)  # ログインは第１引数にTrueをセット
    print('送信文字列＝')
    print(work_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', work_url)
    print("req.status= ", req.status )


    # 取得したデータがbytes型なので、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数：アクセスするurl（'auth/'以下は付けない）、ユーザーID、パスワード、class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(url_base, my_userid, my_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    req_item = [class_req()]   
    
    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = my_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = my_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    json_return = func_api_req(True, url_base, class_cust_property, req_item)  
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    return json_return



# 機能： ダウンロード用の接続。APIに接続しマスターダウンロードを開始する。
# 引数1： Loginフラグ（マスターダウンロードの場合、False）
# 引数2： 接続先URL（マスターダウンロードの場合、request用URL）
# 引数3： 顧客属性クラス
# 引数4： 要求項目のデータセット
# 引数5： 保存するマスターのファイル名
# 備考： 通常のrequestの接続とは異なる接続。ストリーミングでの接続。
def func_api_req_download(auth_flg, url_target, class_cust_property, work_class_req, str_master_filename):
    
    work_url = func_make_url_request(auth_flg, url_target, class_cust_property, work_class_req)  # ログインは第１引数にTrueをセット
    print('送信文字列＝')
    print(work_url)  # 送信する文字列

    # マスターの終端文字列をセット
##    byte_terminated_string = b'"CLMEventDownloadComplete"\n}\n'
##    byte_terminated_string = byte_terminated_string[-28:-4]       # sJsonOfmit=4 の場合

    print('マスターダウンロード開始')
    print('データが大きいため時間がかかります。')
    print('約21MB。')

    
    # APIに接続
    http = urllib3.PoolManager()

    # ストリーム形式で接続（** 重要 **）
    resp = http.request(
        'GET',
        work_url,
        preload_content=False)
    
    with open(str_master_filename, 'w') as f:
        for chunk in resp.stream(2048):
            str_chunk = chunk.decode('shift-jis', errors = 'replace')
            if str_chunk[-1:] == '}' :
                str_chunk = str_chunk + '\n'

            f.write(str_chunk)

            json_chunk = json.loads(str_chunk)
            if json_chunk.get('sCLMID') == 'CLMEventDownloadComplete' :
##            if chunk[-26:-2] == byte_terminated_string :      # json形式にしない場合。sJsonOfmit=4 の場合。
                print()
                print('最終chunk=',chunk)
                print('terminate_string=',chunk[-26:-2])
                f.close()
                break

    resp.release_conn()
    
    return resp.data





# 機能： マスターダウンロード
# 引数1：str_master_filename ダウンロードしたマスターデータを保存するファイル名
# 引数2：class_cust_property（口座属性クラス）
# 返値： 無し（''）
def func_get_master(str_master_filename, class_cust_property):
    # 送信項目の解説は、マニュアル、（2）インタフェース概要の「立花証券・ｅ支店・ＡＰＩ、インタフェース概要」
    # p7/10 sd 5.マスタダウンロード を参照してください。

    req_item = [class_req()]
    
    str_key = 'sCLMID'
    str_value = 'CLMEventDownload'  # 。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '4'    # ファイル保存後の処理を考え、”4”を指定。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # マスターデータ取得専用のAPI呼び出し
    json_return = func_api_req_download(False, class_cust_property.sUrlRequest, class_cust_property, req_item, str_master_filename)
    # マスターの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。

    return json_return




# ログアウト
# 引数：class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]   

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    # req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    json_return = func_api_req(False, class_cust_property.sUrlRequest, class_cust_property, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    return json_return




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================


# --- 利用時に変数を設定してください -------------------------------------------------------

# デモ環境（新バージョンになった場合、適宜変更）
# 現在、メンテナンス待ちのため、ご利用できません。
#url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
url_base = 'https://kabuka.e-shiten.jp/e_api_v4r2/'

my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える



# 出力するマスターデータのファル名を指定する。
str_master_filename = './master.txt'
    


# --- 以上設定項目 -------------------------------------------------------------------------


# int_p_no = [0]      # request通番
class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワードのURLエンコードをチェックして変換
work_userid = func_replace_urlecnode(my_userid)
work_passwd = func_replace_urlecnode(my_passwd)
work_2pwd = func_replace_urlecnode(my_2pwd)


print('-- login -----------------------------------------------------')
## 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」に記載のログイン例
## 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/auth/?{"p_no":"1","p_sd_date":"2020.11.07-13:46:35.000",'
## '"sCLMID":"CLMAuthLoginRequest","sPassword":"xxxxxx","sUserId":"xxxxxxxx","sJsonOfmt":"5"}'
##
# 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。


# ログイン処理
json_return = func_login(url_base, work_userid, work_passwd,  class_cust_property)
# 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

my_p_error = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
if my_p_error ==  0 :    # ログインエラーでない場合
    my_sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
    my_sSecondPasswordOmit = json_return.get('sSecondPasswordOmit')
    my_sUrlRequest = json_return.get('sUrlRequest')     # request用仮想URL
    my_sUrlEvent = json_return.get('sUrlEvent')         # event用仮想URL

    # 口座属性クラスに取得した値をセット
    class_cust_property.set_property(my_sUrlRequest, my_sUrlEvent, my_sZyoutoekiKazeiC, work_2pwd)

else :  # ログインに問題があった場合
    my_sUrlRequest = ''     # request用仮想URL
    my_sUrlEvent = ''       # event用仮想URL


if len(my_sUrlRequest) > 0 and len(my_sUrlEvent) > 0 :  # ログインOKの場合

    print()
    print('-- マスター 取得 -------------------------------------------------------------')

    json_return = func_get_master(str_master_filename, class_cust_property)
    # マスターの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。
    # カレントディレクトリに「str_master_filename」で指定した名前でファイルを作成する。
    
    
    
    print()
    print('-- logout -------------------------------------------------------------')
    ## マニュアルの解説「（２）ログアウト」
    ##        {
    ##　　　　　"p_no":"2",
    ##　　　　　"p_sd_date":"2020.07.01-10:00:00.100",
    ##　　　　　"sCLMID":"CLMAuthLogoutRequest"
    ##　　　　}
    ##
    ##　　　要求例：
    ##　　　　仮想ＵＲＬ（REQUEST）/?{"p_no":"2","p_sd_date":"2020.07.01-10:00:00.100","sCLMID":"CLMAuthLogoutRequest"}

    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
   # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    json_return = func_logout(class_cust_property)

    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。
    print('p_no= ', json_return.get("p_no"))
    print('sCLMID= ', json_return.get("sCLMID"))
    print('sResultCode= ', json_return.get('sResultCode'))  # 業務処理.エラーコード 0:正常、5桁数字:「結果テキスト」に対応するエラーコード
    
else :
    print('ログインに失敗しました')


                   
