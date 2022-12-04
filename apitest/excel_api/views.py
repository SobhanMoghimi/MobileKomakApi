from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from excel_api import serializers
import requests
from .models import ExcelData, ConstantDatas
from typing import Tuple


class HelloApiView(APIView):
    """Test API View."""
    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None):
        """Returns a list of APIView features."""
        an_apiview = [
            'Uses HTTP methods as function (get, post, patch, put, delete)',
            'Is similar to a traditional Django View',
            'Gives you the most control over your application logic',
            'Is mapped manually to URLs',
        ]

        return Response({'message': 'Hello!', 'an_apiview': an_apiview})

    def post(self, request, format=None):
        """Create a hello message with our name."""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class ExcelApiView(APIView):
    """Excel Api View"""
    serializer_class = serializers.ExcelSerializer
    def get(self, request, format=None):
        return Response('Soon you will see the result')

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            symbol = serializer.validated_data.get('symbol')
            order_price = serializer.validated_data.get('order_price')
            stop_loss = serializer.validated_data.get('stop_loss')
            take_profit = serializer.validated_data.get('take_profit')
            contract_type = serializer.validated_data.get('contract_type')

            constansObj = ConstantDatas.objects.last()
            signal = constansObj.signal
            total_position = constansObj.total_position
            initial_margin = constansObj.initial_margin
            total_deposit = constansObj.total_deposit


            token_quantity, leverage = process(symbol,
                                               order_price,
                                               stop_loss,
                                               take_profit,
                                               contract_type,
                                               signal,
                                               total_position,
                                               initial_margin,
                                               total_deposit
                                               )

            # save excel data to database
            ExcelData.objects.create(
                symbol=symbol,
                order_price=order_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                contract_type=contract_type,
                signal=signal,
                total_position=total_position,
                initial_margin=initial_margin,
                total_deposit=total_deposit,
                token_quantity=token_quantity,
                leverage=leverage
            )

            # Json output for Get request
            message = {
                'symbol': symbol,
                'order_price': order_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'contract_type': contract_type,
                'leverage': leverage,
                'token_quantity': token_quantity
            }
            return Response(message)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

"""
TODO:
    1. Create Liquidation Price
    2. Make 
"""
def process(symbol: str,
                    order_price: float,
                    stop_loss: float,
                    take_profit: float,
                    contract_type: str,
                    signal: bool,
                    total_position: float,
                    initial_margin_percent: float,
                    total_deposit: float) -> Tuple[float, float]:
                # calculating leverage
                try:
                    total_loss = total_deposit * total_position
                    coef = 1 if contract_type == 'short' else -1
                    percent_of_loss = (order_price - stop_loss) / order_price * coef
                    real_position_size = total_deposit * initial_margin_percent
                    leverage = abs((total_loss / percent_of_loss) / real_position_size)
                except:
                    leverage = 0

                # calculating token quantity
                try:
                    leveraged_position_size = real_position_size * leverage
                    print(leveraged_position_size, real_position_size)
                    token_quantity = leveraged_position_size / order_price
                except:
                    token_quantity = 0

                token_quantity = round(token_quantity, 2)
                leverage = round(leverage, 2)
                return token_quantity, leverage
