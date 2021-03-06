import django.shortcuts

def render_to_response(template, dictionary=None, context_instance=None, mimetype=None):
    """
    A modification of render_to_response providing some default template variables.
    """

    if dictionary is None:
        dictionary = {}

    dictionary.setdefault('base', 'base.html')
    return django.shortcuts.render_to_response(template, dictionary=dictionary, context_instance=context_instance, mimetype=mimetype)


def paginate(objects, page, n, count=None):
    from django.core.paginator import Paginator
    paginator = Paginator(objects, n)
    if count is not None:
        paginator._count = count
    current_page = paginator.page(page)
    page_range = range(max(1, page-3), min(paginator.num_pages, page+3)+1)
    objects = current_page.object_list

    return objects, paginator, current_page, page_range


def form_error_msg(errors):
    msg = ''
    for field, error_list in errors.iteritems():
        msg += ' '.join(error_list) + ' '
    return msg
