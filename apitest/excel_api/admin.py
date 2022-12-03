from django.contrib import admin
from excel_api import models

# Register your models here.
admin.site.register(models.UserProfile)
admin.site.register(models.excel_data)
admin.site.register(models.ConstantDatas)