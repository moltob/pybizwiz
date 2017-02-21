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

import decimal
import django.db.transaction

_logger = logging.getLogger('import-bw2')

Bw2Article = collections.namedtuple(
    'Bw2Article',
    'id invoice_text last_price outdated'
)
Bw2Customer = collections.namedtuple(
    'Bw2Customer',
    'id last_name first_name title company_name street_address zip_code city salutation '
    'phone_number mobile_number email shoot_1_date shoot_2_date shoot_3_date shoot_4_date notes'
)
Bw2Project = collections.namedtuple(
    'Bw2Project',
    'id name notes start_date'
)
Bw2CustomerGroup = collections.namedtuple(
    'Bw2CustomerGroup',
    'id name project_id'
)
Bw2CustomerInGroupAssoc = collections.namedtuple(
    'Bw2CustomerInGroupAssoc',
    'id customer_group_id customer_id'
)
Bw2ArticleInProjectAssoc = collections.namedtuple(
    'Bw2ArticleInProjectAssoc',
    'id article_id project_id'
)
Bw2ArticleList = collections.namedtuple(
    'Bw2ArticleList',
    'id invoice_number invoice_date payment_date offer_date order_date taxes_filed '
    'customer_in_group_assoc_id pay_before_ship offer_with_articles_pending'
)
Bw2ArticleListItem = collections.namedtuple(
    'Bw2ArticleListItem',
    'id article_list_id article_id price amount'
)


class Bw2Importer:
    def __init__(self, folderpath, prefix='BizWiz_replica_dbo_'):
        self.folderpath = folderpath
        self.prefix = prefix

    def run(self):
        _logger.info('Importing Bizwiz 2 data from {}.'.format(self.folderpath))
        django.setup()
        articles = self.import_articles()
        customers = self.import_customers()
        projects = self.import_projects(articles)
        customer_groups, group_customer_assocs = self.import_customer_groups(projects, customers)
        invoices = self.import_invoices(group_customer_assocs, articles)

    @staticmethod
    def date(s):
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

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
        unique_article_names = set()
        bw2_articles = (Bw2Article(*fields) for fields in self.imported_objects('Article', Article))
        for bw2_article in bw2_articles:
            article = Article(name=bw2_article.invoice_text.strip(),
                              price=float(bw2_article.last_price.strip()),
                              inactive=bool(int(bw2_article.outdated)))

            if "rabatt" in article.name.lower() and not article.inactive:
                _logger.info('Deactivating old rebate article: {}.'.format(article.name))
                article.inactive = True

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
        return articles

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

    def import_projects(self, articles):
        from bizwiz.projects.models import Project

        projects = {}
        bw2_projects = (Bw2Project(*fields) for fields in self.imported_objects('Project', Project))

        for bw2_project in bw2_projects:
            project = Project(name=bw2_project.name,
                              start_date=self.date(bw2_project.start_date),
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

        group_customer_assocs = {}
        assoc_ids_by_group_id = collections.defaultdict(set)
        count = 0
        for bw2_assoc in bw2_assocs:
            assoc_id = int(bw2_assoc.id)
            group_id = int(bw2_assoc.customer_group_id)
            customer_id = int(bw2_assoc.customer_id)

            group = customer_groups[group_id]
            customer = customers[customer_id]
            group_customer_assocs[assoc_id] = group, customer
            assoc_ids_by_group_id[group_id].add(assoc_id)
            group.customers.add(customer)
            group.save()
            count += 1

        _logger.info('Added {} customers to groups.'.format(count))

        # remove the "Alle" customer groups:
        customer_groups_copy = customer_groups.copy()
        for customer_group_id, group in customer_groups_copy.items():
            remove = False
            if group.name == 'Alle':
                _logger.info('Removing customer group "Alle" from project {}.'
                             .format(group.project.name))
                remove = True
            if group.customers.count() == 0:
                _logger.info('Removing empty customer group {}.'.format(group.name))
                remove = True
            if remove:
                group.delete()
                del customer_groups[customer_group_id]
                for assoc_id in assoc_ids_by_group_id[customer_group_id]:
                    # tag group as being deleted but keep customer information:
                    _, customer = group_customer_assocs[assoc_id]
                    group_customer_assocs[assoc_id] = None, customer

        # remove projects without customer groups:
        projects_copy = projects.copy()
        for project_id, project in projects_copy.items():
            if project.customergroup_set.count() == 0:
                _logger.info('Deleting project without customer groups: {}'.format(project.name))
                project.delete()
                del projects[project_id]

        return customer_groups, group_customer_assocs

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

    def import_invoices(self, group_customer_assocs, articles):
        from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle
        invoices = {}

        bw2_invoices = (Bw2ArticleList(*fields) for fields in
                        self.imported_objects('CustomersArticleList', Invoice))

        for bw2_invoice in bw2_invoices:
            bw2_id = int(bw2_invoice.id)
            number = bw2_invoice.invoice_number.strip()
            invoice_date = self.date(bw2_invoice.invoice_date)
            payment_date = self.date(bw2_invoice.payment_date) if bw2_invoice.payment_date else None
            taxes_filed = bw2_invoice.taxes_filed.strip() == '1'
            customer_in_group_assoc_id = int(bw2_invoice.customer_in_group_assoc_id)

            group, customer = group_customer_assocs.get(customer_in_group_assoc_id, (None, None))

            invoice = Invoice(
                number=int(number),
                date_created=invoice_date,
                date_paid=payment_date,
                date_taxes_filed=payment_date if taxes_filed else None,
                project=group.project if group else None,
            )
            invoice.save()
            invoices[bw2_id] = invoice

            if customer:
                _logger.debug('Invoice {} for {}.'.format(invoice.number, customer.full_name()))
                invoiced_customer = InvoicedCustomer.create(invoice, customer)
                invoiced_customer.save()
            else:
                _logger.debug('Invoice {} has no customer.'.format(invoice.number))

        bw2_article_list_items = (Bw2ArticleListItem(*fields) for fields in
                                  self.imported_objects('ArticleListItem', InvoicedArticle))

        for bw2_article_list_item in bw2_article_list_items:
            article_list_id = int(bw2_article_list_item.article_list_id)
            article_id = int(bw2_article_list_item.article_id)
            price = float(bw2_article_list_item.price)
            amount = int(bw2_article_list_item.amount)

            article = articles[article_id]
            invoice = invoices[article_list_id]
            invoiced_article = InvoicedArticle.create(invoice, article, amount)
            invoiced_article.price = price
            invoiced_article.save()

        _logger.info('Imported {} invoices.'.format(len(invoices)))
        return invoices

    def verify_invoices(self):
        bw2_article_list_items = (Bw2ArticleListItem(*fields) for fields in
                                  self.imported_objects('ArticleListItem', None))

        invoice_total_bw2 = 0.0

        for bw2_article_list_item in bw2_article_list_items:
            price = float(bw2_article_list_item.price)
            amount = int(bw2_article_list_item.amount)
            invoice_total_bw2 += price * amount

        _logger.info('Total of all invoiced items in Bizwiz 2: %.2f' % invoice_total_bw2)

        invoice_total_bw4 = decimal.Decimal(0)

        from bizwiz.invoices.models import Invoice
        for invoice in Invoice.objects.all():
            for item in invoice.invoiced_articles.all():
                invoice_total_bw4 += item.price * item.amount

        _logger.info('Total of all invoiced items in Bizwiz 4: %.2f' % invoice_total_bw4)

        assert abs(invoice_total_bw2 - float(invoice_total_bw4)) < 0.01


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
    importer.verify_invoices()


if __name__ == '__main__':
    main()
