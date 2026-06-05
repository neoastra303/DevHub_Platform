from django_filters import rest_framework as filters
from .models import Project, Post


class ProjectFilter(filters.FilterSet):
    min_created_at = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    max_created_at = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    tech = filters.CharFilter(field_name="technologies__slug", lookup_expr="iexact")
    
    class Meta:
        model = Project
        fields = ["is_featured", "tech"]


class PostFilter(filters.FilterSet):
    author_username = filters.CharFilter(field_name="author__username", lookup_expr="iexact")
    
    class Meta:
        model = Post
        fields = ["author_username"]
