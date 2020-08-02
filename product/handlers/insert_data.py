import csv
import logging
import os
import arrow
from django.conf import settings
from django.http import StreamingHttpResponse

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
        count = 0
        while count < 4:
            if count == 0:
                message = 'started..\n\n'
                count += 1
            elif count == 1:
                pd_data = self.create_list(filepath)
                message = 'Reading Csv File..\n\n'
                count += 1
            elif count == 2:
                Products.objects.bulk_create(pd_data, batch_size=500,
                                             ignore_conflicts=True)
                message = 'Bulk Creating into DB..\n\n'
                count += 1
            else:
                message = 'View  - {}/product/view/'.format(host)
                count += 1
            yield message

    def process_file(self, filepath, host):
        stream = self.bulk_creation(filepath, host)
        response = StreamingHttpResponse(stream, status=200, content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

    def validate_duplicate(self, sku):
        return Products.objects.filter(sku__icontains=sku).exists()

    def create_product(self, req_data):
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
        try:
            Products.objects.get(sku=sku).delete()
            return {'message': 'Deleted Successfully'}
        except Exception as e:
            logger.error('Exception-{}, sku-{}'.format(e, sku))
            return {'message': 'Unable to Delete'}

    def get_product(self, sku):
        try:
            return True, Products.objects.get(sku=sku)
        except Exception as e:
            logger.error('Exception-{}, sku-{}'.format(e, sku))
            return False, {'message': 'Unable to Fetch data'}

    def update_product(self, data):
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
