# -*- coding: utf-8 -*-

# Copyright (c) 2022 Tachibana Securities Co., Ltd. All rights reserved.
# 2022.04.12, yo.

# Python 3.6.8 / centos7.4
# API V4r2で動作確認

# おまけ
#
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ダウンロードしたマスターから、日付け情報の営業日（当日）、営業日（翌日）を取得します。

# マスターの「CLMDateZyouhou」については、
# APIマニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」の
# p8/43「２－２．日付情報」を参照ください。

# 営業日の考え方は、
# APIマニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」の15ページ以降に
# 「2-4-1.資料_株式タイムテーブル」として記載させていただいております。

import urllib3
import datetime
import json
import time


# request項目を保存するクラス。配列として使う。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)



# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    work_key = ''
    work_value = ''
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
                str_json_data = str_json_data + work_class_req[i].str_key \
                                    + ':' + func_strip_dquot(work_value) \
                                    + ',\n\t'
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)
                str_json_data = str_json_data + func_check_json_dquat(work_class_req[i].str_key) \
                                    + ':' + work_value \
                                    + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('ファイルに書き込めません!!!  ファイル名：',str_fname_output)
        print(type(e))





# 一括ダウンロードしたマスターデータのファル名。
str_master_filename = './master.txt'
# 営業日をjson形式で保存するファイル名。
str_fname_output = './eigyou_day.txt'

# --------------------------------------------------

# おまけ。 営業日を取得し「str_fname_output」に保存する。
req_item = [class_req()]
try:
    str_shiftjis = ''
    str_key = 'CLMDateZyouhou'
    my_eigyouday = ''

    with open(str_master_filename, 'r', encoding = 'shift-jis', errors = 'replace') as fin:
        while True:
            str_shiftjis = fin.readline()

            if not len(str_shiftjis) :
                break

##            if str_shiftjis[39:64] == '"sCLMID":"CLMDateZyouhou"' :
            json_shiftjis = json.loads(str_shiftjis)
            if json_shiftjis.get('sCLMID') == str_key :
                print(str_shiftjis)
                print('営業日（当日）sDayKey: ', json_shiftjis.get('sDayKey'))
                print('営業日（当日）sTheDay: ', json_shiftjis.get('sTheDay'))
                print('営業日（翌日）sYokuEigyouDay_1: ', json_shiftjis.get('sYokuEigyouDay_1'))
                
                str_key = '"sDayKey"'
                str_value = json_shiftjis.get('sDayKey')
                #req_item.append(class_req())
                req_item[-1].add_data(str_key, str_value)

                str_key = '"sTheDay"'
                str_value = json_shiftjis.get('sTheDay')
                req_item.append(class_req())
                req_item[-1].add_data(str_key, str_value)

                str_key = '"sYokuEigyouDay_1"'
                str_value = json_shiftjis.get('sYokuEigyouDay_1')
                req_item.append(class_req())
                req_item[-1].add_data(str_key, str_value)

                my_eigyouday = func_make_json_format(req_item)
                func_write_to_file(str_fname_output, my_eigyouday)

except IOError as e:
    print('File Not Found!!!')
    print(type(e))
    #print(line)


