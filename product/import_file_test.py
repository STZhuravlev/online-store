import os
import json
import django
import logging

from typing import Any

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from product.models import Product, Category, Property, ProductImage, Offer
from shop.models import Seller
from users.models import CustomUser


file_log = logging.FileHandler(os.path.abspath(
    os.path.join('../media/import_files/loggers_import_files/', 'import_files.log')
))

print(os.path.abspath(os.path.join('../media/import_files/loggers_import_files/', 'import_files.log')))
console_out = logging.StreamHandler()

logging.basicConfig(
    handlers=(file_log, console_out),
    level=logging.DEBUG,
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
)

logger = logging.getLogger('import_file_1.py')

folder_path = os.path.abspath(os.path.join('../media/import_files/queued_files/test_test.json'))


def get_or_none(classmodel, **kwargs):

    """Возвращает продукт, если его нет, то None"""

    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def get_category_id(name: str) -> Any:

    """Функция возврата id категории, если категории нет, то создаёт её"""

    category = get_or_none(Category, name=name)

    if not category:
        try:
            Category.objects.create(
                name=name
            )

            category = Category.objects.get(name=name)
            return category

        except Exception as ex:
            logger.error(f'Ошибка {ex}')
    return category


def moving_file(path_file: str):

    """Перемещение файла в другую директорию"""

    path_dir = os.path.abspath(os.path.join('../media/import_files/successful_imports/'))

    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)

    os.replace(path_file, f'{path_dir}/{path_file.split("/")[-1]}')


def parsing_json_file(path_file_json: str) -> None:

    """Обработка файла json"""

    print(path_file_json)
    with open(path_file_json, 'r', encoding='utf-8') as file:
        open_file = json.load(file)

    seller = get_or_none(Seller, user=get_or_none(CustomUser, email=open_file['author']))

    for i_category in open_file['category']:
        category = get_category_id(i_category)

        for j_product in open_file['category'][i_category]:

            try:
                product = get_or_none(Product, name=j_product['name'])

                if not product:
                    product = Product.objects.create(
                        name=j_product['name'],
                        description=j_product['description'],
                        category=category
                    )

                    if j_product.get('image'):
                        # Проблемы с отображением фото товара если URL ссылкой
                        ProductImage.objects.create(
                            product=product,
                            image=j_product['image']
                        )

                Offer.objects.create(
                    product=product,
                    seller=seller,
                    price=j_product['offer']['price']
                )

            except Exception as ex:
                logger.error(f'Ошибка возникла при создании модели продукт - [{ex}]')

    moving_file(path_file_json)
    logger.info('File import')


# Если в скрипте есть логирование, то возникает во время вызова функции из product/management/commands/import_file
# Исключение
# FileNotFoundError: [Errno 2] No such file or directory: '/media/import_files/loggers_import_files/import_files.log'
#
# Если убрать логирование, то возникает исключение
# PermissionError: [Errno 13] Permission denied: '/media/import_files'
#
# Высов скрипта делаю через консольную команду python manage.py import_file test_test.json
