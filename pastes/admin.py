from django.contrib import admin
from models import *

class SyntaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'lexer', 'order')
    search_fields = ('name', 'lexer')
    list_filter = ('parent',)
    
admin.site.register(Syntax, SyntaxAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('subdomain', 'name', 'url')
    search_fields = ('subdomain', 'name', 'url')
    
admin.site.register(Group, GroupAdmin)

class PasteAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'group', 'ip')
    search_fields = ('type', 'post_date')
    
admin.site.register(Paste, PasteAdmin)