#!/bin/env bash

# Order matters here - you don't want to create open orders and then cross them
# with fill or kill orders. So we do the limit orders and maker orders later.

# Add -v for more verbosity
PYUnit="python3 -m unittest"
${PYUnit} test_fill_or_kill_oo
${PYUnit} test_http_error_codes_oo
${PYUnit} test_immediate_or_cancel_oo
${PYUnit} test_stop_limit_oo
${PYUnit} test_maker_or_cancel_oo
${PYUnit} test_auction_only_oo
${PYUnit} test_indication_of_interest_oo
