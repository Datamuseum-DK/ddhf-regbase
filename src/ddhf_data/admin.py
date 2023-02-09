# -*- coding: UTF-8 -*-
#
from ddhf_data.models import Donators
from ddhf_data.models import Files
from ddhf_data.models import Sted
from ddhf_data.models import Subjects
from ddhf_data.models import Pictures
from ddhf_data.models import Producers
from ddhf_data.models import Items
from django.contrib import admin
from django.contrib.auth.models import User


def set_user(request, obj, field_name, change):
  if hasattr(obj, field_name):
    username = getattr(obj,  field_name)
    if username is None or len(username.strip()) == 0:
      setattr(obj, field_name, request.user.username)
      change = True
  else:   
    setattr(obj, field_name, request.user.username)
    change = True
  # return change
  return True


class PicturesAdmin(admin.ModelAdmin):
    list_display = ("pictureid", "picture_tag", "picturetext", "pictureregisteredby")
    list_display_links = ("pictureid", "picture_tag")
    search_fields =('picturetext', 'pictureid')
    readonly_fields = ['pictureregisteredby',]
    ordering = ['-pictureid']

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "pictureregisteredby", change):
          obj.save()


admin.site.register(Pictures, PicturesAdmin)

class ItemsAdmin(admin.ModelAdmin):
    list_per_page = 50
    save_on_top = True
    save_as = True
    fields =('fileid', 'itempicture', 'itemdeleted',
             'itemheadline', 'itemdescription', 'itemsize',
             'itemweight', 'itemmodeltype', 'itemserialno',
             'itemdatingfrom', 'itemdatingto',
             'producerid', 'donatorid', 'itemacquiretype',
             'itemdepositeduntil', 'itemoutdated', 'itemborroweduntil',
             'itemreceived', 'itemreceivedby', 'itemregistered',
             'itemregisteredby', 'itemthanksletter', 'itemlocation',
             'itemusedby', 'itemusedfor', 'itemusedwhereid',
             'itemusedfrom', 'itemusedto', 'itemusedendfrom',
             'itemusedendto', 'itemextrainfo', 'itemrestoration',
             'itemreferences', 'itemremarks',
             'itemsubject',
            )
    # list_display = 'itemid', 'itemheadline', 'get_pictures', 'itemdescription', 'itemregisteredby',
    list_display = 'itemheadline', 'get_pictures', 'itemdescription', 'itemregisteredby',
    search_fields =('itemheadline', 'itemdescription', 'itemmodeltype',
                    'itemusedby', 'itemusedfor',
                    'itemusedwhereid__stednavn',
                    'itemextrainfo', 'itemremarks',
                    'producerid__producertitle',
                    'donatorid__donatorname',
                    'fileid__filetitle',
                    'itemsubject__subjecttitle',
                    'itemserialno', 'itemlocation'
                    )
    filter_horizontal = 'itemsubject',
    raw_id_fields = 'itempicture',
    date_hierarchy = 'itemdatingfrom'

    class Admin:
        list_filter = 'itemreceived', 'itemreceivedby', 'lastmodified', 'itemregistered'

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "itemregisteredby", change):
        obj.save()


admin.site.register(Items, ItemsAdmin)

class ItemsInline(admin.StackedInline):
    model = Items
    raw_id_fields = 'itempicture',
    fieldsets = [
        ( 'genstand',
            {
            'fields':['fileid',
                       'itempicture',
                       'itemdeleted',
                       'itemheadline',
                       'itemdescription',
                       'itemsize',
                       'itemweight',
                       'itemmodeltype',
                       'itemserialno',
                       'itemdatingfrom',
                       'itemdatingto',
                       'producerid',
                       'donatorid',
                       'itemacquiretype',
                       'itemdepositeduntil',
                       'itemoutdated',
                       'itemborroweduntil',
                       'itemreceived',
                       'itemreceivedby',
                       'itemregistered',
                       'itemregisteredby',
                       'itemthanksletter',
                       'itemlocation',
                       'itemusedby',
                       'itemusedfor',
                       'itemusedwhereid',
                       'itemusedfrom',
                       'itemusedto',
                       'itemusedendfrom',
                       'itemusedendto',
                       'itemextrainfo',
                       'itemrestoration',
                       'itemreferences',
                       'itemremarks',
                       'itemsubject',
                       ],
             'classes': ['collapse'],
            },
        ),
            # { 'filter_horizontal':['itemsubject'],},
            # { 'filter_vertical':['itempicture'],},
        ]
    extra = 0

class DonatorsAdmin(admin.ModelAdmin):
    list_display = (
               'donatorname',
               'donatorinstitution',
               'donatorposition',
               'donatoraddress',
               'donatorphone',
               'donatoremail',
               'creator',
                   )
    list_display_links = ( 'donatorname',)
    readonly_fields = ['creator',]
    list_filter = [ 'created', 'lastmodified', ]
    fields = (
                'donatorname',
                'donatorinstitution',
                'donatorposition',
                'donatoraddress',
                'donatorphone',
                'donatoremail',
                'creator'
              )
    inlines = [ItemsInline]

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "creator", change):
        obj.save()


admin.site.register(Donators, DonatorsAdmin)


class FilesAdmin(admin.ModelAdmin):
    list_display = (
        'filetitle',
        'filedescription',
        'datingfrom',
        'datingto',
        'creator',

        )
    list_display_links = ( 'filetitle',)

    date_hierarchy = 'datingfrom'
    readonly_fields = ['creator', 'lastmodified']
    list_filter = [ 'created', 'lastmodified', ]
    fields = 'filetitle', 'filedescription', 'datingfrom', 'datingto', 'creator',
    inlines = [ItemsInline]

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "creator", change):
        obj.save()


admin.site.register(Files, FilesAdmin)

class StedAdmin (admin.ModelAdmin):
    list_display = ['stednavn']
    pass

admin.site.register(Sted, StedAdmin)

class ProducersAdmin(admin.ModelAdmin):
    list_display = (
        'producertitle',
        'producerdescription',
        )

    list_display_link = (
        'producertitle',
        )

    list_filter = [ 'created', 'lastmodified', ]
    fields = [ 'producertitle', 'producerdescription', 'creator', ]
    readonly_fields = ['creator',]

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "creator", change):
        obj.save()

    inlines = [ItemsInline]
admin.site.register(Producers, ProducersAdmin)


class SubjectsAdmin(admin.ModelAdmin):
    list_display = (
            'subjecttitle',
            'subjectdescription',
            )
    list_display_links = 'subjecttitle',
    search_fields =('picturetext', 'pictureid')
    list_filter = [ 'created', 'lastmodified', ]
    fields = [ 'subjecttitle', 'subjectdescription', 'creator', ]
    readonly_fields = ['creator',]

    def save_model(self, request, obj, form, change):
      if set_user(request, obj, "creator", change):
        obj.save()

admin.site.register(Subjects, SubjectsAdmin)

