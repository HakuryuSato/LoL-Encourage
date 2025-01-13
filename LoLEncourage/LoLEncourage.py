from riotwatcher import LolWatcher, RiotWatcher
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
import os
import re
import json
import requests


# Riot APIキー
api_key = settings.RIOT_API_KEY
watcher = LolWatcher(api_key)


# ファイルから結果詳細を読み込む
def open_result_detail_json():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(
        current_directory, "static", "LoLEncourage", "json", "result_detail.json"
    )

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


# Nameからpuuidを取得(ハッシュタグの有無で判断)
def get_puuid(name):
    try:  # もしエラーがあればNoneを返す
        if "#" in name:
            game_name, tag_line = name.split("#")
            region = "asia"
            url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key}"
            response = requests.get(url)
            response_data = response.json()
            return response_data["puuid"]
        else:
            summoner = watcher.summoner.by_name("jp1", name)
            return summoner["puuid"]
    except:
        return None


# ゲームIDからマッチ取得
def get_match_from_game_id(game_id):
    try:
        match_id = "JP1_" + game_id
        match = watcher.match.by_id("jp1", match_id)
        return match
    except:
        return None


# participantsデータ抽出
def get_participants_data(match):
    participants_data = match["info"]["participants"]
    return participants_data


# puuidからマッチリストを取得
def get_match_list_from_puuid(puuid):
    try:
        matchlist = watcher.match.matchlist_by_puuid("jp1", puuid)
        return matchlist
    except:
        return None


# サモリフ試合のみ抽出
def extract_classic_match(matchlist):
    for match_id in matchlist:
        match = watcher.match.by_id("jp1", match_id)
        game_mode = match["info"]["gameMode"]

        if game_mode == "CLASSIC":
            return match

    return None


# ユーザーのチャンピオン名の取得
def get_user_champion_name(participants_data, puuid):
    for participant in participants_data:
        if participant["puuid"] == puuid:
            return participant["championName"]


# ユーザーのデータの取得
def get_user_data(participants_data, puuid, game_key_list):
    for participant in participants_data:
        if participant["puuid"] == puuid:
            return {
                f"{index}_{key}": participant[key]
                for index, key in enumerate(game_key_list)
                if key in participant
            }


# マッチの全ての参加者のデータを抽出
def get_all_player_data(participants_data, game_key_list):
    return {
        user["puuid"]: {key: user.get(key, None) for key in game_key_list}
        for user in participants_data
    }


# チームのデータを抽出
def get_same_team_data(participants_data, puuid, game_key_list):
    # puuidに対応するユーザーのチームIDを取得
    my_team_id = None

    for user in participants_data:
        if user["puuid"] == puuid:
            my_team_id = user["teamId"]
            break

    # 自分と同じチームの全てのユーザーのデータを抽出
    return {
        user["puuid"]: {key: user.get(key, None) for key in game_key_list}
        for user in participants_data
        if user["teamId"] == my_team_id
    }


# 訪問者が最も高かったスコアを抽出
def get_peak_score(all_player_data, user_data, game_key_list):
    result = {}
    for key in game_key_list:  # キー(キル数やアシストなど、自分で選択した項目)でループ
        if key is None or key == "null":  # キーがない場合次のキーへ（キー名称をriotが変更した場合の対処)
            continue

        user_value = user_data[key]
        if key in user_data:
            if user_value is None: # キーの値がNoneの場合（恐らく試合で該当のスコアが無い場合はNoneになる）
                continue

            else: 
                

                max_value = max(
                    player_data[key] for player_data in all_player_data.values()
                )

            # for player_data in all_player_data.values():
            #     if player_data[key] is not None:
            #         if max_value is None or player_data[key] > max_value:
            #             max_value = player_data[key]

            if user_value >= max_value and user_value > 0:
                result[key] = user_value

    return result


# 訪問者が最も高かったスコアのタイプを取得
def get_peak_score_type(
    all_player_data, user_data, game_key_list, peak_score_in_match, peak_score_in_team
):
    if peak_score_in_match:  # マッチで1番高いスコアがある場合
        return "試合の中で誰よりも", list(peak_score_in_match.keys())[0]

    elif peak_score_in_team:  # チームで1番高いスコアがある場合
        return "チーム内で最も", list(peak_score_in_team.keys())[0]

    else:  # 何もない場合
        return "試合の中で誰よりも", None


def make_error_result(error):
    return {"error_text": error}


def get_result(summoner_name):  # メイン関数
    # 結果詳細を読み込み
    result_detail = open_result_detail_json()
    game_key_list = result_detail.keys()

    # サモナー名からPUUIDを取得, #が含まれればriot_idから取得する
    puuid = get_puuid(summoner_name)
    if puuid is None:  # PUUIDを取得出来なかった場合
        return make_error_result("サモナー名が見つかりませんでした")

    # puuidから試合リストを取得
    match_list = get_match_list_from_puuid(puuid)
    if match_list is None:  # マッチリストを取得出来なかった場合
        return make_error_result("最近サモナーズリフトで行った試合が見つかりませんでした")

    # 最後のクラシックマッチを取得
    match = extract_classic_match(match_list)
    if match_list is None:  # マッチリストを取得出来なかった場合
        return make_error_result("最近サモナーズリフトで行った試合が見つかりませんでした")

    try: #以降の処理は内部での問題になる
        # participants_dataを取得
        participants_data = get_participants_data(match)

        # 訪問者の使用キャラクター名を取得
        user_champion_name = get_user_champion_name(participants_data, puuid)

        # 全プレイヤーのデータを抽出
        all_player_data = get_all_player_data(participants_data, game_key_list)

        # 同じチームのデータを抽出
        same_team_data = get_same_team_data(participants_data, puuid, game_key_list)

        # プレイヤーのデータを抽出
        user_data = all_player_data[puuid]

        # データをマッチ全体で比較して1番高いものがないか探す
        peak_score_in_match = get_peak_score(all_player_data, user_data, game_key_list)

        # データをチーム内で比較して1番高いものがないか探す
        peak_score_in_team = get_peak_score(same_team_data, user_data, game_key_list)

        # 最も高いスコアのタイプと値を取得
        scope_type, peak_score_type = get_peak_score_type(
            peak_score_in_match,
            peak_score_in_team,
            game_key_list,
            peak_score_in_match,
            peak_score_in_team,
        )

        result_title = result_detail[peak_score_type]["title"]
        result_peak = peak_score_type
        result_text = (
            "あなたは最後にプレイした" + scope_type + result_detail[peak_score_type]["description"]
        )

        static_root = settings.STATIC_ROOT
        print(static_root)

        image_path = (f'static/LoLEncourage/images/champion/{user_champion_name}.jpg')
        print(image_path)


        
        # print(hashed_image_path)
        # print(user_champion_name)
        # print(result_title)
        # print(result_text)

        return {
            "result_title": result_title,
            "result_peak": result_peak,
            "result_text": result_text,
            "image_path": image_path,
        }
    except:
        return make_error_result("何らかのエラーが発生しました")


# 12/07 API障害？アプデ？ puuid取得でエラーになる、08に再度実行してテスト
# jas = "jasper#7se"
# test_data = watcher.league.by_id("jp1", "jasper")
# print(test_data)

# dict = get_result("LUL#JP1")
# print(dict)