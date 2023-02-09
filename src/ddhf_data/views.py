#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.contrib   import databrowse
from django.shortcuts import render_to_response
from ddhf_data.models import Producers
from ddhf_data.models import Files
from ddhf_data.models import Items
from ddhf_data.models import Donators
from ddhf_data.models import Subjects
from ddhf_data.models import Pictures
from django.template  import RequestContext

from django.shortcuts import get_object_or_404

def ItemsView(request, itemid):
    item = get_object_or_404(Items, pk=itemid)
    c = RequestContext(request, { 'pic': True, "item": item, })
    return render_to_response("admin/base_site.html", c)

def AboutView(request):
    return render_to_response("admin/about.html")
    
databrowse.site.register(Producers)
databrowse.site.register(Files)
databrowse.site.register(Items)
# databrowse.site.register(Donators)
databrowse.site.register(Subjects)
databrowse.site.register(Pictures)
