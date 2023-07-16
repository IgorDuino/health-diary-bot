from django.contrib import admin

from text_manager.models import Text, Texts, ButtonText, ButtonTexts


class TextAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ("title",)
    list_display = ("title", "text")
    list_filter = ("title",)
    search_fields = ("title", "text")

    actions = ("set_default",)


@admin.register(Text)
class TextAdminText(TextAdmin):
    def set_default(self, request, queryset):
        for text in queryset:
            try:
                text: Text
                text.text = getattr(Texts, text.title)
                text.save()
            except Exception as e:
                self.message_user(request, f"Ошибка: {e}")
                queryset.delete()


@admin.register(ButtonText)
class TextAdminButtonText(TextAdmin):
    def set_default(self, request, queryset):
        for text in queryset:
            try:
                text: ButtonText
                text.text = getattr(ButtonTexts, text.title)
                text.save()
            except Exception as e:
                self.message_user(request, f"Ошибка: {e}")
                queryset.delete()
