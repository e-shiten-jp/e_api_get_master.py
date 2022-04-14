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


# 出力するマスターデータのファル名を指定する。
str_master_filename = './master.txt'
    



# おまけ。 営業日を取得。
try:
    str_shiftjis = ''
    str_key = 'CLMDateZyouhou'    

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
                

except IOError as e:
    print('File Not Found!!!')
    print(type(e))
    #print(line)


