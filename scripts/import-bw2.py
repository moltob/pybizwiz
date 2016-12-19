"""Import Bizwiz 2 data into Bizwiz 4.

The data from Bizwiz 2 must have been exported as CSV tables from the BW2 database into a folder
that is passed to this script as command line argument.

Execution of this code interacts with the Dkango configured database. For this to work the
DJANGO_SETTINGS_MODULE environment variable must point to the settings module to be used by Django.
"""
import argparse
import csv

import logging
import os

import django.db.transaction

_logger = logging.getLogger('import-bw2')


class Bw2Importer:
    def __init__(self, folderpath, prefix='BizWiz_replica_dbo_'):
        self.folderpath = folderpath
        self.prefix = prefix

    def run(self):
        _logger.info('Importing Bizwiz 2 data from {}.'.format(self.folderpath))
        django.setup()
        self.import_articles()

    def exported_filepath(self, modelname):
        filename = '{}{}.csv'.format(self.prefix, modelname)
        return os.path.join(self.folderpath, filename)

    def imported_objects(self, modelname, modelclass):
        with django.db.transaction.atomic():
            deleted, _ = modelclass.objects.all().delete()
            if deleted:
                _logger.info('Deleted {} preexisting {} objects.'.format(deleted, modelname))

            count = 0
            with open(self.exported_filepath(modelname), encoding='utf-8') as file:
                for row in csv.reader(file):
                    yield row
                    count += 1

            _logger.info('Imported {} {} objects.'.format(count, modelname))

    def import_articles(self):
        from bizwiz.articles.models import Article
        for bw2_id, invoice_text, last_price, outdated in self.imported_objects('Article', Article):
            article = Article(name=invoice_text, price=last_price, inactive=outdated)
            article.save()


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(description='Importer for Biwwiz 2 data into '
                                                 'Bizwiz 4 database.')
    parser.add_argument('folderpath', help='Folder where Bizwiz 2 export CSV files are stored.')
    args = parser.parse_args()

    importer = Bw2Importer(args.folderpath)
    importer.run()


if __name__ == '__main__':
    main()
