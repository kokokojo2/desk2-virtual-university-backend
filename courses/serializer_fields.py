from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.reverse import reverse


class CourseRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'course_id': request.resolver_match.kwargs['course_id'],
            'pk': obj.pk
        }

        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class ChapterRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'course_id': request.resolver_match.kwargs['course_id'],
            'chapter_id': obj.chapter.pk,
            'pk': obj.pk
        }

        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)
