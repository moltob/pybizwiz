import logging

from django import contrib
from django import urls, http
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.rebates.forms import RebateFormset
from bizwiz.rebates.models import Rebate

_logger = logging.getLogger(__name__)


class Update(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = 'rebates/rebates_update.html'

    def get_context_data(self, **kwargs):
        if self.request.method in ('POST', 'PUT'):
            rebate_formset = RebateFormset(self.request.POST)
        else:
            rebate_formset = RebateFormset(queryset=Rebate.objects.all().order_by('name'))
        return super().get_context_data(formset=rebate_formset, **kwargs)

    def post(self, request, *args, **kwargs):
        rebate_formset = RebateFormset(request.POST)
        if rebate_formset.is_valid():
            return self.formset_valid(rebate_formset)
        else:
            return self.render_to_response(self.get_context_data())

    def formset_valid(self, rebate_formset):
        rebate_formset.save()

        def log_modification(objects, fmt):
            if objects:
                names = (r.name for r in objects)
                msg = _(fmt).format(', '.join(names))
                _logger.info(msg)
                contrib.messages.success(self.request, msg)

        log_modification(rebate_formset.new_objects, _('Added rebates: {}.'))
        log_modification(rebate_formset.deleted_objects, _('Deleted rebates: {}.'))

        # changed object field is actually a tuple of what fields were changed, so extract objects:
        changed_objects = [r for r, f in rebate_formset.changed_objects]  # list allows empty check
        log_modification(changed_objects, _('Modified rebates: {}.'))

        return http.HttpResponseRedirect(urls.reverse('rebates:update'))
