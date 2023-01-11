from django.conf import settings
from django.core.paginator import Paginator


def paginate(posts, request):
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def check_post_exist(post, response):
    if post in response.context['page_obj']:
        return True
    return False
