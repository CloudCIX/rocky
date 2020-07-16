# CHANGELOG

## 0.3.5
- Minor bug fixes

## 0.3.4
- Added `ADMINISTRATOR_ENCRYP_PASS`, `API_USER_PASS`, `RADIUS_SERVER_ADDRESS`, `RADIUS_SERVER_SECRET`,
  `MAP_ACCESS_LIST` to main settings in settings.py.
- Added `COP_ACCESS_LIST` to cloud settings in settings.py.
- Added `pod` to cloud settings in settings.py.
- In cloud pod and regions settings, added `IPv4_link_subnet`, `IPv4_pod_subnets`, `IPv6_link_subnet`,
  `IPv6_pod_subnets`, `IPv4_RFC1918_subnets`and `vpns`.
- In cloud pod and regions settings, removed `ROUTER_USER`, `ROUTER_PASSWORD`, `COP_IPV4`, `COP_IPV6`,
  `ROCKY`, `IPv4`, `IPv6`.
- Updated router_scrub.py to use the above setting changes to initialise an SRX router in preparation
  for installation in a CloudCIX region

## 0.3.3
- Minor bug fixes

## 0.3.2
- Add `PORTS_PATH` variable to settings file

## 0.3.1
- Minor bug fixes

## 0.3.0
- Initial deployment
