from django.shortcuts import render
from django.http import HttpResponseRedirect
from .LoLEncourage import get_result
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def view_home(request):
    if request.method == "POST":
        data_input = request.POST.get("data")

        # result_dict = get_result(data_input)

        try:
            result_dict = get_result(data_input)
        except Exception as e:
            print(e)  # エラーメッセージをコンソールに出力
            return render(request, "home.html", {"error": str(e)})

        if "result_title" in result_dict:  # エラーなしの場合

            # result_dict = { #テスト用
            # "result_title": "戦場の死神",
            # "result_peak": "kills",
            # "result_text": "あなたは最後にプレイした試合の中で誰よりも敵をキルしました",
            # "image_path": "static/LoLEncourage/images/champion/Aatrox.jpg"
            # }

            print(result_dict)
            return render(request, "result.html", {"data": result_dict})

        else:  # エラーがあった場合
            return render(request, "home.html", result_dict)
            # return render(request, 'home.html', context= {"error": "最近サモナーズリフトで行った試合が見つかりませんでした"})

    return render(request, "home.html")
