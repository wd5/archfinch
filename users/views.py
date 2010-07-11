from django.http import HttpResponse
#from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from main.models import Opinion, Similarity
from users.models import User

def overview(request, username):
    viewed_user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        opinions = Opinion.objects.opinions_of(viewed_user, request.user)

        # this is only for testing and should be removed
        Similarity.objects.update_user_pair(viewed_user, request.user)
        #Similarity.objects.update_user(viewed_user)

        try:
            similarity_value = viewed_user.similarity_set.get(user2=request.user.id).value
        except ObjectDoesNotExist:
            similarity_value = None
        return render_to_response('user/overview.html',
            {'viewed_user': viewed_user, 'opinions': opinions,
            'similarity': similarity_value},
             context_instance=RequestContext(request))
    else:
        opinions = [] # TODO: fix this 
        return render_to_response('user/overview_anonymous.html',
            {'viewed_user': viewed_user, 'opinions': opinions},
            context_instance=RequestContext(request))

def similar(request):
    '''
    Show users most similar to the logged in user.
    '''

    if request.user.is_authenticated():
        similar_users = request.user.similar()
        return render_to_response('user/similar.html',
            {'similar_users': similar_users[:10]})
    else:
        return render_to_response('user/similar_anonymous.html')
    