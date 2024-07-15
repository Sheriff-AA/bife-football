from django.shortcuts import render, reverse
from django.views import generic


from players.mixins import AdminRequiredMixin
from .forms import AdminModelForm

# Create your views here.
class AdminCreateView(AdminRequiredMixin, generic.CreateView):
    template_name = "teams/team_create.html"
    form_class = AdminModelForm

    def get_success_url(self):
        return reverse("team:team-list")
    
    def form_valid(self, form):
        return super(AdminCreateView, self).form_valid(form)
