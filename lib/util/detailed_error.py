"""
最後に起こったエラーを詳細に文字列として出力する
"""
import sys, traceback


def get_error():

    # エラーの情報をsysモジュールから取得
    info = sys.exc_info()

    # tracebackモジュールのformat_tbメソッドで特定の書式に変換
    tbinfo = traceback.format_tb( info[2] )

    # 整形
    detailed_error = ""
    for tb in tbinfo:
        detailed_error += tb
        detailed_error += "\n"

    return detailed_error
