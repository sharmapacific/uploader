from django.conf.urls import url
from product.views import (
                    CreateView,
                    DeleteView,
                    FileView,
                    TableView,
                    UpdateView
                )

app_name = 'product'

urlpatterns = [
    url(r'^upload/$', FileView.as_view(), name='upload'),
    url(r'^view/$', TableView.as_view(), name='view'),
    url(r'^create/$', CreateView.as_view(), name='create'),
    url(r'^update/$', UpdateView.as_view(), name='update'),
    url(r'^delete/$', DeleteView.as_view(), name='delete'),
]
