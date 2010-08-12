from django.db import models
from djangosphinx.models import SphinxSearch


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    element_singular = models.CharField(max_length=200)
    element_plural = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category)
    parent = models.ForeignKey('Item', null=True, blank=True)
    name = models.CharField(max_length=1000)

    search = SphinxSearch(
        mode='SPH_MATCH_EXTENDED2',
        rankmode='SPH_RANK_SPH04',
        weights={'name': 1},
        index='main_item',
    )

    def __unicode__(self):
        return self.name


class ItemProfile(models.Model):
    item = models.OneToOneField(Item, related_name='profile')

    page = models.ForeignKey('wiki.Page', null=True)


class Review(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey('users.User')
    text = models.TextField()


class Action(models.Model):
    time = models.DateTimeField(auto_now=True, unique=False)
    opinion = models.ForeignKey('Opinion', null=True, blank=True)
    review = models.ForeignKey('Review', null=True, blank=True)
    user = models.ForeignKey('users.User')

    types = {
        'rating': 1,
        'review': 2,
    }
    types_reverse = dict((v,k) for k, v in types.items())
    TYPE_CHOICES = types_reverse.items()
    type = models.IntegerField(choices=TYPE_CHOICES)

    def __unicode__(self):
        return self.time.ctime()


class OpinionManager(models.Manager):
    def opinions_of(self, viewed, viewer, category=None):
        '''
        Fetches opinions of a user (viewed) on items
         that the viewer also rated.
        '''

        where = ''
        params = [viewed.id, viewer.id, viewed.id]
        if category is not None and category:
            where += ' AND mc.id = %s'
            params.append(category.id)

        return self.raw("""
            SELECT m1.id, m1.item_id, m1.rating, m2.rating AS your_rating,
             mc.element_singular AS category_singular,
             mi.name AS item_name,
             (EXISTS (SELECT 1 FROM main_review WHERE main_review.user_id = %s AND main_review.item_id = mi.id)) AS review
            FROM main_opinion m1
            LEFT JOIN main_opinion m2
             ON (m1.item_id=m2.item_id AND m2.user_id=%s)
            INNER JOIN main_item mi
             ON (m1.item_id=mi.id)
            INNER JOIN main_category mc
             ON (mi.category_id=mc.id)
            WHERE m1.user_id = %s""" + where + """
            ORDER BY m2.rating IS NULL, m1.rating DESC, mi.name""",
                params)


class Opinion(models.Model):
    user = models.ForeignKey('users.User')
    item = models.ForeignKey(Item)

    RATING_CHOICES = (
        (1, 'Hate it'),
        (2, 'Dislike it'),
        (3, 'Neutral to it'),
        (4, 'Like it'),
        (5, 'Love it'),
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, db_index=True)

    objects = OpinionManager()

    def __unicode__(self):
        return "%s gave %s a rating of %d." % (self.user.username, self.item.name, self.rating)

    def get_third_person(self):
        third_person_choices = {
            1: 'hates',
            2: 'dislikes',
            3: 'is neutral to',
            4: 'likes',
            5: 'loves',
        }
        return third_person_choices[self.rating]


class SimilarityManager(models.Manager):
    def update_user(self, user):
        '''
        Update similarity values for a user against all other users.
        '''
        for user2 in User.objects.all():
            self.update_user_pair(user, user2)

    def update_item_delta(self, user, delta):
        '''
        Update similarity values for a user against all other users after
         an opinion set update, represented by a delta dict.
        '''
        from django.db import connection, transaction

        cursor = connection.cursor()

        items = list(delta.iterkeys())
        for item in items:
            cursor.execute("SELECT update_item_rated(%s, %s);", [user.id, item])

        transaction.commit_unless_managed()


    def update_user_pair(self, user1, user2):
        '''
        Update similarity values for a pair of users.

        NOTE: This has been superseded by update_item_delta.
         Never use this for production.
        '''
        from django.db import connection
        if user1 == user2:
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT m1.rating, m2.rating
            FROM main_opinion m1
            INNER JOIN main_opinion m2
            ON (m1.item_id = m2.item_id AND m1.user_id=%s)
            WHERE m2.user_id = %s
            """, [user1.id, user2.id])

        value = 0
        for row in cursor.fetchall():
            difference = abs(row[0] - row[1])
            if difference == 0:
                value += 2
            elif difference == 1:
                value += 1
            elif difference == 2:
                pass
            elif difference == 3:
                value -= 1
            elif difference == 4:
                value -= 2
        obj, created = Similarity.objects.get_or_create(user1=user1,
            user2=user2, defaults={'value': value})
        if not created:
            obj.value = value
            obj.save()

        obj, created = Similarity.objects.get_or_create(user1=user2,
            user2=user1, defaults={'value': value})
        if not created:
            obj.value = value
            obj.save()


class Similarity(models.Model):
    user1 = models.ForeignKey('users.User')
    user2 = models.ForeignKey('users.User', related_name="similarity_set2")
    value = models.IntegerField(db_index=True)

    objects = SimilarityManager()

    def __unicode__(self):
        return "S(%s, %s) = %d" % (self.user1.username,
            self.user2.username, self.value)
