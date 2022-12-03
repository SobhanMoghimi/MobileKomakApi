from rest_framework import serializers

class HelloSerializer(serializers.Serializer):
    """Serializes a name field for testing our APIView."""
    name = serializers.CharField(max_length=10)

class ExcelSerializer(serializers.Serializer):
    """Serializes a name field for testing our APIView."""
    symbol = serializers.CharField(max_length=10)
    order_price = serializers.FloatField()
    stop_loss = serializers.FloatField()
    take_profit = serializers.FloatField()
    contract_type = serializers.CharField(max_length=10)
    # signal = serializers.BooleanField()
    # total_position = serializers.IntegerField()
    # initial_margin = serializers.IntegerField()
    # total_deposit = serializers.FloatField()