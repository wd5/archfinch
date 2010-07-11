from django.shortcuts import render_to_response, get_object_or_404, HttpResponse
from django.template import RequestContext
from main.models import Item, Opinion, Action

def welcome(request):
    if request.user.is_authenticated():
        return render_to_response("main/welcome.html", context_instance=RequestContext(request))
    else:
        return render_to_response("main/welcome_anonymous.html", context_instance=RequestContext(request))

def item(request, item_id):
    '''
    Item page.
    '''

    item_id = int(item_id)
    item = get_object_or_404(Item, pk=item_id)

    if request.user.is_authenticated():
        try:
            opinion = request.user.opinion_set.get(item=item)
        except Opinion.DoesNotExist:
            opinion = None
    else:
        opinion = None

    return render_to_response("main/item.html", {'item': item, 'opinion': opinion})

def opinion_set(request, item_id, rating):
    '''
    Set rating for a (user, item) pair.

    Note: this is temporary and should be ajaxified later.
    '''

    item_id = int(item_id)
    rating = int(rating)
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_authenticated():
        # perhaps this is an opportunity to capture a yet unregistered user and shouldn't be an error
        return render_to_response('error.html', {'error_msg': 'You need to be logged in to set a rating.'})

    # this should be forwarded to a server which does this kind of work and not done during the client request
    # also, this should update similarities
    action = Action()
    action.save()
    opinion, created = Opinion.objects.get_or_create(user=request.user, item=item, defaults={'action': action})
    opinion.rating = rating
    opinion.action = action
    opinion.save()

    return HttpResponse('OK.')

def opinion_remove(request, item_id):
    '''
    Remove rating for a (user, item) pair.

    Note: this is temporary and should be ajaxified later.
    '''

    item_id = int(item_id)
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_authenticated():
        return render_to_response('error.html', {'error_msg': 'You need to be logged in to remove a rating.'})

    # see a similar comment for opinion_set
    opinion = Opinion.objects.get(user=request.user, item=item).delete()

    return HttpResponse('OK.')
