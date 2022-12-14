from pybit import inverse_perpetual


def get_api_data():
    api_key = 'c8opp8Ian7V4qEFC9E'
    api_secret = 'qBcXgBcr9GxGgX5yuJKwVtMBgw0YYePx9uB5'
    return api_key, api_secret


def get_balance():
    api_credentials = get_api_data()
    api_key = api_credentials[0]
    api_secret = api_credentials[1]
    session_auth = inverse_perpetual.HTTP(
        api_key=api_key,
        api_secret=api_secret
    )
    balance = session_auth.get_wallet_balance()

    return balance
