from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from excel_api import serializers
from .models import ExcelData, ConstantDatas
from typing import Tuple
from excel_api import bybit

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

            constant_objects = ConstantDatas.objects.last()
            signal = constant_objects.signal
            total_position = constant_objects.total_position
            initial_margin = constant_objects.initial_margin
            total_deposit = constant_objects.total_deposit

            token_quantity, leverage, valid_action, log_info = process(symbol,
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
                # Constants for now
                signal=signal,
                total_position=total_position,
                initial_margin=initial_margin,
                total_deposit=total_deposit,
                token_quantity=token_quantity,
                # Calculated
                leverage=leverage,
                total_loss=log_info['total_loss'],
                percent_of_loss=log_info['percent_of_loss'],
                leveraged_percent_of_loss=log_info['leveraged_percent_of_loss'],
                percent_of_profit=log_info['percent_of_profit'],
                leveraged_percent_of_profit=log_info['leveraged_percent_of_profit'],
                total_profit=log_info['total_profit'],
                real_position_size=log_info['real_position_size'],
                leveraged_position_size=log_info['leveraged_position_size'],
                reward_risk=log_info['reward_risk'],
                # Liquidation Price
                valid_action=valid_action,
                liquidation_price=log_info['liquidation_price'],
                # Take Profits
                take_profit_1=log_info['take_profit_1'],
                take_profit_2=log_info['take_profit_2'],
                take_profit_3=log_info['take_profit_3'],
                take_profit_4=log_info['take_profit_4'],
                take_profit_5=log_info['take_profit_5']
            )

            try:
                current_balance = bybit.get_balance()
            except Exception as e:
                current_balance = 'Error'
                print(e.with_traceback())

            # Json output for Get request
            message = {
                'symbol': symbol,
                'order_price': order_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'contract_type': contract_type,
                'leverage': leverage,
                'token_quantity': token_quantity,
                'valid_action': valid_action,
                'balance': current_balance
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
            total_position: int,
            initial_margin_percent: int,
            total_deposit: float) -> Tuple[float, float]:
    # calculating leverage
    try:
        total_loss = total_deposit * total_position
        coef = 1 if contract_type == 'short' else -1
        percent_of_loss = (order_price - stop_loss) / order_price * coef
        percent_of_profit = (order_price - take_profit) / order_price * coef
        real_position_size = total_deposit * initial_margin_percent
        leverage = abs((total_loss / percent_of_loss) / real_position_size)
        leveraged_percent_of_loss = percent_of_loss * leverage
        leveraged_percent_of_profit = percent_of_profit * leverage
        total_profit = leveraged_percent_of_profit * real_position_size
        reward_risk = abs(total_profit / total_loss)
        # There are two 'total loss' in csv file, are they different?

        # take profits
        take_profit_1 = abs(((order_price - take_profit) * coef / 5 * 1) + (coef * -1 * order_price))
        take_profit_2 = abs(((order_price - take_profit) * coef / 5 * 2) + (coef * -1 * order_price))
        take_profit_3 = abs(((order_price - take_profit) * coef / 5 * 3) + (coef * -1 * order_price))
        take_profit_4 = abs(((order_price - take_profit) * coef / 5 * 4) + (coef * -1 * order_price))
        take_profit_5 = abs(((order_price - take_profit) * coef / 5 * 5) + (coef * -1 * order_price))

        # liquidation price
        coef_leverage = 0.005 if symbol == "BTCUSDT" else 0.01
        liquidation_price = ((order_price * leverage) / (abs(leverage + (coef * -1) + (coef * coef_leverage * leverage))))

        valid_action = True
        if liquidation_price < stop_loss and contract_type == "short":
            valid_action = False
        if liquidation_price > stop_loss and contract_type != "short":
            valid_action = False

        liquidation_price = round(liquidation_price, 3)
        leverage = round(leverage, 2)
        total_profit = round(total_profit, 2)
        leveraged_percent_of_loss = round(leveraged_percent_of_loss, 2)
        leveraged_percent_of_profit = round(leveraged_percent_of_profit, 2)
        reward_risk = round(reward_risk, 2)
        percent_of_loss = round(percent_of_loss, 2)

    except:
        leverage = 0
        percent_of_loss = 0
        percent_of_profit = 0
        reward_risk = 0
        liquidation_price = 0
        leveraged_percent_of_profit = 0
        leveraged_percent_of_loss = 0
        reward_risk = 0
        percent_of_loss = 0
        valid_action = False

    # calculating token quantity
    try:
        leveraged_position_size = real_position_size * leverage
        token_quantity = leveraged_position_size / order_price
        token_quantity = round(token_quantity, 2)
    except:
        token_quantity = 0

    log_info = {
        'percent_of_loss': percent_of_loss,
        'leveraged_percent_of_loss': leveraged_percent_of_loss,
        'percent_of_profit': percent_of_profit,
        'leveraged_percent_of_profit': leveraged_percent_of_profit,
        'total_profit': total_profit,
        'real_position_size': real_position_size,
        'leveraged_position_size': leveraged_position_size,
        'reward_risk': reward_risk,
        'take_profit_1': take_profit_1,
        'take_profit_2': take_profit_2,
        'take_profit_3': take_profit_3,
        'take_profit_4': take_profit_4,
        'take_profit_5': take_profit_5,
        'liquidation_price': liquidation_price,
        'total_loss': total_loss
    }

    return token_quantity, leverage, valid_action, log_info
