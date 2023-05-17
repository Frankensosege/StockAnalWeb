import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from Investar.StockMarketDB import MarketDB

def create_portpolio(request):
    user_id = request.session.get('id')
    if user_id is None or user_id=='':
        return render(request, 'common_ui/stock_man_index.html')


    return render(request, 'Investar/invest_items.html')

def total_item_count(request):
    total_count = MarketDB().get_total_item_count()

    contJson = json.dumps({'totalItems': str(total_count)})

    return HttpResponse(contJson, content_type="application/json")

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
