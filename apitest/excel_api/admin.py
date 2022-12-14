from django.contrib import admin
from excel_api import models
from django.http import HttpResponse
import csv

class ExcelDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'valid_action',
                    'symbol',
                    'order_price',
                    'stop_loss',
                    'take_profit',
                    'contract_type',
                    'total_position',
                    'initial_margin',
                    'total_deposit',
                    'token_quantity',
                    'leverage',
                    'liquidation_price',
                    'leveraged_percent_of_loss',
                    'total_loss',
                    'percent_of_profit',
                    'percent_of_loss',
                    'leveraged_percent_of_profit',
                    'total_profit',
                    'real_position_size',
                    'leveraged_position_size',
                    'reward_risk',
                    'take_profit_1',
                    'take_profit_2',
                    'take_profit_3',
                    'take_profit_4',
                    'take_profit_5')
    list_display_links = ('id', 'time', 'valid_action', 'symbol', 'total_position', 'initial_margin', 'total_deposit', 'order_price', 'stop_loss', 'take_profit', 'contract_type', 'token_quantity', 'leverage', 'liquidation_price')
    list_filter = ('time',
                   'valid_action',
                   'symbol',
                   'total_position',
                   'initial_margin',
                   'contract_type',
                   'token_quantity')
    list_per_page = 20

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response


# Register your models here.
admin.site.register(models.UserProfile)
admin.site.register(models.ExcelData, ExcelDataAdmin)
admin.site.register(models.ConstantDatas)
