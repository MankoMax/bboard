from django.contrib import admin
import datetime
from .models import AdvUser
from .utilities import send_activation_notification
from .models import SuperRubric, SubRubric, Bb, AdditionalImage, Comment
from .forms import SubRubricForm


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с оповещениями отправлены')
    send_activation_notifications.short_description = 'Отправка писем с оповещениями об активации'
    
    
class NonActivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'
    
    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        )
        
    def queryset(self, request, queryset):
        if self.value() == 'activated':
            return queryset.filter(is_activated=True)
        elif self.value() == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_activated=False, date_joined__date__lt=d)
        elif self.value() == 'week':
            d = datetime.date.today() - datetime.timedelta(days=7)
            return queryset.filter(is_activated=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    list_filter = (NonActivatedFilter,)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fields = (('username', 'email'), 
              ('first_name', 'last_name'), 
              ('send_messages', 'is_activated'), 
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions', 
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)
    

class SubRubricInline(admin.TabularInline):
    model = SubRubric
    
class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm
    
class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage
    
class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (('rubric', 'author'),'title', 'content', 'price', 'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'is_active')
    list_display_links = ('author', 'content')
    list_filter = ('is_active',)
    search_fields = ('author', 'content',)
    date_hierarchy = 'created_at'
    fields = ('author', 'content', 'is_active', 'created_at')
    readonly_fields = ('created_at',)
    
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bb, BbAdmin)    
admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SubRubric, SubRubricAdmin) 
admin.site.register(SuperRubric, SuperRubricAdmin)