import json
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from Utilities.StockMarketDB import MarketDB

def create_portpolio(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'Investar/invest_items.html', {'user': cur_user})

def total_item_count(request):
    total_count = MarketDB().get_total_item_count()

    contJson = json.dumps({'totalItems': str(total_count)})

    return HttpResponse(contJson, content_type="application/json")

def retrieve_portpolio(request):
    if request.method == 'GET':
        user_id = request.session.get('id')

        if user_id is None or user_id == '':
            return render(request, 'common_ui/stock_man_index.html')
        items = MarketDB().get_invest_items(user_id)

        item_list = []
        for _, item in items.iterrows():
            item_list.append({'code': item.code, 'company': item.company})

        return HttpResponse(json.dumps(item_list), content_type="application/json")
    else:
        messages.error(request, '유효한 사용자가 아닙니다.')


def get_paged_item(request):
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        items = (MarketDB().get_comp_info(start=offset, ret_items=limit))

        item_list = []
        for _, item in items.iterrows():
            item_list.append({'code': item.code, 'company': item.company})

        return HttpResponse(json.dumps(item_list), content_type="application/json")
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

def save_investitem(request):
    cur_user = request.user
    if request.method == 'POST':
        # user_id = request.session.get('id')
        # if user_id is None or user_id == '':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        ret = MarketDB().create_invitem_list(cur_user.id, invitems)
        if ret is not None:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return HttpResponse(contJson, content_type="application/json")

def tool_man(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'Investar/user_tool_man.html', {'user': cur_user})

