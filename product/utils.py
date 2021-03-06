import glob
import os

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate_objects(request, objs_list):
    paginator = Paginator(objs_list, 100)
    page = request.GET.get('page')
    try:
        objs = paginator.page(page)
    except PageNotAnInteger:
        objs = paginator.page(1)
    except EmptyPage:
        objs = paginator.page(paginator.num_pages)
    return objs


def update_obj(model_obj, kwargs):
    for key, value in kwargs.items():
        setattr(model_obj, key, value)
    model_obj.save()
    return model_obj


def rm_existing_file():
    try:
        files = glob.glob(settings.BASE_DIR+'/media/*')
        for f in [file for file in files if file.endswith('.csv')]:
            os.remove(f)
    except Exception as e:
        pass
