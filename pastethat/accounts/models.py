from django.db import models
from django.contrib.auth.models import User

import datetime
import hashlib

class LostPasswordHash(models.Model):
    user    = models.ForeignKey(User, unique=True)
    hash    = models.CharField(max_length=32)
    date_added = models.DateTimeField(default=datetime.datetime.now, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.hash:
            self.set_hash()
        super(LostPasswordHash, self).save(*args, **kwargs)
    
    def set_hash(self):
        self.hash = hashlib.md5(str(random.randint(1, 10000000))).hexdigest()
    
    @property
    def is_valid(self):
        return self.date_added > datetime.datetime.now()-datetime.timedelta(days=1)
    
    @models.permalink
    def get_absolute_url(self):
        return ('accounts.recover.confirm', (), dict(user_id=self.user_id, hash=self.hash))
