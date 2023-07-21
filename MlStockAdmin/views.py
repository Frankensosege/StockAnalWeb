import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from Utilities.StockMarketDB import MarketDB
from Utilities.TrainModel import MLStockRNN
from Utilities.VisualUtil import plotter
from datetime import datetime

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

        if str(type(limit))=="<class 'str'>":
            limit = int(limit)
        if str(type(offset))=="<class 'str'>":
            offset = int(offset)

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
                items.append(r[1] + ': ' + r[2])

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
                items.append(r[1] + ': ' + r[2])

        ret = prepSQL.create_learn_schedule(start_date, end_date, items)

        if not ret:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return HttpResponse(contJson, content_type="application/json")

def item_learn_model(request):
    cur_user = request.user
    if request.method == 'POST':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        start_date = invitems['start_date']
        end_date = invitems['end_date']
        items = invitems['item_list']

        ret_loss=''
        for item in items:
            code, company = item.split(':')

            ret_loss += item + '--> '
            model = MLStockRNN(code)
            loss = model.train_model(datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date())
            ret_loss += str(loss) + '\n'

        contJson = {'result': ret_loss}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return JsonResponse(contJson, content_type="application/json")

def item_prediction(request):
    decision = ['매수', '매도', '관망']
    cur_user = request.user
    if request.method == 'POST':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        invitems = json.loads(request.body)

        items = invitems['item_list']

        ret_str = ''
        for item in items:
            code, company = item.split(':')
            model = MLStockRNN(code)
            ret_str += item + '\n'

            pred = model.predict()
            for idx, prd in enumerate(pred[0]):
                prd_str = "{0:.2f}%".format(prd * 100)
                ret_str += '\t' + decision[idx] + ' : ' + prd_str + '\n'

        #     pred_list = {}
        #     item_pred['company'] = company.strip()
        #     for idx, prd in enumerate(pred[0]):
        #         prd_str = "{0:.2f}%".format(prd * 100)
        #         pred_list.update({decision[idx]:prd_str})
        #
        #     item_pred["pred"] = pred_list
        #
        contJson = {'result': ret_str}

        print(contJson)
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return JsonResponse(contJson, content_type="application/json")

def anal_tool_man(request):
    cur_user = request.user
    # user_id = request.session.get('id')
    if not cur_user.is_authenticated:
        return render(request, 'common_ui/stock_man_index.html')

    return render(request, 'MlStockAdmin/anal_tool_man.html', {'user': cur_user})

def total_tool_count(request):
    total_count = MarketDB().get_total_tool_count()

    contJson = json.dumps({'totalItems': str(total_count)})

    return HttpResponse(contJson, content_type="application/json")

def get_paged_tool(request):
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        items = MarketDB().get_tools(start=offset, ret_items=limit)

        item_list = []
        for _, item in items.iterrows():
            item_list.append({'tool_id': item.tool_id, 'tool_nm': item.tool_nm, 'tool_method': item.tool_method, 'img_prefix': item.img_prefix})

        return HttpResponse(json.dumps(item_list), content_type="application/json")
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

def save_tool(request):
    save_item = {}
    if request.method == 'GET':
        save_item['tool_id'] = request.GET.get('tool_id')
        save_item['tool_nm'] = request.GET.get('tool_nm')
        save_item['tool_method'] = request.GET.get('tool_method')
        save_item['img_prefix'] = request.GET.get('img_prefix')

        print(save_item)

        prepSQL = MarketDB()
        ret = prepSQL.save_tool(save_item)

        if not ret:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}

    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return JsonResponse(contJson, content_type="application/json")

def delete_tool(request):
    if request.method == 'GET':
        selitem = request.GET.get('tool_id')

        tool_id, tool_nm = selitem.split(':')

        prepSQL = MarketDB()
        ret = prepSQL.delete_tool(tool_id)

        if not ret:
            contJson = {'result': ret}
        else:
            contJson = {'result': 'success'}

    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return JsonResponse(contJson, content_type="application/json")

def show_tool(request):
    cur_user = request.user
    if request.method == 'GET':
        if not cur_user.is_authenticated:
            return render(request, 'common_ui/stock_man_index.html')

        # tool_data = json.loads(request.body)

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        tool_id, tool_nm = request.GET.get('tool_id').split(":")
        item_code = request.GET.get('item_code')

        prepSQL = MarketDB()
        tool = prepSQL.get_tools(tool_id=tool_id)
        # hloc = prepSQL.get_hloc(item_code, date_from=start_date, date_to=end_date, is_train=True)

        plt = plotter([tool.loc[0]["tool_nm"]])
        drawFnc = getattr(plt, tool.loc[0]["tool_method"])
        plt.draw_graphs([drawFnc], item_code, date_from=start_date, date_to=end_date, is_train=True)
        # plt.draw_graphs([tool.loc[0]["tool_method"]], hloc)
        contJson = {'result': 'success'}
    else:
        error = '요청경로가 올바르지 않습니다.'
        return JsonResponse({'error': error})

    return JsonResponse(contJson, content_type="application/json")