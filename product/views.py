import os

from django.conf import settings
from django.contrib import messages

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse
from product.handlers.insert_data import FileToDb

from product.models import Products
from product.utils import paginate_objects
from rest_framework.views import APIView


class FileView(APIView):
    http_method_names = ['get', 'post']

    def get(self, request):
        return render(request, 'product/upload.html')

    def post(self, request):
        file1 = request.FILES.get('attachment')
        if file1:
            file_path = self.get_file_path(file1)
            FileToDb().process_file(file_path)
        return HttpResponse('ok')

    def get_file_path(self, attachment):
        fs = FileSystemStorage()
        filename = fs.save(attachment.name, attachment)
        file_url = fs.url(filename)
        return os.path.join(settings.BASE_DIR + file_url)


class TableView(APIView):
    http_method_names = ['get']

    def get(self, request):
        objs_qs = Products.objects.all().order_by('-modified_at')
        objs = paginate_objects(request, objs_qs)
        context = {'products': objs}
        return render(request, 'product/view.html', context)


class CreateView(APIView):
    http_method_names = ['get', 'post']

    def get(self, request):
        return render(request, 'product/add.html')

    def post(self, request):
        data = request.POST.dict()
        response = FileToDb().create_product(data)
        messages.success(request, response['message'])
        arg_num = reverse('product:view')
        return HttpResponseRedirect(arg_num)


class UpdateView(APIView):
    http_method_names = ['get', 'post']

    def get(self, request):
        param = request.query_params.dict()
        if param.get('delete'):
            obj = FileToDb().delete_product(param['sku'])
        else:
            _, obj = FileToDb().get_product(param['sku'])
            if isinstance(obj, Products):
                return render(request, 'product/update.html', {'product': obj})
        messages.warning(request, obj['message'])
        arg_num = reverse('product:view')
        return HttpResponseRedirect(arg_num)

    def post(self, request):
        data = request.POST.dict()
        response = FileToDb().update_product(data)
        messages.success(request, response['message'])
        arg_num = reverse('product:view')
        return HttpResponseRedirect(arg_num)


class DeleteView(APIView):
    http_method_names = ['get', 'post']

    def get(self, request):
        # Products.objects.all().delete()
        messages.warning(request, 'Deleted Successfully')
        arg_num = reverse('index')
        return HttpResponseRedirect(arg_num)
