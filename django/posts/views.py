import re
from django.shortcuts import render
from django.http import HttpResponse
from elastic_search import search


def index(request):
    if request.method == 'POST': # 만약 요청 방식이 POST라면
        return_dict = {}


        all_search = request.POST.get('all_search')
        

        category = request.POST.get('category')


        region = request.POST.get('region')


        salary = request.POST.get('salary')
        


        res_list = search(all_search = all_search, category = category, region = region, salary = salary)

        return render(request, 'posts/result.html', {'res_len': len(res_list),'res_list': res_list})
    else: # 만약 요청 방식이 GET이라면
        return render(request, 'posts/search_form.html') 