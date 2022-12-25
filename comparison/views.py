from django.shortcuts import render, redirect
from product.models import Product


def comparce(request):
    com = request.session.get('comparison')
    goods_item = Product.objects.filter(id__in=(item['id'] for item in com))
    content = {'goods_item': goods_item}
    return render(request, 'product/comparison.html', content)


def add(request, id):
    if request.method == 'POST':
        if not request.session.get('comparison'):
            request.session['comparison'] = list()
        else:
            request.session['comparison'] = list(request.session['comparison'])
        item_exist = next((item for item in request.session['comparison'] if item['type'] == request.POST.get('type')
                           and item['id'] == 'id'), False)
        add_data = {
                'type': request.POST.get('type'),
                'id': id
            }
        if not item_exist:
            request.session['comparison'].append(add_data)
            request.session.modified = True
            print(request.session['comparison'])
    return redirect('/')


def remove_comparison(request, id):
    if request.method == 'POST':
        for item in request.session['comparison']:
            if item['id'] == id and item['type'] == request.POST.get('type'):
                item.clear()
                while {} in request.session['comparison']:
                    request.session['comparison'].remove({})
                if not request.session['comparison']:
                    del request.session['comparison']
        request.session.modified = True
    return redirect('/')


def delete_comparison(request):
    if request.session.get('comparison'):
        del request.session['comparison']
    return redirect('/')
