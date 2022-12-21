from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from excel_api import serializers, bybit, utils
# from excel_api.bybit import BybitApi
from .models import ExcelData, ConstantDatas
import traceback


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

        bybit_connection = bybit.BybitApi()
        out_balance = bybit.BybitApi().get_wallet_balance()

        return Response({'message': 'Hello!', 'bybit': out_balance})

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
        return Response('Waiting For Post Request')

    def post(self, request, format=None):

        # request_json = JSONParser().parse(request)

        # print(request_json)
        data = request.data

        if "side" in data.keys():
            if data["side"] == "sell":
                data["contract_type"] = "short"
            else:
                data["contract_type"] = "long"

        if "entry" in data.keys():
            data["order_price"] = data["entry"]["0"]["price"]

        if "stop" in data.keys():
            data["stop_loss"] = data["stop"]["0"]["price"]

        if "target" in data.keys():
            data["take_profit"] = data["target"]["0"]["price"]

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            symbol = serializer.validated_data.get('symbol')
            order_price = float(serializer.validated_data.get('order_price'))
            stop_loss = float(serializer.validated_data.get('stop_loss'))
            take_profit = float(serializer.validated_data.get('take_profit'))
            contract_type = serializer.validated_data.get('contract_type')

            constant_objects = ConstantDatas.objects.last()
            signal = constant_objects.signal
            total_position = constant_objects.total_position
            initial_margin = constant_objects.initial_margin
            total_deposit = constant_objects.total_deposit

            token_quantity, leverage, valid_action, log_info = utils.process(symbol,
                                                                             order_price,
                                                                             stop_loss,
                                                                             take_profit,
                                                                             contract_type,
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
                bybit_connection = bybit.BybitApi()
                current_balance = bybit_connection.get_wallet_balance()
            except Exception as e:
                current_balance = 'Error'
                print('Error in calling bybit balance: ', e)
                print('Traceback:', traceback.format_exc())

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
