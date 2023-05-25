import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from Utilities.StockMarketDB import MarketDB

# Create your views here.
def item_admin(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'MlStockAdmin/invest_item_man.html', {'user': cur_user})

def total_item_count(request):
    total_count = MarketDB().get_total_invest_item_count()

    contJson = json.dumps({'totalItems': str(total_count)})

    return HttpResponse(contJson, content_type="application/json")

def get_paged_item(request):
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        items = MarketDB().get_invest_items(start=offset, ret_items=limit)

        item_list = []
        for _, item in items.iterrows():
            item_list.append({'code': item.code, 'company': item.company})

        return HttpResponse(json.dumps(item_list), content_type="application/json")
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

def save_item_price(request):
    cur_user = request.user
    if request.method == 'POST':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        start_date = invitems['start_date']
        items = invitems['item_list']
        prepSQL = MarketDB()
        if len(items) <= 0:
            items_df = prepSQL.get_invest_items(user_id=None, start=0, ret_items=0)
            for r in items_df.itertuples():
                items.append(r[1] + ' ' + r[2])

        ret =prepSQL.update_daily_price(start_date, items)

        if ret is not None:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return HttpResponse(contJson, content_type="application/json")

def item_fss(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'MlStockAdmin/item_fss_man.html', {'user': cur_user})

def save_item_fss(request):
    cur_user = request.user
    if request.method == 'POST':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        start_date = invitems['start_date']
        fs_sheet = invitems['fs_sheet']
        items = invitems['item_list']
        prepSQL = MarketDB()
        if len(items) <= 0:
            items_df = prepSQL.get_invest_items(user_id=None, start=0, ret_items=0)
            for r in items_df.itertuples():
                items.append(r[1] + ' ' + r[2])

        ret = prepSQL.update_item_fss(start_date, fs_sheet, items)

        if ret is not None:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return HttpResponse(contJson, content_type="application/json")

def item_learn(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'MlStockAdmin/invest_item_learn.html', {'user': cur_user})

def save_item_learn(request):
    cur_user = request.user
    if request.method == 'POST':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        start_date = invitems['start_date']
        end_date = invitems['end_date']
        items = invitems['item_list']
        prepSQL = MarketDB()
        if len(items) <= 0:
            items_df = prepSQL.get_invest_items(user_id=None, start=0, ret_items=0)
            for r in items_df.itertuples():
                items.append(r[1] + ' ' + r[2])

        ret = prepSQL.create_learn_schedule(start_date, end_date, items)

        if ret is not None:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return HttpResponse(contJson, content_type="application/json")

