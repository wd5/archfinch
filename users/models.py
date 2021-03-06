from django.db import models
from django.db.models import F, Count
from django.contrib.auth.models import User as BaseUser, UserManager as BaseUserManager
from django.utils.http import int_to_base36
from django.core.urlresolvers import reverse
from archfinch.main.models import Opinion, Similarity, Item, Category
from lazysignup.utils import is_lazy_user


class User(BaseUser):
    objects = BaseUserManager()

    karma = models.IntegerField(default=0)
    referred_by = models.ForeignKey('users.User', null=True, blank=True)

    def self_lists(self):
        lists = [
            {'name': 'ignored', 'id': '!ignored'},
            {'name': 'queue', 'id': '!queue'},
        ]
        for list in self.list_set.exclude(ignored=True).exclude(queue=True):
            lists.append({'name': list.name, 'id': int_to_base36(list.id)})

        return lists


    def similar(self):
        '''
        Fetches users most similar to self.user, ordered by descending
         similarity.
        '''
        similar_users = Similarity.objects.filter(user1__exact=self).exclude(
            user2__exact=self).filter(value__gt=0).order_by('-value', 'user2')
        return similar_users


    def add_points(self, n):
        '''
        Adds points to user's karma.
        '''
        self.karma = self.karma + n
        self.save()

        # if the user's current karma passes 20, reward their referrer (if any)
        if self.karma >= 20 and self.karma - n < 20 and self.referred_by:
            self.referred_by.add_points(20)

        # unreward the referrer if the karma goes back though (nice try)
        if self.karma < 20 and self.karma - n >= 20 and self.referred_by:
            self.referred_by.add_points(-20)


    def karma_place(self):
        '''
        Fetches user's place in the top users chart, according to karma.
        '''
        return User.objects.filter(karma__gt=self.karma).count()+1


    def categories(self, hide=True):
        '''
        Fetches categories in which the user has rated items, ordered
         by descending rating count.
        '''
        
        categories = self.opinion_set.all()
        if hide:
            categories = categories.filter(item__category__hide=False)       
        categories = categories.values('item__category__element_plural', 'item__category__slug').annotate(count=Count('item__category')).order_by('-count')
   
        # translate the long keys 
        translate = {'item__category__element_plural': 'element_plural', 'item__category__slug': 'slug'}
        categories = map(lambda c: dict((translate.get(k,k), v) for k,v in c.iteritems()), categories)

        return categories

    def my_categories(self):
        '''
        If the user doesn't have any categories, return the 'major' ones.
        '''
        if self.opinion_set.filter(item__category__hide=False):
            return self.categories()
        else:
            return Category.objects.filter(name__in=['TV shows', 'Films', 'Video games', 'Books']).values('element_plural', 'slug')

    def is_generic(self):
        return not self.opinion_set.exists()

    def __unicode__(self):
        if is_lazy_user(self):
            return 'anonymous user'
        else:
            return self.username
