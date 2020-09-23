import csv
import logging
import os
import webbrowser
import arrow
import threading

from django.conf import settings
from django.http import StreamingHttpResponse

from product.constants import Stream
from product.models import Products
from product.utils import update_obj


logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(settings.LOG_DIR) + '/insert_data.log',
    format='%(asctime)s - [%(levelname)s] - %(app)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
)
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, {'app': 'product'})


class FileToDb:
    def create_list(self, filepath):
        """
        Putting all csv content in list for bulk_create
        """
        pd_list = []
        with open(filepath, 'r', encoding='ascii', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            created_at = arrow.utcnow().datetime
            for row in reader:
                pd_list.append(Products(
                    name=row['name'],
                    sku=row['sku'],
                    description=row['description'],
                    created_at=created_at,
                    modified_at=created_at,
                ))
        return pd_list

    def bulk_creation(self, filepath, host):
        """
        bulkcreation as well returning live streaming
        """
        status = 0
        while status < Stream.STREAM_LIMIT:
            if status == Stream.STARTED:
                message = 'Started..\n\n'
                status += 1
            elif status == Stream.CSV_LIST:
                pd_data = self.create_list(filepath)
                message = 'Reading Csv File..\n\n'
                status += 1
            elif status == Stream.BULK_CREATE:
                Products.objects.bulk_create(pd_data, batch_size=500,
                                             ignore_conflicts=True)
                message = 'Bulk Creating into DB..\n\n'
                status += 1
            else:
                message = 'Data insertion Done. \n\nView  - {}/product/view/'.format(host)
                status += 1
            yield message

    def process_file(self, filepath, host):
        """
        Processor function for insert csv into DB
        """
        stream = self.bulk_creation(filepath, host)
        response = StreamingHttpResponse(stream, status=200, content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

    def skip_streaming(self, filepath):
        """
        skip live stream in case of large file
        """
        pd_data = self.create_list(filepath)
        Products.objects.bulk_create(pd_data, batch_size=500,
                                     ignore_conflicts=True)
        return {'message': 'process'}

    def async_upload(self, filepath):
        """
        asynchronously uploading csv
        """
        threading.Thread(target=self.skip_streaming, args=(filepath,)).start()
        return {'message': 'Csv Uploading asynchronously..'}

    def validate_duplicate(self, sku):
        """
        validating if sku exists already in DB
        """
        return Products.objects.filter(sku__icontains=sku).exists()

    def create_product(self, req_data):
        """
        Creating a new product after duplication validation
        """
        if self.validate_duplicate(req_data['sku']):
            return {'message': 'SKU already exists'}
        try:
            data = {
                'sku': req_data['sku'],
                'name': req_data.get('name', ''),
                'description': req_data.get('description', ''),
                'modified_at': arrow.utcnow().datetime
                }
            Products.objects.create(**data)
            return {'message': 'Product has been added Successfully'}
        except Exception as e:
            logger.error('Exception-{}, data-{}'.format(e, req_data))
            return {'message': 'Unable to create'}

    def delete_product(self, sku):
        """
        To delete a product from database
        """
        try:
            Products.objects.get(sku=sku).delete()
            return {'message': 'Deleted Successfully'}
        except Exception as e:
            logger.error('Exception-{}, sku-{}'.format(e, sku))
            return {'message': 'Unable to Delete'}

    def get_product(self, sku):
        """
        Retrieve record from DB
        """
        try:
            return True, Products.objects.get(sku=sku)
        except Exception as e:
            logger.error('Exception-{}, sku-{}'.format(e, sku))
            return False, {'message': 'Unable to Fetch data'}

    def update_product(self, data):
        """
        Updating Product in database
        """
        try:
            pd_obj, _ = self.get_product(data['sku'])
            if pd_obj:
                data = {
                    'sku': data['sku'],
                    'name': data.get('name', ''),
                    'description': data.get('description', ''),
                    'modified_at': arrow.utcnow().datetime
                }
                update_obj(_, data)
                return {'message': 'Updated Successfully'}
        except Exception as e:
            logger.error('Exception-{}, data-{}'.format(e, data))
            return {'message': 'Unable to Update'}
