from django.contrib import admin

from core import models, constants
from . import mixins
from rangefilter.filters import DateRangeFilterBuilder


@admin.register(models.FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_filter = (("created_at", DateRangeFilterBuilder()),)


@admin.register(models.SiteSettings)
class SiteSettingsAdmin(mixins.SingleObjectAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.CompanyContacts)
class CompanyContactsAdmin(mixins.SingleObjectAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("name", "publish_at", "is_published")
    list_filter = ("is_published",)
    fieldsets = [
        (
            'Основная информация',
            {
                "fields": ('name', 'image', 'is_published', 'publish_at')
            }
        ),
        constants.AdminFields.SEO_FIELD
    ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.TextPage)
class TextPageAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            'Основная информация',
            {
                "fields": ('name',)
            }
        ),
        constants.AdminFields.SEO_FIELD
    ]
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(models.TelegramBotCredentials, admin.ModelAdmin)

admin.site.register(models.Survey, admin.ModelAdmin)


class AnswerOptionInline(admin.TabularInline):
    model = models.AnswerOption
    extra = 0


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]


class UserAnswerInline(admin.TabularInline):
    model = models.UserAnswer
    extra = 0


@admin.register(models.UserSurvey)
class UserSurveyAdmin(admin.ModelAdmin):
    inlines = [UserAnswerInline]