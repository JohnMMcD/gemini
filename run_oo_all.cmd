
@REM Order matters here - you don't want to create open orders and then cross them 
@REM with fill or kill orders. So we do the limit orders and maker orders later.
python -m unittest test_fill_or_kill_oo
python -m unittest test_http_error_codes_oo
python -m unittest test_immediate_or_cancel_oo
python -m unittest test_stop_limit_oo
python -m unittest test_maker_or_cancel_oo
