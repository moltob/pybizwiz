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

import collections

import datetime
import django.db.transaction

_logger = logging.getLogger('import-bw2')

Bw2Article = collections.namedtuple('Bw2Article', 'id invoice_text last_price outdated')
Bw2Customer = collections.namedtuple('Bw2Customer', 'id last_name first_name title company_name '
                                                    'street_address zip_code city salutation '
                                                    'phone_number mobile_number email shoot_1_date '
                                                    'shoot_2_date shoot_3_date shoot_4_date notes')
Bw2Project = collections.namedtuple('Bw2Project', 'id name notes start_date')
Bw2CustomerGroup = collections.namedtuple('Bw2CustomerGroup', 'id name project_id')
Bw2CustomerInGroupAssoc = collections.namedtuple('Bw2CustomerInGroupAssoc', 'id customer_group_id '
                                                                            'customer_id')
Bw2ArticleInProjectAssoc = collections.namedtuple('Bw2ArticleInProjectAssoc', 'id article_id '
                                                                              'project_id')


class Bw2Importer:
    def __init__(self, folderpath, prefix='BizWiz_replica_dbo_'):
        self.folderpath = folderpath
        self.prefix = prefix

    def run(self):
        _logger.info('Importing Bizwiz 2 data from {}.'.format(self.folderpath))
        django.setup()
        articles, rebate_ids = self.import_articles()
        customers = self.import_customers()
        projects = self.import_projects(articles, rebate_ids)
        customer_groups = self.import_customer_groups(projects, customers)

    def exported_filepath(self, modelname):
        filename = '{}{}.csv'.format(self.prefix, modelname)
        return os.path.join(self.folderpath, filename)

    def imported_objects(self, modelname, modelclass):
        with django.db.transaction.atomic():
            if modelclass:
                deleted, _ = modelclass.objects.all().delete()
                if deleted:
                    _logger.info('Deleted {} preexisting {} objects.'.format(deleted, modelname))

            with open(self.exported_filepath(modelname), encoding='utf-8') as file:
                for row in csv.reader(file):
                    yield row

    def import_articles(self):
        from bizwiz.articles.models import Article

        articles = {}
        rebate_ids = set()
        unique_article_names = set()
        bw2_articles = (Bw2Article(*fields) for fields in self.imported_objects('Article', Article))
        for bw2_article in bw2_articles:
            if "rabatt" in bw2_article.invoice_text.lower():
                _logger.info('Skipping import of rebate: {}.'.format(bw2_article.invoice_text))
                rebate_ids.add(int(bw2_article.id))
            else:
                article = Article(name=bw2_article.invoice_text.strip(),
                                  price=bw2_article.last_price.strip(),
                                  inactive=bw2_article.outdated.strip())

                if article.name in unique_article_names:
                    _logger.warning('Article {} {} violates unique naming condition and'
                                    ' must be deduplicated.'.
                                    format(bw2_article.id, bw2_article.invoice_text))
                else:
                    unique_article_names.add(article.name)
                    article.save()
                    articles[int(bw2_article.id)] = article

        _logger.info('Imported {} articles.'.format(len(articles)))
        self.delete_duplicates('Kontaktabzug behalten', articles, 115, (118,))
        return articles, rebate_ids

    def import_customers(self):
        from bizwiz.customers.models import Customer, Salutation

        salutation = [Salutation.MR, Salutation.MRS, Salutation.FAMILY]

        customers = {}
        bw2_customers = (Bw2Customer(*fields) for fields in
                         self.imported_objects('Customer', Customer))

        for bw2_customer in bw2_customers:
            customer = Customer(last_name=bw2_customer.last_name.strip(),
                                first_name=bw2_customer.first_name.strip(),
                                salutation=salutation[int(bw2_customer.salutation) - 1],
                                title=bw2_customer.title.strip(),
                                company_name=bw2_customer.company_name.strip(),
                                street_address=bw2_customer.street_address.strip(),
                                zip_code=bw2_customer.zip_code.strip(),
                                city=bw2_customer.city.strip(),
                                phone_number=bw2_customer.phone_number.strip(),
                                mobile_number=bw2_customer.mobile_number.strip(),
                                email=bw2_customer.email.strip(),
                                notes=bw2_customer.notes.strip())

            if customer.last_name.startswith('-'):
                old = customer.last_name
                new = old[1:]
                _logger.info('Clean up: "{}" --> "{}"'.format(old, new))
                customer.last_name = new

            customer.save()
            customers[int(bw2_customer.id)] = customer

        _logger.info('Imported {} customers.'.format(len(customers)))
        self.delete_duplicates('Frank Hemmer, M-Wert', customers, 1224, (1222, 1223, 1225))
        self.delete_duplicates('Konstantin Körner', customers, 1105, (1116, 1117))
        return customers

    def import_projects(self, articles, rebate_ids):
        from bizwiz.projects.models import Project

        projects = {}
        bw2_projects = (Bw2Project(*fields) for fields in self.imported_objects('Project', Project))

        for bw2_project in bw2_projects:
            project = Project(name=bw2_project.name,
                              start_date=datetime.datetime.strptime(bw2_project.start_date,
                                                                    '%Y-%m-%d %H:%M:%S'),
                              notes=bw2_project.notes)
            project.save()
            projects[int(bw2_project.id)] = project

        _logger.info('Imported {} projects.'.format(len(projects)))

        bw2_assocs = (Bw2ArticleInProjectAssoc(*fields) for fields in
                      self.imported_objects('ArticleInProjectAssoc', None))

        count = 0
        for bw2_assoc in bw2_assocs:
            article_id = int(bw2_assoc.article_id)
            project_id = int(bw2_assoc.project_id)

            project = projects[project_id]
            if article_id in rebate_ids:
                _logger.debug('Skipping rebate association with {}.'.format(project.name))
            else:
                article = articles[article_id]
                project.articles.add(article)
                project.save()
                count += 1

        _logger.info('Added {} articles to projects.'.format(count))
        return projects

    def import_customer_groups(self, projects, customers):
        from bizwiz.projects.models import CustomerGroup

        customer_groups = {}
        bw2_groups = (Bw2CustomerGroup(*fields) for fields in
                      self.imported_objects('CustomerGroup', CustomerGroup))

        for bw2_group in bw2_groups:
            bw2_project_id = int(bw2_group.project_id)
            group = CustomerGroup(name=bw2_group.name, project=projects[bw2_project_id])
            group.save()
            customer_groups[int(bw2_group.id)] = group

        _logger.info('Imported {} customer groups.'.format(len(customer_groups)))

        bw2_assocs = (Bw2CustomerInGroupAssoc(*fields) for fields in
                      self.imported_objects('CustomerInGroupAssoc', None))

        count = 0
        for bw2_assoc in bw2_assocs:
            group_id = int(bw2_assoc.customer_group_id)
            customer_id = int(bw2_assoc.customer_id)

            group = customer_groups[group_id]
            customer = customers[customer_id]
            group.customers.add(customer)
            group.save()
            count += 1

        _logger.info('Added {} customers to groups.'.format(count))
        return customer_groups

    @staticmethod
    def delete_duplicates(description, objects, keep_id, duplicate_ids):
        keep_object = objects[keep_id]
        for duplicate in duplicate_ids:
            duplicate_object = objects.get(duplicate)
            objects[duplicate] = keep_object
            _logger.info('Deduplication "{}":\n  From: {}\n  To:   {}'.format(description,
                                                                              duplicate_object,
                                                                              keep_object))
            if duplicate_object:
                duplicate_object.delete()


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
