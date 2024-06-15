from django.db import models

# Create your models here.

class testtable(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50)
    date_hired = models.DateField()

    def _str_(self):
        return f"{self.first_name} {self.last_name} - {self.position}"