from django.shortcuts import render
from django.views.generic import TemplateView


class OffersIndexPage(TemplateView):
    template_name = 'offers/index.html'
