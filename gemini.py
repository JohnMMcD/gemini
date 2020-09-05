# Constant-ish attributes
BASE_URL = "https://api.sandbox.gemini.com"
ENDPOINT = "/v1/order/new"
URL = BASE_URL + ENDPOINT

# from https://docs.gemini.com/rest-api/#all-supported-symbols
# btcusd ethbtc ethusd zecusd zecbtc zeceth zecbch 
# zecltc bchusd bchbtc bcheth ltcusd ltcbtc ltceth 
# ltcbch batusd daiusd linkusd oxtusd batbtc 
# linkbtc oxtbtc bateth linketh oxteth
SUPPORTED_SYMBOLS_REGEX =  "btcusd|ethbtc|ethusd|zecusd|zecbtc|zeceth|zecbch"
SUPPORTED_SYMBOLS_REGEX += "|zecltc|bchusd|bchbtc|bcheth|ltcusd|ltcbtc|ltceth"
SUPPORTED_SYMBOLS_REGEX += "|ltcbch|batusd|daiusd|linkusd|oxtusd|batbtc"
SUPPORTED_SYMBOLS_REGEX += "|linkbtc|oxtbtc|bateth|linketh|oxteth"

class NSFError(Exception):
    pass
