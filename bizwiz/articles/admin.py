from django.contrib import admin

from bizwiz.articles.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inactive')
    search_fields = ('name',)


admin.site.register(Article, ArticleAdmin)
