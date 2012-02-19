from django.db import models

class Hello(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.CharField('data', max_length=255)
    
    def __str__(self):
        return '%s, %s' % (self.id, self.data)
    
    class Meta:
        db_table = 'hello'
