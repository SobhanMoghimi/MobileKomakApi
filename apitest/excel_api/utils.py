from typing import Tuple
import traceback


def process(symbol: str,
            order_price: float,
            stop_loss: float,
            take_profit: float,
            contract_type: str,
            total_position: float,
            initial_margin_percent: float,
            total_deposit: float) -> Tuple[float, float, bool, dict]:
    # calculating leverage
    try:
        leverage = 0
        percent_of_loss = 0
        percent_of_profit = 0
        reward_risk = 0
        liquidation_price = 0
        leveraged_percent_of_profit = 0
        leveraged_percent_of_loss = 0
        reward_risk = 0
        percent_of_loss = 0
        total_profit = 0
        real_position_size = 0
        valid_action = False
        total_loss = 0
        take_profit_1 = 0
        take_profit_2 = 0
        take_profit_3 = 0
        take_profit_4 = 0
        take_profit_5 = 0

        total_loss = total_deposit * total_position
        coef = 1 if contract_type == 'short' else -1
        percent_of_loss = ((order_price - stop_loss) / order_price) * coef
        percent_of_profit = ((order_price - take_profit) / order_price) * coef
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
        liquidation_price = ((order_price * leverage) /
                             (abs(leverage + (coef * -1) + (coef * coef_leverage * leverage))))
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

    except Exception as e:
        print('Error in process function', e)
        print('Traceback:', traceback.format_exc())

    # calculating token quantity
    try:
        token_quantity = 0
        leveraged_position_size = 0
        leveraged_position_size = real_position_size * leverage
        token_quantity = leveraged_position_size / order_price
        token_quantity = round(token_quantity, 2)
    except Exception as e:
        print('Error in process function', e)
        print('Traceback:', traceback.format_exc())

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
