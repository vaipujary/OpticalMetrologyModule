import re


data = r""" Time taken to process frame 0: 0.1505 seconds
Time taken to process frame 0: 0.1401 seconds
Time taken to process frame 0: 0.1480 seconds
Time taken to process frame 1: 0.0746 seconds
Time taken to process frame 1: 0.0711 seconds
Time taken to process frame 1: 0.0800 seconds
Time taken to process frame 0: 0.1523 seconds
Time taken to process frame 2: 0.0703 seconds
Time taken to process frame 0: 0.1578 seconds
Time taken to process frame 2: 0.1036 seconds
Time taken to process frame 1: 0.0485 seconds
Time taken to process frame 0: 0.1475 seconds
Time taken to process frame 2: 0.1153 seconds
Time taken to process frame 1: 0.0455 seconds
Time taken to process frame 3: 0.1313 seconds
Time taken to process frame 3: 0.1230 seconds
Time taken to process frame 1: 0.0909 seconds
Time taken to process frame 0: 0.1613 seconds
Time taken to process frame 2: 0.1582 seconds
Time taken to process frame 3: 0.1028 seconds
Time taken to process frame 0: 0.1839 seconds
Time taken to process frame 0: 0.1649 seconds
Time taken to process frame 4: 0.0840 seconds
Time taken to process frame 4: 0.0475 seconds
Time taken to process frame 0: 0.1962 seconds
Time taken to process frame 2: 0.1827 seconds
Time taken to process frame 1: 0.1102 seconds
Time taken to process frame 3: 0.1217 seconds
Time taken to process frame 1: 0.0648 seconds
Time taken to process frame 2: 0.1823 seconds
Time taken to process frame 1: 0.1168 seconds
Time taken to process frame 4: 0.1428 seconds
Time taken to process frame 5: 0.1173 seconds
Time taken to process frame 5: 0.1296 seconds
Time taken to process frame 1: 0.1177 seconds
Time taken to process frame 3: 0.0811 seconds
Time taken to process frame 2: 0.1162 seconds
Time taken to process frame 2: 0.1713 seconds
Time taken to process frame 4: 0.1723 seconds
Time taken to process frame 3: 0.0320 seconds
Time taken to process frame 6: 0.1206 seconds
Time taken to process frame 3: 0.1750 seconds
Time taken to process frame 6: 0.1090 seconds
Time taken to process frame 2: 0.1576 seconds
Time taken to process frame 2: 0.0930 seconds
Time taken to process frame 5: 0.2182 seconds
Time taken to process frame 3: 0.2161 seconds
Time taken to process frame 4: 0.2513 seconds
Time taken to process frame 6: 0.0652 seconds
Time taken to process frame 7: 0.1768 seconds
Time taken to process frame 3: 0.1438 seconds
Time taken to process frame 4: 0.2541 seconds
Time taken to process frame 5: 0.2747 seconds
Time taken to process frame 4: 0.0655 seconds
Time taken to process frame 4: 0.2610 seconds
Time taken to process frame 7: 0.2537 seconds
Time taken to process frame 8: 0.0870 seconds
Queue size: 0
Time taken to process frame 7: 0.1075 seconds
Time taken to process frame 4: 0.1185 seconds
Time taken to process frame 3: 0.2828 seconds
Time taken to process frame 8: 0.0282 seconds
Time taken to process frame 8: 0.0742 seconds
Time taken to process frame 5: 0.2651 seconds
Time taken to process frame 6: 0.1720 seconds
Time taken to process frame 5: 0.1772 seconds
Time taken to process frame 5: 0.1308 seconds
Queue size: 0
Time taken to process frame 4: 0.0596 seconds
Time taken to process frame 5: 0.2603 seconds
Time taken to process frame 6: 0.0430 seconds
Time taken to process frame 9: 0.1649 seconds
Time taken to process frame 9: 0.2290 seconds
Time taken to process frame 6: 0.0571 seconds
Time taken to process frame 9: 0.1581 seconds
Time taken to process frame 6: 0.0523 seconds
Time taken to process frame 7: 0.1617 seconds
Time taken to process frame 5: 0.1241 seconds
Queue size: 0
Time taken to process frame 5: 0.1407 seconds
Time taken to process frame 0: 0.1191 seconds
Time taken to process frame 6: 0.1722 seconds
Time taken to process frame 6: 0.0496 seconds
Time taken to process frame 8: 0.0566 seconds
Time taken to process frame 10: 0.1412 seconds
Time taken to process frame 7: 0.1839 seconds
Time taken to process frame 7: 0.1147 seconds
Queue size: 0
Time taken to process frame 7: 0.1237 seconds
Time taken to process frame 1: 0.1449 seconds
Time taken to process frame 10: 0.2885 seconds
Time taken to process frame 10: 0.2583 seconds
Time taken to process frame 6: 0.2294 seconds
Time taken to process frame 9: 0.1220 seconds
Time taken to process frame 8: 0.1358 seconds
Time taken to process frame 7: 0.2603 seconds
Time taken to process frame 11: 0.1370 seconds
Queue size: 2
Time taken to process frame 2: 0.0925 seconds
Time taken to process frame 8: 0.1686 seconds
Time taken to process frame 11: 0.3304 seconds
Time taken to process frame 8: 0.2541 seconds
Time taken to process frame 7: 0.2421 seconds
Time taken to process frame 9: 0.1732 seconds
Time taken to process frame 11: 0.2480 seconds
Time taken to process frame 7: 0.2466 seconds
Time taken to process frame 12: 0.1405 seconds
Time taken to process frame 12: 0.0675 seconds
Time taken to process frame 3: 0.1350 seconds
Time taken to process frame 8: 0.2063 seconds
Queue size: 3
Time taken to process frame 9: 0.0750 seconds
Time taken to process frame 9: 0.1150 seconds
Time taken to process frame 8: 0.1810 seconds
Time taken to process frame 10: 0.3659 seconds
Time taken to process frame 13: 0.0985 seconds
Time taken to process frame 9: 0.0754 seconds
Time taken to process frame 8: 0.1333 seconds
Time taken to process frame 4: 0.1059 seconds
Time taken to process frame 14: 0.0841 seconds
Queue size: 1
Time taken to process frame 10: 0.2097 seconds
Time taken to process frame 10: 0.3036 seconds
Time taken to process frame 9: 0.1302 seconds
Time taken to process frame 10: 0.2550 seconds
Time taken to process frame 9: 0.1509 seconds
Time taken to process frame 11: 0.0861 seconds
Time taken to process frame 11: 0.2814 seconds
Time taken to process frame 11: 0.1096 seconds
Queue size: 0
Time taken to process frame 12: 0.0781 seconds
Time taken to process frame 13: 0.2207 seconds
Time taken to process frame 10: 0.3204 seconds
Time taken to process frame 5: 0.2577 seconds
Time taken to process frame 15: 0.2212 seconds
Time taken to process frame 12: 0.0953 seconds
Time taken to process frame 11: 0.1611 seconds
Time taken to process frame 10: 0.2370 seconds
Time taken to process frame 12: 0.1296 seconds
Time taken to process frame 14: 0.0880 seconds
Time taken to process frame 13: 0.0290 seconds
Queue size: 2
Time taken to process frame 11: 0.1800 seconds
Time taken to process frame 16: 0.1726 seconds
Time taken to process frame 12: 0.2809 seconds
Time taken to process frame 12: 0.1288 seconds
Time taken to process frame 13: 0.1653 seconds
Time taken to process frame 11: 0.1238 seconds
Time taken to process frame 10: 0.3176 seconds
Time taken to process frame 17: 0.0628 seconds
Time taken to process frame 6: 0.2783 seconds
Time taken to process frame 12: 0.1148 seconds
Time taken to process frame 14: 0.1449 seconds
Time taken to process frame 15: 0.1130 seconds
Queue size: 0
Time taken to process frame 13: 0.0885 seconds
Time taken to process frame 13: 0.1621 seconds
Time taken to process frame 15: 0.1171 seconds
Time taken to process frame 13: 0.3078 seconds
Time taken to process frame 12: 0.1643 seconds
Time taken to process frame 14: 0.2163 seconds
Time taken to process frame 14: 0.0411 seconds
Queue size: 1Time taken to process frame 7: 0.1903 seconds

Time taken to process frame 16: 0.1914 seconds
Time taken to process frame 14: 0.1825 seconds
Time taken to process frame 16: 0.1766 seconds
Time taken to process frame 17: 0.1017 seconds
Queue size: 0
Time taken to process frame 13: 0.3998 seconds
Time taken to process frame 13: 0.2737 seconds
Time taken to process frame 15: 0.2015 seconds
Time taken to process frame 18: 0.0486 seconds
Time taken to process frame 17: 0.1046 seconds
Time taken to process frame 8: 0.2059 seconds
Time taken to process frame 15: 0.2671 seconds
Time taken to process frame 11: 0.4789 seconds
Time taken to process frame 14: 0.2892 seconds
Time taken to process frame 15: 0.2162 seconds
Time taken to process frame 18: 0.1493 seconds
Time taken to process frame 14: 0.0612 seconds
Time taken to process frame 16: 0.0472 seconds
Queue size: 0
Time taken to process frame 18: 0.1262 seconds
Time taken to process frame 19: 0.1241 seconds
Time taken to process frame 14: 0.1335 seconds
Time taken to process frame 19: 0.0301 seconds
Time taken to process frame 15: 0.2255 seconds
Time taken to process frame 9: 0.1730 seconds
Time taken to process frame 16: 0.1122 seconds
Time taken to process frame 16: 0.1657 seconds
Time taken to process frame 19: 0.0801 seconds
Queue size: 4
Time taken to process frame 12: 0.2420 seconds
Time taken to process frame 16: 0.0588 seconds
Time taken to process frame 15: 0.1915 seconds
Time taken to process frame 17: 0.2228 seconds
Time taken to process frame 20: 0.1695 seconds
Time taken to process frame 15: 0.2171 seconds
Time taken to process frame 17: 0.1810 seconds
Time taken to process frame 18: 0.0858 seconds
Queue size: 0
Time taken to process frame 20: 0.1801 seconds
Time taken to process frame 17: 0.1725 seconds
Time taken to process frame 20: 0.2931 seconds
Time taken to process frame 17: 0.1747 seconds
Time taken to process frame 10: 0.2374 seconds
Time taken to process frame 16: 0.1746 seconds
Time taken to process frame 18: 0.1430 seconds
Time taken to process frame 16: 0.1714 seconds
Time taken to process frame 18: 0.0510 seconds
Time taken to process frame 21: 0.1730 seconds
Queue size: 0
Time taken to process frame 18: 0.0740 seconds
Time taken to process frame 19: 0.1627 seconds
Time taken to process frame 21: 0.1940 seconds
Time taken to process frame 17: 0.0826 seconds
Time taken to process frame 21: 0.1956 seconds
Time taken to process frame 13: 0.1862 seconds
Time taken to process frame 11: 0.1668 seconds
Time taken to process frame 19: 0.1267 seconds
Time taken to process frame 22: 0.1218 seconds
Time taken to process frame 22: 0.0992 seconds
Time taken to process frame 19: 0.1994 seconds
Time taken to process frame 17: 0.1568 seconds
Queue size: 0
Time taken to process frame 12: 0.0412 seconds
Time taken to process frame 19: 0.1609 seconds
Time taken to process frame 22: 0.1278 seconds
Time taken to process frame 18: 0.0316 seconds
Time taken to process frame 18: 0.1134 seconds
Time taken to process frame 23: 0.0856 seconds
Queue size: 0Time taken to process frame 14: 0.2666 seconds

Time taken to process frame 20: 0.2671 seconds
Time taken to process frame 23: 0.0957 seconds
Time taken to process frame 13: 0.1538 seconds
Time taken to process frame 23: 0.2175 seconds
Time taken to process frame 20: 0.2636 seconds
Time taken to process frame 24: 0.0365 seconds
Time taken to process frame 19: 0.1563 seconds
Time taken to process frame 24: 0.1342 seconds
Queue size: 0
Time taken to process frame 15: 0.1928 seconds
Time taken to process frame 20: 0.3375 seconds
Time taken to process frame 19: 0.2460 seconds
Time taken to process frame 21: 0.1280 seconds
Time taken to process frame 21: 0.1519 seconds
Time taken to process frame 14: 0.1899 seconds
Time taken to process frame 24: 0.2292 seconds
Time taken to process frame 16: 0.0787 seconds
Time taken to process frame 21: 0.0965 seconds
Time taken to process frame 20: 0.1902 seconds
Queue size: 0
Time taken to process frame 20: 0.4898 seconds
Time taken to process frame 25: 0.2175 seconds
Time taken to process frame 22: 0.1711 seconds
Time taken to process frame 22: 0.1756 seconds
Time taken to process frame 15: 0.1883 seconds
Time taken to process frame 20: 0.1772 seconds
Time taken to process frame 17: 0.1832 seconds
Time taken to process frame 21: 0.1146 seconds
Time taken to process frame 25: 0.3807 seconds
Time taken to process frame 21: 0.1389 seconds
Time taken to process frame 26: 0.0887 seconds
Time taken to process frame 23: 0.0801 seconds
Time taken to process frame 18: 0.0373 seconds
Queue size: 1
Time taken to process frame 23: 0.0755 seconds
Time taken to process frame 21: 0.0725 seconds
Time taken to process frame 16: 0.0245 seconds
Time taken to process frame 22: 0.2073 seconds
Time taken to process frame 22: 0.1212 seconds
Time taken to process frame 27: 0.0872 seconds
Time taken to process frame 26: 0.1343 seconds
Queue size: 0
Time taken to process frame 25: 0.1760 seconds
Time taken to process frame 24: 0.1351 seconds
Time taken to process frame 22: 0.1282 seconds
Time taken to process frame 23: 0.0422 seconds
Time taken to process frame 19: 0.1368 seconds
Time taken to process frame 24: 0.1722 seconds
Time taken to process frame 17: 0.1365 seconds
Time taken to process frame 22: 0.2134 seconds
Queue size: 0
Time taken to process frame 27: 0.1285 seconds
Time taken to process frame 24: 0.1497 seconds
Time taken to process frame 28: 0.2446 seconds
Time taken to process frame 23: 0.0885 seconds
Time taken to process frame 18: 0.1085 seconds
Time taken to process frame 26: 0.2114 seconds
Time taken to process frame 28: 0.0926 seconds
Time taken to process frame 25: 0.2646 seconds
Time taken to process frame 23: 0.2225 seconds
Queue size: 0
Time taken to process frame 27: 0.0737 seconds
Time taken to process frame 24: 0.1281 seconds
Time taken to process frame 29: 0.2325 seconds
Time taken to process frame 24: 0.1230 seconds
Time taken to process frame 25: 0.3851 seconds
Time taken to process frame 19: 0.2005 seconds
Queue size: 0
Time taken to process frame 26: 0.2005 seconds
Time taken to process frame 23: 0.4636 seconds
Time taken to process frame 29: 0.2592 seconds
Time taken to process frame 28: 0.1863 seconds
Time taken to process frame 20: 0.5236 seconds
Time taken to process frame 25: 0.4440 seconds
Time taken to process frame 30: 0.1900 seconds
Queue size: 0
Time taken to process frame 26: 0.2627 seconds
Time taken to process frame 26: 0.1223 seconds
Time taken to process frame 21: 0.1608 seconds
Time taken to process frame 20: 0.2883 seconds
Time taken to process frame 30: 0.2901 seconds
Time taken to process frame 25: 0.3778 seconds
Time taken to process frame 24: 0.2635 seconds
Time taken to process frame 29: 0.2513 seconds
Time taken to process frame 25: 0.4806 seconds
Queue size: 0
Time taken to process frame 31: 0.2767 seconds
Time taken to process frame 27: 0.3196 seconds
Time taken to process frame 27: 0.2297 seconds
Time taken to process frame 22: 0.2604 seconds
Time taken to process frame 21: 0.2204 seconds
Time taken to process frame 27: 0.3255 seconds
Queue size: 0
Time taken to process frame 31: 0.2331 seconds
Time taken to process frame 32: 0.2053 seconds
Time taken to process frame 26: 0.2663 seconds
Time taken to process frame 28: 0.1483 seconds
Time taken to process frame 25: 0.3544 seconds
Time taken to process frame 22: 0.1503 seconds
Time taken to process frame 30: 0.2978 seconds
Queue size: 0
Time taken to process frame 28: 0.1956 seconds
Time taken to process frame 26: 0.4388 seconds
Time taken to process frame 33: 0.1299 seconds
Time taken to process frame 29: 0.1149 seconds
Time taken to process frame 32: 0.1604 seconds
Time taken to process frame 26: 0.1170 seconds
Time taken to process frame 28: 0.3493 seconds
Time taken to process frame 23: 0.1230 seconds
Time taken to process frame 27: 0.1772 seconds
Time taken to process frame 23: 0.3514 seconds
Time taken to process frame 34: 0.0608 seconds
Time taken to process frame 24: 0.0678 seconds
Time taken to process frame 29: 0.1871 seconds
Queue size: 1
Time taken to process frame 31: 0.2419 seconds
Time taken to process frame 27: 0.2034 seconds
Time taken to process frame 27: 0.2196 seconds
Time taken to process frame 33: 0.2260 seconds
Time taken to process frame 24: 0.2145 seconds
Time taken to process frame 25: 0.1821 seconds
Queue size: 0
Time taken to process frame 28: 0.1289 seconds
Time taken to process frame 35: 0.2342 seconds
Time taken to process frame 30: 0.3604 seconds
Time taken to process frame 28: 0.3228 seconds
Time taken to process frame 32: 0.2878 seconds
Time taken to process frame 29: 0.1997 seconds
Time taken to process frame 34: 0.1916 seconds
Queue size: 0
Time taken to process frame 36: 0.1719 seconds
Time taken to process frame 33: 0.0810 seconds
Time taken to process frame 29: 0.2039 seconds
Time taken to process frame 28: 0.3583 seconds
Time taken to process frame 30: 0.4624 seconds
Time taken to process frame 31: 0.2438 seconds
Time taken to process frame 26: 0.3285 seconds
Queue size: 0
Time taken to process frame 25: 0.4105 seconds
Time taken to process frame 37: 0.2054 seconds
Time taken to process frame 29: 0.3555 seconds
Time taken to process frame 34: 0.2297 seconds
Time taken to process frame 35: 0.3358 seconds
Time taken to process frame 32: 0.1761 seconds
Time taken to process frame 31: 0.2326 seconds
Time taken to process frame 27: 0.2202 seconds
Queue size: 3
Time taken to process frame 26: 0.2096 seconds
Time taken to process frame 38: 0.1931 seconds
Time taken to process frame 30: 0.4899 seconds
Time taken to process frame 29: 0.3748 seconds
Time taken to process frame 36: 0.1863 seconds
Time taken to process frame 30: 0.4628 seconds
Time taken to process frame 32: 0.2141 seconds
Queue size: 0
Time taken to process frame 27: 0.1638 seconds
Time taken to process frame 30: 0.3374 seconds
Time taken to process frame 28: 0.2218 secondsTime taken to process frame 39: 0.1584 seconds

Time taken to process frame 37: 0.1030 seconds
Time taken to process frame 33: 0.3134 seconds
Time taken to process frame 31: 0.1992 seconds
Time taken to process frame 35: 0.4620 seconds
Time taken to process frame 33: 0.1794 seconds
Time taken to process frame 34: 0.1192 seconds
Queue size: 2
Time taken to process frame 31: 0.2532 seconds
Time taken to process frame 28: 0.2064 seconds
Time taken to process frame 31: 0.2730 seconds
Time taken to process frame 30: 0.4233 seconds
Time taken to process frame 32: 0.2243 seconds
Time taken to process frame 35: 0.1301 seconds
Time taken to process frame 29: 0.1239 seconds
Time taken to process frame 34: 0.1841 seconds
Time taken to process frame 40: 0.3083 seconds
Queue size: 1
Time taken to process frame 36: 0.2221 seconds
Time taken to process frame 29: 0.2581 seconds
Time taken to process frame 38: 0.3128 seconds
Time taken to process frame 33: 0.1665 seconds
Time taken to process frame 32: 0.2169 seconds
Time taken to process frame 35: 0.1840 seconds
Time taken to process frame 31: 0.2670 seconds
Time taken to process frame 32: 0.3661 seconds
Queue size: 3
Time taken to process frame 34: 0.0864 seconds
Time taken to process frame 39: 0.1465 seconds
Time taken to process frame 33: 0.1058 seconds
Time taken to process frame 41: 0.2595 seconds
Time taken to process frame 36: 0.1165 seconds
Time taken to process frame 36: 0.3806 seconds
Time taken to process frame 37: 0.2749 seconds
Time taken to process frame 30: 0.3467 seconds
Queue size: 0
Time taken to process frame 32: 0.2168 seconds
Time taken to process frame 34: 0.1696 seconds
Time taken to process frame 37: 0.0692 seconds
Time taken to process frame 35: 0.2664 seconds
Time taken to process frame 40: 0.3120 seconds
Time taken to process frame 30: 0.5874 seconds
Time taken to process frame 31: 0.1477 seconds
Time taken to process frame 38: 0.2074 seconds
Queue size: 0
Time taken to process frame 33: 0.1865 seconds
Time taken to process frame 33: 0.2856 seconds
Time taken to process frame 42: 0.3976 seconds
Time taken to process frame 36: 0.1965 seconds
Time taken to process frame 37: 0.3827 seconds
Time taken to process frame 32: 0.1797 seconds
Time taken to process frame 38: 0.2906 seconds
Time taken to process frame 34: 0.1428 seconds
Queue size: 0
Time taken to process frame 34: 0.1423 seconds
Time taken to process frame 39: 0.2872 seconds
Time taken to process frame 39: 0.1420 seconds
Time taken to process frame 38: 0.2082 seconds
Time taken to process frame 37: 0.2481 seconds
Time taken to process frame 43: 0.2833 seconds
Queue size: 2
Time taken to process frame 35: 0.5487 seconds
Time taken to process frame 33: 0.2442 seconds
Time taken to process frame 35: 0.2811 seconds
Time taken to process frame 41: 0.5638 seconds
Time taken to process frame 31: 0.3773 seconds
Time taken to process frame 35: 0.3467 seconds
Time taken to process frame 40: 0.2203 seconds
Time taken to process frame 39: 0.2070 seconds
Time taken to process frame 40: 0.2939 seconds
Queue size: 0
Time taken to process frame 38: 0.1233 seconds
Time taken to process frame 44: 0.2402 seconds
Time taken to process frame 34: 0.1854 seconds
Time taken to process frame 32: 0.1071 seconds
Time taken to process frame 36: 0.2463 seconds
Time taken to process frame 41: 0.1225 seconds
Time taken to process frame 39: 0.1017 seconds
Time taken to process frame 36: 0.2286 seconds
Time taken to process frame 42: 0.1746 seconds
Queue size: 0
Time taken to process frame 36: 0.1959 seconds
Time taken to process frame 37: 0.0976 seconds
Time taken to process frame 38: 0.0266 seconds
Time taken to process frame 42: 0.1537 seconds
Time taken to process frame 35: 0.2499 seconds
Time taken to process frame 43: 0.0412 seconds
Time taken to process frame 41: 0.1279 seconds
Queue size: 0
Time taken to process frame 44: 0.0280 seconds
Time taken to process frame 45: 0.3458 seconds
Time taken to process frame 33: 0.3808 seconds
Time taken to process frame 42: 0.1185 seconds
Time taken to process frame 37: 0.3224 seconds
Time taken to process frame 43: 0.3139 seconds
Time taken to process frame 39: 0.2263 seconds
Queue size: 0
Time taken to process frame 44: 0.1100 seconds
Time taken to process frame 40: 0.4421 seconds
Time taken to process frame 36: 0.3709 seconds
Time taken to process frame 45: 0.3617 seconds
Queue size: 0
Time taken to process frame 38: 0.2546 seconds
Time taken to process frame 37: 0.1346 seconds
Time taken to process frame 34: 0.3668 seconds
Time taken to process frame 45: 0.2261 seconds
Time taken to process frame 43: 0.3683 seconds
Time taken to process frame 40: 0.3601 seconds
Queue size: 0
Time taken to process frame 39: 0.1905 seconds
Time taken to process frame 44: 0.1425 seconds
Time taken to process frame 46: 0.7489 seconds
Time taken to process frame 46: 0.4166 seconds
Queue size: 8
Time taken to process frame 37: 0.6902 seconds
Time taken to process frame 46: 0.4178 seconds
Time taken to process frame 41: 0.3568 seconds
Time taken to process frame 45: 0.2631 seconds
Queue size: 0
Time taken to process frame 38: 0.5900 seconds
Time taken to process frame 47: 0.1516 seconds
Time taken to process frame 40: 1.3431 seconds
Time taken to process frame 47: 0.1498 seconds
Time taken to process frame 38: 0.1588 seconds
Time taken to process frame 41: 0.8357 seconds
Time taken to process frame 42: 0.1665 seconds
Time taken to process frame 47: 0.2492 seconds
Queue size: 0
Time taken to process frame 40: 0.5946 seconds
Time taken to process frame 35: 0.2403 seconds
Time taken to process frame 46: 0.2040 seconds
Time taken to process frame 39: 0.2826 seconds
Time taken to process frame 48: 0.1496 seconds
Time taken to process frame 36: 0.1254 seconds
Time taken to process frame 42: 0.1098 seconds
Time taken to process frame 39: 0.1723 seconds
Time taken to process frame 48: 0.2810 seconds
Queue size: 0
Time taken to process frame 41: 0.1415 seconds
Time taken to process frame 41: 0.2982 seconds
Time taken to process frame 47: 0.1411 seconds
Time taken to process frame 37: 0.0942 seconds
Time taken to process frame 43: 0.3138 seconds
Time taken to process frame 40: 0.1411 seconds
Time taken to process frame 42: 0.0786 seconds
Time taken to process frame 48: 0.1098 seconds
Time taken to process frame 43: 0.1098 seconds
Time taken to process frame 49: 0.0781 seconds
Queue size: 0
Time taken to process frame 49: 0.1254 seconds
Time taken to process frame 42: 0.1476 seconds
Time taken to process frame 44: 0.1258 seconds
Time taken to process frame 48: 0.2825 seconds
Time taken to process frame 43: 0.1727 seconds
Queue size: 9
Time taken to process frame 50: 0.1884 seconds
Time taken to process frame 44: 0.2196 seconds
Time taken to process frame 43: 0.2196 seconds
Time taken to process frame 41: 0.3450 seconds
Time taken to process frame 49: 0.2982 seconds
Time taken to process frame 49: 0.1567 seconds
Time taken to process frame 38: 0.3607 seconds
Time taken to process frame 51: 0.1571 seconds
Queue size: 4
Time taken to process frame 40: 0.5651 seconds
Time taken to process frame 44: 0.2509 seconds
Time taken to process frame 45: 0.2170 seconds
Time taken to process frame 42: 0.1727 seconds
Time taken to process frame 44: 0.2196 seconds
Time taken to process frame 39: 0.1793 seconds
Queue size: 0
Time taken to process frame 50: 0.5273 seconds
Time taken to process frame 52: 0.2352 seconds
Time taken to process frame 43: 0.1254 seconds
Time taken to process frame 45: 0.6120 seconds
Time taken to process frame 46: 0.2196 seconds
Time taken to process frame 45: 0.2373 seconds
Queue size: 0
Time taken to process frame 53: 0.1415 seconds
Time taken to process frame 44: 0.1411 seconds
Time taken to process frame 51: 0.2825 seconds
Time taken to process frame 50: 0.5182 seconds
Time taken to process frame 41: 0.4396 seconds
Time taken to process frame 46: 0.1884 seconds
Time taken to process frame 40: 0.3299 seconds
Time taken to process frame 46: 0.1254 seconds
Time taken to process frame 50: 0.5807 seconds
Time taken to process frame 45: 0.4549 seconds
Time taken to process frame 54: 0.1571 seconds
Time taken to process frame 47: 0.2356 seconds
Queue size: 0
Time taken to process frame 52: 0.1255 seconds
Time taken to process frame 51: 0.0942 seconds
Time taken to process frame 47: 0.1571 seconds
Time taken to process frame 41: 0.1587 seconds
Time taken to process frame 42: 0.2196 secondsTime taken to process frame 47: 0.1567 seconds

Time taken to process frame 53: 0.0942 seconds
Time taken to process frame 45: 0.3294 seconds
Time taken to process frame 48: 0.0786 seconds
Queue size: 0
Time taken to process frame 42: 0.1098 seconds
Time taken to process frame 46: 0.1567 seconds
Time taken to process frame 48: 0.2509 seconds
Time taken to process frame 54: 0.0942 seconds
Time taken to process frame 51: 0.3294 seconds
Time taken to process frame 55: 0.3138 seconds
Time taken to process frame 52: 0.2665 seconds
Time taken to process frame 46: 0.2040 seconds
Time taken to process frame 43: 0.1255 seconds
Queue size: 1
Time taken to process frame 47: 0.1566 secondsTime taken to process frame 49: 0.2196 secondsTime taken to process frame 56: 0.0877 secondsTime taken to process frame 55: 0.1411 secondsTime taken to process frame 48: 0.2478 seconds
Time taken to process frame 43: 0.2200 seconds
Time taken to process frame 53: 0.0942 secondsTime taken to process frame 52: 0.1571 seconds



Time taken to process frame 49: 0.3385 seconds
Queue size: 0
Time taken to process frame 47: 0.2637 seconds


Time taken to process frame 44: 0.2438 seconds
Time taken to process frame 48: 0.1213 seconds
Time taken to process frame 53: 0.1538 seconds
Time taken to process frame 54: 0.1165 seconds
Time taken to process frame 57: 0.1345 seconds
Time taken to process frame 48: 0.0786 seconds
Time taken to process frame 50: 0.2315 seconds
Queue size: 0
Time taken to process frame 56: 0.0630 seconds
Time taken to process frame 49: 0.1761 seconds
Time taken to process frame 44: 0.1255 seconds
Time taken to process frame 50: 0.1098 seconds
Time taken to process frame 54: 0.0343 seconds
Time taken to process frame 58: 0.0287 seconds
Time taken to process frame 45: 0.1728 seconds
Time taken to process frame 49: 0.1411 seconds
Time taken to process frame 51: 0.0469 seconds
Time taken to process frame 51: 0.0473 seconds
Time taken to process frame 55: 0.1415 seconds
Queue size: 0
Time taken to process frame 49: 0.2158 seconds
Time taken to process frame 46: 0.0664 seconds
Time taken to process frame 55: 0.2292 seconds
Time taken to process frame 59: 0.1951 seconds
Queue size: 0
Time taken to process frame 57: 0.4213 seconds
Time taken to process frame 56: 0.1079 seconds
Queue size: 0
Time taken to process frame 45: 0.4949 seconds
Time taken to process frame 56: 0.3423 seconds
Time taken to process frame 50: 0.5923 seconds
Queue size: 0
Time taken to process frame 52: 0.4670 seconds
Time taken to process frame 58: 0.2584 seconds
Time taken to process frame 51: 0.1155 seconds
Time taken to process frame 52: 0.6342 seconds
Time taken to process frame 57: 0.3735 seconds
Queue size: 0
Time taken to process frame 50: 0.6947 seconds
Time taken to process frame 53: 0.1660 seconds
Time taken to process frame 50: 0.8915 seconds
Queue size: 0
Time taken to process frame 58: 0.2300 seconds
Time taken to process frame 51: 0.0916 seconds
Time taken to process frame 57: 0.5762 seconds
Time taken to process frame 58: 0.0613 seconds
Time taken to process frame 53: 0.5606 seconds
Time taken to process frame 59: 0.5340 seconds
Queue size: 0
Time taken to process frame 60: 1.0706 seconds
Time taken to process frame 54: 0.3847 seconds
Time taken to process frame 46: 0.8833 seconds
Time taken to process frame 59: 0.3790 seconds
Queue size: 0
Time taken to process frame 54: 0.2894 seconds
Time taken to process frame 52: 0.3843 seconds
Time taken to process frame 61: 0.2237 seconds
Time taken to process frame 51: 0.6261 seconds
Time taken to process frame 47: 1.2808 seconds
Time taken to process frame 52: 0.8630 seconds
Queue size: 0
Time taken to process frame 60: 0.4139 seconds
Time taken to process frame 53: 0.0615 seconds
Time taken to process frame 59: 0.6327 seconds
Time taken to process frame 55: 0.4765 seconds
Queue size: 0
Time taken to process frame 61: 0.3040 seconds
Time taken to process frame 60: 0.5605 seconds
Queue size: 0
Time taken to process frame 62: 0.5633 seconds
Time taken to process frame 48: 0.3692 seconds
Time taken to process frame 60: 0.4222 seconds
Queue size: 0
Time taken to process frame 63: 0.1591 seconds
Time taken to process frame 47: 0.7171 seconds
Time taken to process frame 53: 0.7743 seconds
Time taken to process frame 52: 0.8319 seconds
Time taken to process frame 61: 0.4371 seconds
Queue size: 0
Time taken to process frame 55: 1.0304 seconds
Time taken to process frame 49: 0.4181 seconds
Time taken to process frame 62: 0.6362 seconds
Queue size: 0
Time taken to process frame 54: 0.3585 seconds
Time taken to process frame 64: 0.3871 seconds
Time taken to process frame 53: 0.3320 seconds
Time taken to process frame 62: 0.3276 seconds
Time taken to process frame 61: 0.2881 seconds
Time taken to process frame 56: 0.9743 seconds
Time taken to process frame 54: 1.0471 seconds
Queue size: 0
Time taken to process frame 62: 0.2374 seconds
Queue size: 0
Time taken to process frame 63: 0.3353 seconds
Time taken to process frame 54: 0.3959 seconds
Time taken to process frame 65: 0.4468 seconds
Time taken to process frame 48: 0.6297 seconds
Time taken to process frame 63: 0.5939 seconds
Time taken to process frame 57: 0.4323 seconds
Queue size: 0
Time taken to process frame 66: 0.1363 seconds
Time taken to process frame 49: 0.1967 seconds
Time taken to process frame 55: 0.2466 seconds
Time taken to process frame 55: 0.7272 seconds
Time taken to process frame 63: 0.3461 seconds
Time taken to process frame 55: 0.5921 seconds
Time taken to process frame 64: 0.3429 seconds
Time taken to process frame 64: 0.2542 seconds
Time taken to process frame 56: 0.9820 seconds
Queue size: 2
Time taken to process frame 64: 0.1366 seconds
Time taken to process frame 56: 0.1577 seconds
Time taken to process frame 65: 0.1074 seconds
Time taken to process frame 50: 1.0782 seconds
Queue size: 0
Time taken to process frame 67: 0.3946 seconds
Time taken to process frame 56: 0.2789 seconds
Time taken to process frame 68: 0.0664 seconds
Time taken to process frame 50: 0.3985 seconds
Time taken to process frame 57: 0.2020 seconds
Time taken to process frame 58: 0.5410 seconds
Time taken to process frame 57: 0.1080 seconds
Time taken to process frame 56: 0.4259 seconds
Queue size: 0
Time taken to process frame 57: 0.4297 seconds
Time taken to process frame 69: 0.1608 seconds
Time taken to process frame 65: 0.5392 seconds
Time taken to process frame 65: 0.5174 seconds
Time taken to process frame 66: 0.4003 seconds
Time taken to process frame 58: 0.1393 seconds
Queue size: 0
Time taken to process frame 58: 0.2784 seconds
Time taken to process frame 59: 0.3552 seconds
Time taken to process frame 51: 0.5223 seconds
Time taken to process frame 57: 0.2226 seconds
Time taken to process frame 67: 0.1459 seconds
Time taken to process frame 70: 0.2857 seconds
Time taken to process frame 66: 0.2680 seconds
Time taken to process frame 58: 0.5142 seconds
Queue size: 3
Time taken to process frame 59: 0.2530 seconds
Time taken to process frame 66: 0.3617 seconds
Time taken to process frame 59: 0.2411 seconds
Time taken to process frame 68: 0.2076 seconds
Time taken to process frame 52: 0.2361 seconds
Time taken to process frame 59: 0.1407 seconds
Time taken to process frame 51: 0.7091 seconds
Time taken to process frame 67: 0.1907 seconds
Time taken to process frame 67: 0.1280 seconds
Queue size: 0
Time taken to process frame 60: 0.3416 seconds
Time taken to process frame 53: 0.1358 seconds
Time taken to process frame 60: 0.2654 seconds
Time taken to process frame 60: 0.1346 seconds
Time taken to process frame 58: 0.3399 seconds
Time taken to process frame 71: 0.4319 seconds
Time taken to process frame 61: 0.1381 seconds
Time taken to process frame 54: 0.1078 seconds
Queue size: 0
Time taken to process frame 61: 0.1113 seconds
Time taken to process frame 68: 0.2242 seconds
Time taken to process frame 52: 0.3335 seconds
Time taken to process frame 69: 0.4179 seconds
Time taken to process frame 60: 0.4684 seconds
Time taken to process frame 72: 0.1927 seconds
Time taken to process frame 59: 0.2488 seconds
Time taken to process frame 61: 0.2688 seconds
Time taken to process frame 62: 0.1743 seconds
Time taken to process frame 62: 0.1625 seconds
Queue size: 0
Time taken to process frame 68: 0.4086 seconds
Time taken to process frame 69: 0.1795 seconds
Time taken to process frame 55: 0.2871 seconds
Time taken to process frame 73: 0.1178 seconds
Time taken to process frame 69: 0.0668 seconds
Time taken to process frame 63: 0.1737 seconds
Time taken to process frame 63: 0.1599 seconds
Time taken to process frame 61: 0.2504 seconds
Queue size: 8
Time taken to process frame 53: 0.3081 seconds
Time taken to process frame 70: 0.1715 seconds
Time taken to process frame 60: 0.3072 seconds
Time taken to process frame 74: 0.1948 seconds
Time taken to process frame 56: 0.2584 seconds
Time taken to process frame 71: 0.1439 seconds
Time taken to process frame 54: 0.1775 seconds
Queue size: 3
Time taken to process frame 62: 0.2784 seconds
Time taken to process frame 64: 0.2728 seconds
Time taken to process frame 64: 0.2595 seconds
Time taken to process frame 75: 0.1258 seconds
Time taken to process frame 57: 0.1007 seconds
Time taken to process frame 70: 0.3574 seconds
Time taken to process frame 62: 0.3142 seconds
Time taken to process frame 70: 0.4761 seconds
Time taken to process frame 58: 0.0869 seconds
Time taken to process frame 72: 0.2059 seconds
Queue size: 0Time taken to process frame 76: 0.1044 seconds

Time taken to process frame 61: 0.3965 seconds
Time taken to process frame 77: 0.0483 seconds
Time taken to process frame 78: 0.0308 seconds
Time taken to process frame 65: 0.2916 seconds
Time taken to process frame 59: 0.1388 seconds
Queue size: 0
Time taken to process frame 65: 0.2589 seconds
Time taken to process frame 71: 0.3341 seconds
Time taken to process frame 63: 0.2633 seconds
Time taken to process frame 79: 0.1027 seconds
Time taken to process frame 62: 0.2078 seconds
Time taken to process frame 55: 0.4383 seconds
Time taken to process frame 71: 0.2955 seconds
Time taken to process frame 66: 0.0860 seconds
Time taken to process frame 66: 0.1697 seconds
Time taken to process frame 63: 0.3696 seconds
Time taken to process frame 73: 0.3515 seconds
Queue size: 0Time taken to process frame 60: 0.2299 seconds

Time taken to process frame 67: 0.1597 seconds
Time taken to process frame 64: 0.2771 seconds
Time taken to process frame 72: 0.2127 seconds
Time taken to process frame 61: 0.1105 seconds
Time taken to process frame 80: 0.3130 seconds
Time taken to process frame 72: 0.2608 seconds
Time taken to process frame 64: 0.1746 seconds
Queue size: 0
Time taken to process frame 63: 0.3433 seconds
Time taken to process frame 67: 0.2913 seconds
Time taken to process frame 74: 0.2819 seconds
Time taken to process frame 56: 0.4131 seconds
Time taken to process frame 62: 0.1986 seconds
Time taken to process frame 73: 0.2406 seconds
Queue size: 0
Time taken to process frame 81: 0.2186 seconds
Time taken to process frame 68: 0.3341 seconds
Time taken to process frame 57: 0.1671 seconds
Time taken to process frame 82: 0.1576 seconds
Time taken to process frame 75: 0.2718 seconds
Queue size: 0
Time taken to process frame 74: 0.2192 seconds
Time taken to process frame 65: 0.4153 seconds
Time taken to process frame 63: 0.2577 seconds
Time taken to process frame 58: 0.1387 seconds
Time taken to process frame 73: 0.4149 seconds
Time taken to process frame 69: 0.1995 seconds
Time taken to process frame 64: 0.4031 seconds
Time taken to process frame 65: 0.5487 seconds
Time taken to process frame 83: 0.1886 seconds
Time taken to process frame 68: 0.4992 seconds
Time taken to process frame 66: 0.1495 seconds
Time taken to process frame 76: 0.1938 seconds
Queue size: 5
Time taken to process frame 59: 0.1846 seconds
Time taken to process frame 74: 0.1751 seconds
Time taken to process frame 75: 0.3267 seconds
Time taken to process frame 84: 0.1677 seconds
Time taken to process frame 64: 0.3244 seconds
Time taken to process frame 67: 0.1337 seconds
Time taken to process frame 70: 0.2878 seconds
Time taken to process frame 77: 0.1879 seconds
Time taken to process frame 66: 0.2705 seconds
Queue size: 0
Time taken to process frame 69: 0.3193 seconds
Time taken to process frame 71: 0.0954 seconds
Time taken to process frame 75: 0.2542 seconds
Time taken to process frame 67: 0.1001 seconds
Time taken to process frame 65: 0.4547 seconds
Queue size: 0
Time taken to process frame 76: 0.0828 seconds
Time taken to process frame 78: 0.2484 seconds
Time taken to process frame 85: 0.3341 seconds
Time taken to process frame 76: 0.3671 seconds
Time taken to process frame 68: 0.2728 seconds
Time taken to process frame 79: 0.1041 seconds
Time taken to process frame 68: 0.1985 seconds
Queue size: 4
Time taken to process frame 77: 0.1589 seconds
Time taken to process frame 60: 0.5848 seconds
Time taken to process frame 65: 0.4731 seconds
Time taken to process frame 72: 0.3287 seconds
Time taken to process frame 70: 0.3527 seconds
Time taken to process frame 66: 0.2921 seconds
Time taken to process frame 69: 0.1653 seconds
Time taken to process frame 80: 0.1223 seconds
Time taken to process frame 69: 0.1107 seconds
Time taken to process frame 78: 0.0979 seconds
Time taken to process frame 77: 0.2247 seconds
Queue size: 0
Time taken to process frame 86: 0.2991 seconds
Time taken to process frame 81: 0.0450 seconds
Time taken to process frame 78: 0.0440 seconds
Time taken to process frame 66: 0.1808 seconds
Time taken to process frame 71: 0.2473 seconds
Time taken to process frame 82: 0.1105 seconds
Time taken to process frame 61: 0.3294 seconds
Time taken to process frame 79: 0.2101 seconds
Queue size: 0
Time taken to process frame 70: 0.2626 seconds
Time taken to process frame 73: 0.3389 seconds
Time taken to process frame 79: 0.1785 seconds
Time taken to process frame 67: 0.3247 seconds
Time taken to process frame 87: 0.2396 seconds
Time taken to process frame 70: 0.3326 seconds
Time taken to process frame 74: 0.0420 seconds
Time taken to process frame 72: 0.1856 seconds
Time taken to process frame 71: 0.0325 seconds
Time taken to process frame 88: 0.0495 seconds
Time taken to process frame 67: 0.2916 seconds
Time taken to process frame 83: 0.1931 seconds
Queue size: 0
Time taken to process frame 71: 0.2031 seconds
Time taken to process frame 73: 0.1115 seconds
Time taken to process frame 80: 0.2596 seconds
Time taken to process frame 62: 0.2816 seconds
Time taken to process frame 89: 0.0825 seconds
Time taken to process frame 72: 0.1555 seconds
Time taken to process frame 75: 0.1951 seconds
Time taken to process frame 68: 0.0780 seconds
Time taken to process frame 68: 0.1466 seconds
Time taken to process frame 80: 0.2856 seconds
Time taken to process frame 84: 0.0775 seconds
Time taken to process frame 81: 0.0585 seconds
Queue size: 0
Time taken to process frame 74: 0.0544 seconds
Time taken to process frame 76: 0.0885 seconds
Time taken to process frame 72: 0.1600 seconds
Time taken to process frame 90: 0.1610 seconds
Time taken to process frame 69: 0.0636 seconds
Time taken to process frame 73: 0.1212 seconds
Time taken to process frame 69: 0.1373 seconds
Time taken to process frame 85: 0.1301 seconds
Time taken to process frame 82: 0.1155 seconds
Queue size: 0
Time taken to process frame 63: 0.0862 seconds
Time taken to process frame 81: 0.1268 seconds
Time taken to process frame 74: 0.0413 seconds
Time taken to process frame 73: 0.1055 seconds
Time taken to process frame 77: 0.1540 seconds
Time taken to process frame 91: 0.1243 seconds
Time taken to process frame 70: 0.1521 seconds
Time taken to process frame 86: 0.0810 seconds
Time taken to process frame 75: 0.2537 seconds
Time taken to process frame 64: 0.1316 seconds
Queue size: 0
Time taken to process frame 82: 0.1069 seconds
Time taken to process frame 75: 0.1178 seconds
Time taken to process frame 70: 0.2519 seconds
Time taken to process frame 87: 0.1363 seconds
Time taken to process frame 92: 0.1715 seconds
Time taken to process frame 83: 0.1657 seconds
Time taken to process frame 78: 0.1405 seconds
Time taken to process frame 93: 0.0350 seconds
Time taken to process frame 76: 0.1102 seconds
Queue size: 5
Time taken to process frame 83: 0.0975 seconds
Time taken to process frame 74: 0.1833 seconds
Time taken to process frame 76: 0.0349 seconds
Time taken to process frame 71: 0.1741 seconds
Time taken to process frame 71: 0.1144 seconds
Time taken to process frame 65: 0.1542 seconds
Time taken to process frame 84: 0.1521 seconds
Time taken to process frame 88: 0.1387 seconds
Time taken to process frame 77: 0.1487 seconds
Time taken to process frame 79: 0.1957 seconds
Queue size: 0
Time taken to process frame 94: 0.1957 seconds
Time taken to process frame 77: 0.1648 seconds
Time taken to process frame 72: 0.1422 seconds
Time taken to process frame 72: 0.1406 seconds
Time taken to process frame 75: 0.2277 seconds
Time taken to process frame 66: 0.1549 seconds
Time taken to process frame 84: 0.2077 seconds
Time taken to process frame 78: 0.1261 seconds
Queue size: 0Time taken to process frame 78: 0.0855 seconds

Time taken to process frame 85: 0.1901 seconds
Time taken to process frame 95: 0.0944 seconds
Time taken to process frame 76: 0.1530 seconds
Time taken to process frame 80: 0.2294 seconds
Time taken to process frame 89: 0.1349 seconds
Time taken to process frame 85: 0.1275 seconds
Time taken to process frame 67: 0.1095 seconds
Time taken to process frame 86: 0.0899 seconds
Time taken to process frame 79: 0.1049 seconds
Queue size: 0
Time taken to process frame 73: 0.1555 seconds
Time taken to process frame 79: 0.1078 seconds
Time taken to process frame 96: 0.0575 seconds
Time taken to process frame 73: 0.1016 seconds
Time taken to process frame 90: 0.0889 seconds
Time taken to process frame 77: 0.1069 seconds
Time taken to process frame 68: 0.0922 seconds
Time taken to process frame 81: 0.0436 seconds
Time taken to process frame 86: 0.1142 seconds
Time taken to process frame 87: 0.1327 seconds
Queue size: 0
Time taken to process frame 97: 0.1249 seconds
Time taken to process frame 80: 0.1136 seconds
Time taken to process frame 80: 0.1094 seconds
Time taken to process frame 74: 0.1214 seconds
Time taken to process frame 74: 0.1084 seconds
Time taken to process frame 91: 0.1157 seconds
Time taken to process frame 87: 0.0301 seconds
Time taken to process frame 78: 0.0936 seconds
Time taken to process frame 69: 0.0892 seconds
Time taken to process frame 82: 0.1104 seconds
Queue size: 0
Time taken to process frame 88: 0.1133 seconds
Time taken to process frame 98: 0.1003 seconds
Time taken to process frame 81: 0.1095 seconds
Time taken to process frame 81: 0.1010 seconds
Time taken to process frame 92: 0.0364 seconds
Time taken to process frame 75: 0.0963 seconds
Time taken to process frame 75: 0.0871 seconds
Time taken to process frame 79: 0.0445 seconds
Time taken to process frame 88: 0.0954 seconds
Queue size: 0
Time taken to process frame 83: 0.1082 seconds
Time taken to process frame 70: 0.1052 seconds
Time taken to process frame 82: 0.0447 seconds
Time taken to process frame 89: 0.1111 seconds
Time taken to process frame 93: 0.0384 seconds
Time taken to process frame 99: 0.1171 seconds
Time taken to process frame 76: 0.0325 seconds
Time taken to process frame 76: 0.0286 seconds
Time taken to process frame 82: 0.0960 seconds
Time taken to process frame 89: 0.0290 seconds
Queue size: 0
Time taken to process frame 71: 0.0608 seconds
Time taken to process frame 80: 0.1008 seconds
Time taken to process frame 84: 0.1250 seconds
Time taken to process frame 83: 0.1210 seconds
Time taken to process frame 90: 0.1745 seconds
Time taken to process frame 94: 0.1466 seconds
Time taken to process frame 77: 0.1297 seconds
Queue size: 0
Time taken to process frame 83: 0.1058 seconds
Time taken to process frame 100: 0.2241 seconds
Time taken to process frame 77: 0.1692 seconds
Time taken to process frame 72: 0.1089 seconds
Time taken to process frame 84: 0.0648 seconds
Time taken to process frame 81: 0.1623 seconds
Time taken to process frame 82: 0.0307 seconds
Time taken to process frame 78: 0.1485 seconds
Time taken to process frame 91: 0.1286 seconds
Queue size: 3
Time taken to process frame 90: 0.2856 seconds
Time taken to process frame 79: 0.0455 seconds
Time taken to process frame 84: 0.1786 seconds
Time taken to process frame 78: 0.1756 seconds
Time taken to process frame 85: 0.2046 seconds
Time taken to process frame 73: 0.1781 seconds
Time taken to process frame 95: 0.3007 seconds
Time taken to process frame 85: 0.4117 seconds
Queue size: 2Time taken to process frame 83: 0.2382 seconds

Time taken to process frame 92: 0.1732 seconds
Time taken to process frame 79: 0.1412 seconds
Time taken to process frame 86: 0.1157 seconds
Time taken to process frame 91: 0.2382 seconds
Time taken to process frame 74: 0.1219 seconds
Time taken to process frame 80: 0.2507 seconds
Time taken to process frame 93: 0.1201 seconds
Time taken to process frame 86: 0.1771 seconds
Queue size: 0
Time taken to process frame 101: 0.2766 seconds
Time taken to process frame 81: 0.1354 seconds
Time taken to process frame 84: 0.3014 seconds
Time taken to process frame 87: 0.2865 seconds
Time taken to process frame 87: 0.1544 seconds
Time taken to process frame 92: 0.2490 seconds
Time taken to process frame 102: 0.1526 seconds
Queue size: 0
Time taken to process frame 80: 0.4053 seconds
Time taken to process frame 96: 0.3000 seconds
Time taken to process frame 94: 0.2940 seconds
Time taken to process frame 82: 0.2411 seconds
Time taken to process frame 85: 0.2126 seconds
Queue size: 0
Time taken to process frame 93: 0.2265 seconds
Time taken to process frame 88: 0.3212 seconds
Time taken to process frame 97: 0.2285 seconds
Time taken to process frame 85: 0.6444 seconds
Time taken to process frame 88: 0.3920 seconds
Time taken to process frame 95: 0.3111 seconds
Queue size: 1
Time taken to process frame 94: 0.2318 seconds
Time taken to process frame 81: 0.4237 seconds
Time taken to process frame 75: 0.8282 seconds
Time taken to process frame 89: 0.2620 seconds
Time taken to process frame 98: 0.2777 seconds
Time taken to process frame 89: 0.2130 seconds
Queue size: 7
Time taken to process frame 82: 0.1649 seconds
Time taken to process frame 95: 0.1849 seconds
Time taken to process frame 103: 0.6409 seconds
Time taken to process frame 86: 0.5105 seconds
Time taken to process frame 96: 0.2902 seconds
Time taken to process frame 83: 0.5880 seconds
Queue size: 0
Time taken to process frame 99: 0.2435 seconds
Time taken to process frame 84: 0.1116 seconds
Time taken to process frame 83: 0.1948 seconds
Time taken to process frame 76: 0.4253 seconds
Time taken to process frame 104: 0.2614 seconds
Time taken to process frame 87: 0.2419 seconds
Time taken to process frame 90: 0.4110 seconds
Time taken to process frame 77: 0.0460 seconds
Queue size: 0
Time taken to process frame 97: 0.3262 seconds
Time taken to process frame 86: 0.6984 seconds
Time taken to process frame 90: 0.4908 seconds
Time taken to process frame 100: 0.3299 seconds
Time taken to process frame 96: 0.5072 seconds
Queue size: 0
Time taken to process frame 98: 0.1879 seconds
Time taken to process frame 87: 0.1414 seconds
Time taken to process frame 85: 0.3704 seconds
Time taken to process frame 78: 0.2368 seconds
Time taken to process frame 91: 0.2683 seconds
Time taken to process frame 91: 0.2274 seconds
Time taken to process frame 88: 0.4287 seconds
Time taken to process frame 88: 0.1159 seconds
Time taken to process frame 99: 0.1390 seconds
Time taken to process frame 105: 0.4753 seconds
Queue size: 0
Time taken to process frame 79: 0.1287 seconds
Time taken to process frame 97: 0.2291 seconds
Time taken to process frame 89: 0.1095 seconds
Time taken to process frame 84: 0.3619 seconds
Time taken to process frame 89: 0.1742 seconds
Time taken to process frame 98: 0.1090 seconds
Time taken to process frame 92: 0.2685 seconds
Queue size: 0
Time taken to process frame 86: 0.3317 seconds
Time taken to process frame 80: 0.1968 seconds
Time taken to process frame 101: 0.4389 seconds
Time taken to process frame 92: 0.3422 seconds
Time taken to process frame 85: 0.1676 seconds
Time taken to process frame 100: 0.2383 seconds
Time taken to process frame 90: 0.2637 seconds
Time taken to process frame 106: 0.3626 seconds
Time taken to process frame 90: 0.1690 seconds
Queue size: 3
Time taken to process frame 91: 0.0468 seconds
Time taken to process frame 102: 0.1764 seconds
Time taken to process frame 99: 0.2883 seconds
Time taken to process frame 81: 0.2335 seconds
Time taken to process frame 87: 0.2798 seconds
Time taken to process frame 93: 0.3548 seconds
Time taken to process frame 93: 0.2270 seconds
Queue size: 3
Time taken to process frame 107: 0.1902 seconds
Time taken to process frame 86: 0.3168 seconds
Time taken to process frame 101: 0.3041 seconds
Time taken to process frame 91: 0.2469 seconds
Time taken to process frame 103: 0.1756 seconds
Time taken to process frame 88: 0.1306 seconds
Time taken to process frame 82: 0.1822 seconds
Time taken to process frame 108: 0.0834 seconds
Time taken to process frame 94: 0.1307 seconds
Time taken to process frame 92: 0.3432 seconds
Time taken to process frame 94: 0.1916 seconds
Queue size: 0
Time taken to process frame 83: 0.1239 seconds
Time taken to process frame 89: 0.1929 seconds
Time taken to process frame 87: 0.1321 seconds
Time taken to process frame 104: 0.2383 seconds
Time taken to process frame 93: 0.0761 seconds
Time taken to process frame 92: 0.2915 seconds
Time taken to process frame 100: 0.4648 seconds
Queue size: 3
Time taken to process frame 95: 0.2890 seconds
Time taken to process frame 102: 0.1376 seconds
Time taken to process frame 84: 0.1592 seconds
Time taken to process frame 109: 0.2389 seconds
Time taken to process frame 90: 0.1511 seconds
Time taken to process frame 103: 0.0455 seconds
Time taken to process frame 101: 0.1165 seconds
Time taken to process frame 95: 0.2950 seconds
Queue size: 1
Time taken to process frame 93: 0.2506 seconds
Time taken to process frame 94: 0.3081 seconds
Time taken to process frame 110: 0.1391 seconds
Time taken to process frame 88: 0.2586 seconds
Time taken to process frame 105: 0.2001 seconds
Time taken to process frame 96: 0.2586 seconds
Time taken to process frame 85: 0.2296 seconds
Time taken to process frame 96: 0.1491 seconds
Time taken to process frame 111: 0.0890 seconds
Time taken to process frame 94: 0.1171 seconds
Queue size: 0
Time taken to process frame 91: 0.1566 seconds
Time taken to process frame 104: 0.2652 seconds
Time taken to process frame 102: 0.2472 seconds
Time taken to process frame 89: 0.0756 seconds
Time taken to process frame 106: 0.1296 seconds
Time taken to process frame 95: 0.1458 seconds
Time taken to process frame 92: 0.0468 seconds
Time taken to process frame 86: 0.1070 seconds
Time taken to process frame 97: 0.1435 seconds
Time taken to process frame 103: 0.1130 seconds
Queue size: 0
Time taken to process frame 105: 0.1155 seconds
Time taken to process frame 97: 0.1391 seconds
Time taken to process frame 90: 0.1560 seconds
Time taken to process frame 96: 0.0950 seconds
Time taken to process frame 95: 0.1876 seconds
Time taken to process frame 107: 0.1383 seconds
Time taken to process frame 112: 0.1873 seconds
Time taken to process frame 106: 0.0567 seconds
Queue size: 1
Time taken to process frame 87: 0.1350 seconds
Time taken to process frame 98: 0.0467 seconds
Time taken to process frame 93: 0.1665 seconds
Time taken to process frame 98: 0.1395 seconds
Time taken to process frame 104: 0.1295 seconds
Time taken to process frame 91: 0.0642 seconds
Time taken to process frame 96: 0.0410 seconds
Time taken to process frame 88: 0.0479 seconds
Time taken to process frame 97: 0.1115 seconds
Time taken to process frame 108: 0.0921 seconds
Queue size: 0
Time taken to process frame 107: 0.1330 seconds
Time taken to process frame 94: 0.0946 seconds
Time taken to process frame 99: 0.0894 seconds
Time taken to process frame 99: 0.1287 seconds
Time taken to process frame 113: 0.0404 seconds
Time taken to process frame 92: 0.0969 seconds
Time taken to process frame 98: 0.0569 seconds
Time taken to process frame 105: 0.1525 seconds
Time taken to process frame 97: 0.1299 seconds
Time taken to process frame 108: 0.0560 seconds
Time taken to process frame 89: 0.1258 seconds
Queue size: 1
Time taken to process frame 109: 0.1264 seconds
Time taken to process frame 100: 0.1251 seconds
Time taken to process frame 95: 0.1503 seconds
Time taken to process frame 114: 0.1226 seconds
Time taken to process frame 106: 0.0900 seconds
Time taken to process frame 98: 0.0638 seconds
Time taken to process frame 93: 0.1361 seconds
Time taken to process frame 99: 0.1471 seconds
Time taken to process frame 101: 0.0382 seconds
Queue size: 1
Time taken to process frame 100: 0.2367 seconds
Time taken to process frame 109: 0.1894 seconds
Time taken to process frame 90: 0.1728 seconds
Time taken to process frame 96: 0.1437 seconds
Time taken to process frame 94: 0.0760 seconds
Time taken to process frame 107: 0.1440 seconds
Time taken to process frame 99: 0.1526 seconds
Queue size: 0
Time taken to process frame 101: 0.0701 seconds
Time taken to process frame 91: 0.0721 seconds
Time taken to process frame 115: 0.2387 seconds
Time taken to process frame 110: 0.3282 seconds
Time taken to process frame 102: 0.1923 seconds
Time taken to process frame 97: 0.1438 seconds
Time taken to process frame 108: 0.1291 seconds
Time taken to process frame 95: 0.1589 seconds
Time taken to process frame 100: 0.2841 seconds
Queue size: 0
Time taken to process frame 111: 0.0913 seconds
Time taken to process frame 100: 0.2059 seconds
Time taken to process frame 103: 0.1510 seconds
Time taken to process frame 116: 0.1775 seconds
Time taken to process frame 102: 0.2515 seconds
Time taken to process frame 101: 0.1428 seconds
Time taken to process frame 109: 0.1620 seconds
Time taken to process frame 92: 0.3039 seconds
Queue size: 0
Time taken to process frame 96: 0.0854 seconds
Time taken to process frame 98: 0.3027 seconds
Time taken to process frame 102: 0.1133 seconds
Time taken to process frame 104: 0.2217 seconds
Time taken to process frame 112: 0.2986 seconds
Time taken to process frame 117: 0.2009 seconds
Time taken to process frame 110: 0.3684 seconds
Time taken to process frame 101: 0.2985 seconds
Queue size: 5
Time taken to process frame 113: 0.0525 seconds
Time taken to process frame 102: 0.0300 seconds
Time taken to process frame 99: 0.1548 seconds
Time taken to process frame 103: 0.2984 seconds
Time taken to process frame 97: 0.2846 seconds
Time taken to process frame 111: 0.1405 seconds
Time taken to process frame 93: 0.3540 seconds
Time taken to process frame 110: 0.2733 seconds
Time taken to process frame 103: 0.2714 seconds
Queue size: 0
Time taken to process frame 118: 0.2688 seconds
Time taken to process frame 104: 0.1748 seconds
Time taken to process frame 94: 0.0878 seconds
Time taken to process frame 105: 0.3399 seconds
Time taken to process frame 114: 0.2529 seconds
Time taken to process frame 112: 0.1790 seconds
Time taken to process frame 111: 0.1768 seconds
Time taken to process frame 100: 0.2670 seconds
Time taken to process frame 103: 0.3045 seconds
Time taken to process frame 104: 0.1710 seconds
Time taken to process frame 119: 0.1634 seconds
Queue size: 2
Time taken to process frame 98: 0.2444 seconds
Time taken to process frame 101: 0.1009 seconds
Time taken to process frame 106: 0.2482 seconds
Queue size: 0
Time taken to process frame 99: 0.1555 seconds
Time taken to process frame 102: 0.1230 seconds
Time taken to process frame 115: 0.3155 seconds
Time taken to process frame 113: 0.2950 seconds
Time taken to process frame 112: 0.3128 seconds
Time taken to process frame 105: 0.2726 seconds
Time taken to process frame 95: 0.4152 seconds
Time taken to process frame 105: 0.4596 seconds
Time taken to process frame 104: 0.3702 seconds
Time taken to process frame 114: 0.1193 seconds
Time taken to process frame 103: 0.1648 seconds
Queue size: 1
Time taken to process frame 120: 0.3970 seconds
Time taken to process frame 107: 0.2667 seconds
Time taken to process frame 96: 0.1331 seconds
Time taken to process frame 104: 0.0753 seconds
Time taken to process frame 97: 0.0722 seconds
Time taken to process frame 113: 0.2653 seconds
Time taken to process frame 106: 0.2242 seconds
Time taken to process frame 108: 0.1452 seconds
Time taken to process frame 116: 0.3356 seconds
Queue size: 8
Time taken to process frame 106: 0.3508 seconds
Time taken to process frame 100: 0.4475 seconds
Time taken to process frame 98: 0.1063 seconds
Time taken to process frame 105: 0.2498 seconds
Time taken to process frame 115: 0.3979 seconds
Queue size: 2
Time taken to process frame 105: 0.4827 seconds
Time taken to process frame 99: 0.1212 seconds
Time taken to process frame 107: 0.1955 seconds
Time taken to process frame 114: 0.2550 seconds
Time taken to process frame 107: 0.1935 seconds
Time taken to process frame 109: 0.2800 seconds
Time taken to process frame 121: 0.3570 seconds
Time taken to process frame 101: 0.2535 seconds
Time taken to process frame 106: 0.2173 seconds
Time taken to process frame 117: 0.3108 seconds
Time taken to process frame 116: 0.2107 seconds
Queue size: 0
Time taken to process frame 106: 0.1801 seconds
Time taken to process frame 108: 0.1978 seconds
Time taken to process frame 107: 0.1104 seconds
Time taken to process frame 102: 0.1285 seconds
Time taken to process frame 108: 0.2882 seconds
Time taken to process frame 118: 0.1176 seconds
Time taken to process frame 107: 0.1021 seconds
Time taken to process frame 108: 0.0448 seconds
Time taken to process frame 109: 0.0280 seconds
Queue size: 0
Time taken to process frame 117: 0.1749 seconds
Time taken to process frame 108: 0.0484 seconds
Time taken to process frame 109: 0.1770 seconds
Time taken to process frame 115: 0.4200 seconds
Time taken to process frame 122: 0.3215 seconds
Time taken to process frame 119: 0.1140 seconds
Time taken to process frame 103: 0.1620 seconds
Time taken to process frame 109: 0.0916 seconds
Queue size: 0
Time taken to process frame 110: 0.1775 seconds
Time taken to process frame 110: 0.4980 seconds
Time taken to process frame 109: 0.2594 seconds
Time taken to process frame 100: 0.5271 seconds
Time taken to process frame 111: 0.0878 seconds
Time taken to process frame 123: 0.2068 seconds
Time taken to process frame 104: 0.2049 seconds
Time taken to process frame 101: 0.1029 secondsQueue size: 0

Time taken to process frame 120: 0.3285 seconds
Time taken to process frame 118: 0.4161 seconds
Time taken to process frame 110: 0.2725 seconds
Time taken to process frame 110: 0.1906 seconds
Time taken to process frame 102: 0.1196 seconds
Time taken to process frame 105: 0.1650 seconds
Time taken to process frame 121: 0.0790 seconds
Time taken to process frame 116: 0.4560 seconds
Time taken to process frame 111: 0.0445 seconds
Time taken to process frame 110: 0.4810 seconds
Time taken to process frame 111: 0.0680 seconds
Queue size: 2
Time taken to process frame 106: 0.0495 seconds
Time taken to process frame 111: 0.3577 seconds
Time taken to process frame 111: 0.0625 seconds
Time taken to process frame 112: 0.3364 seconds
Time taken to process frame 103: 0.1160 seconds
Time taken to process frame 124: 0.3186 seconds
Time taken to process frame 119: 0.2346 seconds
Time taken to process frame 122: 0.1664 seconds
Time taken to process frame 112: 0.0581 seconds
Time taken to process frame 113: 0.0499 seconds
Time taken to process frame 107: 0.1614 seconds
Queue size: 0
Time taken to process frame 117: 0.1921 seconds
Time taken to process frame 112: 0.1626 seconds
Time taken to process frame 112: 0.1279 seconds
Time taken to process frame 104: 0.1168 seconds
Time taken to process frame 123: 0.1340 seconds
Time taken to process frame 120: 0.1414 seconds
Time taken to process frame 108: 0.0676 seconds
Time taken to process frame 112: 0.1971 seconds
Queue size: 0
Time taken to process frame 114: 0.1328 seconds
Time taken to process frame 113: 0.0378 seconds
Time taken to process frame 113: 0.1616 seconds
Time taken to process frame 125: 0.1923 seconds
Time taken to process frame 113: 0.0964 seconds
Time taken to process frame 118: 0.1380 seconds
Time taken to process frame 126: 0.0420 seconds
Time taken to process frame 121: 0.0817 seconds
Time taken to process frame 113: 0.0756 seconds
Time taken to process frame 105: 0.1400 seconds
Time taken to process frame 124: 0.1445 seconds
Time taken to process frame 114: 0.0559 seconds
Time taken to process frame 119: 0.0357 seconds
Queue size: 0
Time taken to process frame 115: 0.1496 seconds
Time taken to process frame 114: 0.1215 seconds
Time taken to process frame 114: 0.1481 seconds
Time taken to process frame 109: 0.1140 seconds
Time taken to process frame 106: 0.0514 seconds
Time taken to process frame 127: 0.1101 seconds
Time taken to process frame 114: 0.1213 seconds
Time taken to process frame 122: 0.1409 seconds
Time taken to process frame 116: 0.0384 seconds
Queue size: 1
Time taken to process frame 115: 0.1233 seconds
Time taken to process frame 125: 0.1575 seconds
Time taken to process frame 120: 0.1246 seconds
Time taken to process frame 115: 0.1347 seconds
Time taken to process frame 115: 0.1477 seconds
Time taken to process frame 123: 0.0846 seconds
Time taken to process frame 107: 0.1487 seconds
Queue size: 0
Time taken to process frame 128: 0.1800 seconds
Time taken to process frame 110: 0.2088 seconds
Time taken to process frame 115: 0.1502 seconds
Time taken to process frame 117: 0.1457 seconds
Time taken to process frame 116: 0.0720 seconds
Time taken to process frame 116: 0.1274 seconds
Time taken to process frame 116: 0.2078 seconds
Time taken to process frame 126: 0.1896 seconds
Time taken to process frame 111: 0.0909 seconds
Time taken to process frame 108: 0.0640 seconds
Time taken to process frame 121: 0.2246 seconds
Queue size: 3
Time taken to process frame 116: 0.1227 seconds
Time taken to process frame 129: 0.1555 seconds
Time taken to process frame 118: 0.1266 seconds
Time taken to process frame 117: 0.1385 seconds
Time taken to process frame 124: 0.2440 seconds
Time taken to process frame 117: 0.1460 seconds
Time taken to process frame 127: 0.1505 seconds
Queue size: 0
Time taken to process frame 122: 0.1605 seconds
Time taken to process frame 117: 0.1472 seconds
Time taken to process frame 117: 0.2816 seconds
Time taken to process frame 112: 0.2513 seconds
Time taken to process frame 109: 0.2513 seconds
Time taken to process frame 130: 0.2018 seconds
Time taken to process frame 118: 0.1538 seconds
Time taken to process frame 118: 0.1272 seconds
Time taken to process frame 119: 0.2008 seconds
Time taken to process frame 113: 0.0640 seconds
Time taken to process frame 131: 0.0280 seconds
Queue size: 0
Time taken to process frame 128: 0.1905 seconds
Time taken to process frame 123: 0.1847 seconds
Time taken to process frame 118: 0.1934 seconds
Time taken to process frame 125: 0.3219 seconds
Time taken to process frame 119: 0.1559 seconds
Time taken to process frame 119: 0.2030 seconds
Queue size: 0
Time taken to process frame 132: 0.1976 seconds
Time taken to process frame 118: 0.3238 seconds
Time taken to process frame 114: 0.1745 seconds
Time taken to process frame 124: 0.1735 seconds
Time taken to process frame 110: 0.3391 seconds
Time taken to process frame 119: 0.1955 seconds
Time taken to process frame 126: 0.1777 seconds
Time taken to process frame 120: 0.3382 seconds
Queue size: 0
Time taken to process frame 129: 0.3694 seconds
Time taken to process frame 125: 0.1781 seconds
Time taken to process frame 120: 0.2982 seconds
Time taken to process frame 111: 0.2102 seconds
Time taken to process frame 126: 0.0538 seconds
Time taken to process frame 119: 0.3078 seconds
Time taken to process frame 120: 0.3809 seconds
Queue size: 0
Time taken to process frame 133: 0.4060 seconds
Time taken to process frame 112: 0.1146 seconds
Time taken to process frame 127: 0.3504 seconds
Time taken to process frame 115: 0.4364 seconds
Time taken to process frame 121: 0.3491 seconds
Time taken to process frame 127: 0.1859 seconds
Time taken to process frame 120: 0.4341 seconds
Time taken to process frame 113: 0.1354 seconds
Time taken to process frame 130: 0.3904 seconds
Time taken to process frame 121: 0.2268 secondsTime taken to process frame 128: 0.0834 seconds

Queue size: 0
Time taken to process frame 121: 0.3704 seconds
Time taken to process frame 122: 0.1614 seconds
Time taken to process frame 120: 0.3431 seconds
Time taken to process frame 128: 0.2259 seconds
Time taken to process frame 114: 0.1040 seconds
Time taken to process frame 134: 0.2860 seconds
Time taken to process frame 122: 0.1340 seconds
Time taken to process frame 131: 0.0863 seconds
Time taken to process frame 123: 0.0488 seconds
Queue size: 0
Time taken to process frame 116: 0.3318 seconds
Time taken to process frame 121: 0.2718 seconds
Time taken to process frame 129: 0.1198 seconds
Time taken to process frame 129: 0.1418 seconds
Time taken to process frame 115: 0.1733 seconds
Time taken to process frame 124: 0.0823 seconds
Time taken to process frame 123: 0.1489 seconds
Time taken to process frame 135: 0.2060 seconds
Time taken to process frame 122: 0.0987 seconds
Time taken to process frame 132: 0.1619 seconds
Queue size: 0
Time taken to process frame 116: 0.0678 seconds
Time taken to process frame 121: 0.2512 seconds
Time taken to process frame 130: 0.1970 seconds
Time taken to process frame 124: 0.1339 seconds
Time taken to process frame 136: 0.1237 seconds
Time taken to process frame 122: 0.2571 seconds
Time taken to process frame 130: 0.2551 seconds
Time taken to process frame 125: 0.2413 seconds
Time taken to process frame 117: 0.1242 seconds
Queue size: 0
Time taken to process frame 131: 0.0680 seconds
Time taken to process frame 133: 0.2096 seconds
Time taken to process frame 123: 0.1957 seconds
Time taken to process frame 123: 0.0621 seconds
Time taken to process frame 137: 0.1499 seconds
Time taken to process frame 131: 0.1196 seconds
Time taken to process frame 132: 0.1497 seconds
Queue size: 0
Time taken to process frame 122: 0.2890 seconds
Time taken to process frame 126: 0.1405 seconds
Time taken to process frame 118: 0.1926 seconds
Time taken to process frame 134: 0.1506 seconds
Time taken to process frame 138: 0.1619 seconds
Time taken to process frame 124: 0.2011 seconds
Time taken to process frame 125: 0.3614 seconds
Time taken to process frame 132: 0.1224 seconds
Time taken to process frame 124: 0.2849 seconds
Time taken to process frame 127: 0.1860 seconds
Time taken to process frame 119: 0.1760 seconds
Time taken to process frame 133: 0.2122 seconds
Queue size: 4
Time taken to process frame 123: 0.1517 seconds
Time taken to process frame 126: 0.1184 seconds
Time taken to process frame 135: 0.2572 seconds
Time taken to process frame 139: 0.1852 seconds
Time taken to process frame 125: 0.1644 seconds
Time taken to process frame 117: 0.1393 seconds
Queue size: 0
Time taken to process frame 124: 0.1233 seconds
Time taken to process frame 134: 0.1457 seconds
Time taken to process frame 133: 0.3160 seconds
Time taken to process frame 128: 0.2651 seconds
Time taken to process frame 136: 0.1638 seconds
Time taken to process frame 120: 0.2985 seconds
Time taken to process frame 134: 0.1052 seconds
Time taken to process frame 126: 0.1885 seconds
Time taken to process frame 127: 0.2322 seconds
Queue size: 3
Time taken to process frame 125: 0.2088 seconds
Time taken to process frame 129: 0.1228 seconds
Time taken to process frame 125: 0.5390 seconds
Time taken to process frame 118: 0.3060 seconds
Time taken to process frame 137: 0.0769 seconds
Time taken to process frame 127: 0.1489 seconds
Time taken to process frame 135: 0.1752 seconds
Time taken to process frame 126: 0.0807 seconds
Time taken to process frame 128: 0.1464 seconds
Time taken to process frame 135: 0.3662 seconds
Queue size: 2
Time taken to process frame 140: 0.4857 seconds
Time taken to process frame 121: 0.3142 seconds
Time taken to process frame 126: 0.2282 seconds
Time taken to process frame 138: 0.1746 seconds
Time taken to process frame 129: 0.0953 seconds
Time taken to process frame 141: 0.1261 seconds
Queue size: 0
Time taken to process frame 127: 0.2177 seconds
Time taken to process frame 119: 0.3359 seconds
Time taken to process frame 136: 0.2390 seconds
Time taken to process frame 128: 0.3261 seconds
Time taken to process frame 136: 0.3221 seconds
Time taken to process frame 122: 0.2504 seconds
Time taken to process frame 139: 0.2047 seconds
Time taken to process frame 142: 0.1588 seconds
Time taken to process frame 127: 0.2738 seconds
Time taken to process frame 137: 0.0771 seconds
Queue size: 0
Time taken to process frame 120: 0.1624 seconds
Time taken to process frame 128: 0.2192 seconds
Time taken to process frame 123: 0.1553 seconds
Time taken to process frame 130: 0.6278 seconds
Time taken to process frame 129: 0.2073 seconds
Time taken to process frame 137: 0.2412 seconds
Time taken to process frame 130: 0.4133 seconds
Time taken to process frame 143: 0.2206 seconds
Time taken to process frame 138: 0.1112 seconds
Queue size: 0
Time taken to process frame 128: 0.2556 seconds
Time taken to process frame 129: 0.1405 seconds
Time taken to process frame 130: 0.1941 seconds
Time taken to process frame 124: 0.1852 seconds
Time taken to process frame 138: 0.2053 seconds
Queue size: 0
Time taken to process frame 140: 0.3559 seconds
Time taken to process frame 129: 0.1685 seconds
Time taken to process frame 131: 0.2512 seconds
Time taken to process frame 144: 0.1450 seconds
Time taken to process frame 121: 0.3933 seconds
Time taken to process frame 130: 0.2188 seconds
Time taken to process frame 139: 0.3064 seconds
Time taken to process frame 131: 0.2033 seconds
Time taken to process frame 139: 0.1730 seconds
Time taken to process frame 132: 0.1614 seconds
Queue size: 0
Time taken to process frame 125: 0.3105 seconds
Time taken to process frame 145: 0.2187 seconds
Time taken to process frame 132: 0.1569 seconds
Time taken to process frame 122: 0.2345 seconds
Time taken to process frame 131: 0.5609 seconds
Time taken to process frame 133: 0.1909 seconds
Queue size: 0
Time taken to process frame 131: 0.3012 seconds
Time taken to process frame 140: 0.2986 seconds
Time taken to process frame 140: 0.3166 seconds
Time taken to process frame 123: 0.1532 seconds
Time taken to process frame 133: 0.1886 seconds
Time taken to process frame 141: 0.0630 seconds
Time taken to process frame 134: 0.1352 seconds
Time taken to process frame 141: 0.5864 seconds
Time taken to process frame 132: 0.2690 seconds
Queue size: 0
Time taken to process frame 146: 0.3370 seconds
Time taken to process frame 126: 0.3583 seconds
Time taken to process frame 124: 0.1252 seconds
Time taken to process frame 132: 0.2365 seconds
Time taken to process frame 134: 0.1150 seconds
Time taken to process frame 142: 0.1547 seconds
Time taken to process frame 141: 0.2050 seconds
Time taken to process frame 142: 0.1010 seconds
Time taken to process frame 130: 0.6795 seconds
Time taken to process frame 127: 0.0694 seconds
Time taken to process frame 133: 0.1482 seconds
Queue size: 2
Time taken to process frame 133: 0.1876 seconds
Time taken to process frame 147: 0.1726 seconds
Time taken to process frame 143: 0.1409 seconds
Time taken to process frame 135: 0.1644 seconds
Time taken to process frame 135: 0.3332 seconds
Time taken to process frame 125: 0.2396 seconds
Time taken to process frame 143: 0.1673 seconds
Time taken to process frame 128: 0.1310 seconds
Time taken to process frame 142: 0.2017 seconds
Time taken to process frame 134: 0.0617 seconds
Queue size: 0
Time taken to process frame 136: 0.0710 seconds
Time taken to process frame 136: 0.0622 seconds
Time taken to process frame 131: 0.2679 seconds
Time taken to process frame 143: 0.0747 seconds
Time taken to process frame 134: 0.1344 seconds
Time taken to process frame 144: 0.0695 seconds
Time taken to process frame 148: 0.1394 seconds
Time taken to process frame 144: 0.1192 seconds
Time taken to process frame 137: 0.0797 seconds
Time taken to process frame 135: 0.1217 seconds
Queue size: 0
Time taken to process frame 126: 0.0770 seconds
Time taken to process frame 129: 0.1347 seconds
Time taken to process frame 132: 0.1134 seconds
Time taken to process frame 137: 0.1650 seconds
Time taken to process frame 145: 0.1176 seconds
Time taken to process frame 144: 0.1656 seconds
Time taken to process frame 136: 0.0721 seconds
Time taken to process frame 135: 0.1626 seconds
Time taken to process frame 149: 0.1276 seconds
Queue size: 0
Time taken to process frame 138: 0.1313 seconds
Time taken to process frame 145: 0.1800 seconds
Time taken to process frame 138: 0.0961 seconds
Time taken to process frame 130: 0.1580 seconds
Time taken to process frame 133: 0.1341 seconds
Time taken to process frame 127: 0.1582 seconds
Time taken to process frame 146: 0.1019 seconds
Time taken to process frame 136: 0.0886 seconds
Time taken to process frame 139: 0.0601 seconds
Time taken to process frame 137: 0.1341 seconds
Queue size: 0
Time taken to process frame 131: 0.0979 seconds
Time taken to process frame 150: 0.1464 seconds
Time taken to process frame 145: 0.2278 seconds
Time taken to process frame 134: 0.1574 seconds
Time taken to process frame 139: 0.1283 seconds
Time taken to process frame 128: 0.1693 seconds
Time taken to process frame 138: 0.0805 seconds
Time taken to process frame 147: 0.1659 seconds
Queue size: 0
Time taken to process frame 137: 0.1650 seconds
Time taken to process frame 151: 0.1181 seconds
Time taken to process frame 146: 0.2136 seconds
Time taken to process frame 140: 0.1566 seconds
Time taken to process frame 148: 0.0675 seconds
Time taken to process frame 135: 0.1887 seconds
Time taken to process frame 129: 0.1672 seconds
Time taken to process frame 146: 0.2257 seconds
Time taken to process frame 132: 0.2566 seconds
Time taken to process frame 138: 0.0872 seconds
Queue size: 1Time taken to process frame 139: 0.1958 seconds
Time taken to process frame 141: 0.0802 seconds

Time taken to process frame 147: 0.0828 seconds
Time taken to process frame 152: 0.1679 seconds
Time taken to process frame 140: 0.2324 seconds
Time taken to process frame 147: 0.1446 seconds
Time taken to process frame 136: 0.1927 seconds
Queue size: 0
Time taken to process frame 148: 0.0269 seconds
Time taken to process frame 133: 0.1086 seconds
Time taken to process frame 139: 0.1985 seconds
Time taken to process frame 141: 0.0996 seconds
Time taken to process frame 149: 0.3328 seconds
Time taken to process frame 149: 0.0964 seconds
Time taken to process frame 153: 0.2068 seconds
Time taken to process frame 148: 0.3041 seconds
Time taken to process frame 142: 0.2538 seconds
Queue size: 0
Time taken to process frame 140: 0.3679 seconds
Time taken to process frame 134: 0.2107 seconds
Time taken to process frame 130: 0.4341 seconds
Time taken to process frame 137: 0.2679 seconds
Time taken to process frame 140: 0.2690 seconds
Time taken to process frame 141: 0.0864 seconds
Time taken to process frame 142: 0.3065 seconds
Queue size: 0
Time taken to process frame 138: 0.0755 seconds
Time taken to process frame 149: 0.2777 seconds
Time taken to process frame 154: 0.3014 seconds
Time taken to process frame 131: 0.2124 seconds
Time taken to process frame 141: 0.1813 seconds
Time taken to process frame 143: 0.1468 seconds
Time taken to process frame 142: 0.1844 seconds
Time taken to process frame 150: 0.4292 seconds
Time taken to process frame 143: 0.3198 seconds
Queue size: 0
Time taken to process frame 139: 0.2078 seconds
Time taken to process frame 150: 0.5328 seconds
Time taken to process frame 150: 0.1753 seconds
Time taken to process frame 135: 0.4277 seconds
Time taken to process frame 132: 0.1868 seconds
Time taken to process frame 144: 0.1516 seconds
Time taken to process frame 151: 0.1665 seconds
Time taken to process frame 151: 0.1032 seconds
Queue size: 7
Time taken to process frame 142: 0.2809 seconds
Time taken to process frame 144: 0.2819 seconds
Time taken to process frame 151: 0.1988 seconds
Time taken to process frame 143: 0.3438 seconds
Time taken to process frame 152: 0.1837 seconds
Queue size: 0
Time taken to process frame 152: 0.1882 seconds
Time taken to process frame 152: 0.1297 seconds
Time taken to process frame 133: 0.2876 seconds
Time taken to process frame 153: 0.1057 seconds
Time taken to process frame 136: 0.3956 seconds
Time taken to process frame 154: 0.0665 seconds
Time taken to process frame 153: 0.1794 seconds
Queue size: 0
Time taken to process frame 140: 0.5754 seconds
Time taken to process frame 145: 0.4005 seconds
Time taken to process frame 144: 0.3308 seconds
Time taken to process frame 155: 0.8189 seconds
Time taken to process frame 143: 0.5338 seconds
Queue size: 0
Time taken to process frame 153: 0.4125 seconds
Time taken to process frame 141: 0.2009 seconds
Time taken to process frame 156: 0.1836 seconds
Time taken to process frame 145: 0.7937 seconds
Time taken to process frame 137: 0.4405 seconds
Time taken to process frame 145: 0.3046 seconds
Time taken to process frame 146: 0.3342 seconds
Time taken to process frame 134: 0.5661 seconds
Time taken to process frame 144: 0.2417 seconds
Queue size: 0
Time taken to process frame 155: 0.4632 seconds
Time taken to process frame 154: 0.2318 seconds
Time taken to process frame 154: 0.4508 seconds
Time taken to process frame 138: 0.1654 seconds
Queue size: 0
Time taken to process frame 157: 0.2936 seconds
Time taken to process frame 155: 0.2854 seconds
Time taken to process frame 147: 0.3404 seconds
Time taken to process frame 146: 0.4315 seconds
Queue size: 0
Time taken to process frame 139: 0.2766 seconds
Time taken to process frame 142: 0.6393 seconds
Time taken to process frame 146: 0.5056 seconds
Time taken to process frame 156: 0.4946 seconds
Queue size: 0
Time taken to process frame 145: 0.6101 seconds
Time taken to process frame 140: 0.2211 seconds
Time taken to process frame 156: 0.3272 seconds
Time taken to process frame 135: 0.6002 seconds
Time taken to process frame 147: 0.3617 seconds
Time taken to process frame 155: 0.6801 seconds
Queue size: 0
Time taken to process frame 156: 0.0890 seconds
Time taken to process frame 157: 0.3273 seconds
Time taken to process frame 147: 0.3597 seconds
Time taken to process frame 158: 0.7211 seconds
Time taken to process frame 148: 0.1926 seconds
Queue size: 0
Time taken to process frame 157: 0.4367 seconds
Time taken to process frame 157: 0.2636 seconds
Time taken to process frame 136: 0.4247 seconds
Time taken to process frame 146: 0.5794 seconds
Time taken to process frame 158: 0.3326 seconds
Queue size: 0
Time taken to process frame 148: 0.5245 seconds
Time taken to process frame 158: 0.1990 seconds
Time taken to process frame 149: 0.3270 seconds
Time taken to process frame 158: 0.2719 seconds
Time taken to process frame 159: 0.0440 seconds
Time taken to process frame 137: 0.2398 seconds
Time taken to process frame 159: 0.0538 seconds
Queue size: 0
Time taken to process frame 143: 0.9920 seconds
Time taken to process frame 147: 0.2498 seconds
Time taken to process frame 159: 0.5837 seconds
Time taken to process frame 148: 0.6173 seconds
Time taken to process frame 160: 0.1130 seconds
Time taken to process frame 159: 0.3394 seconds
Queue size: 0
Time taken to process frame 141: 0.9919 seconds
Time taken to process frame 148: 0.1677 seconds
Time taken to process frame 149: 0.4154 seconds
Time taken to process frame 149: 0.2399 seconds
Queue size: 0
Time taken to process frame 138: 0.3381 seconds
Time taken to process frame 150: 0.5544 seconds
Time taken to process frame 144: 0.4419 seconds
Time taken to process frame 149: 0.2737 seconds
Time taken to process frame 139: 0.0705 seconds
Time taken to process frame 142: 0.3104 seconds
Time taken to process frame 160: 0.5415 seconds
Queue size: 0
Time taken to process frame 150: 0.3390 seconds
Time taken to process frame 161: 0.4854 seconds
Time taken to process frame 151: 0.1764 seconds
Time taken to process frame 140: 0.2151 seconds
Time taken to process frame 160: 0.6550 seconds
Queue size: 0
Time taken to process frame 152: 0.1130 seconds
Time taken to process frame 160: 0.8203 seconds
Time taken to process frame 162: 0.2742 seconds
Time taken to process frame 161: 0.3475 seconds
Time taken to process frame 150: 0.3848 seconds
Time taken to process frame 145: 0.4087 seconds
Time taken to process frame 143: 0.1983 seconds
Queue size: 0
Time taken to process frame 146: 0.0830 seconds
Time taken to process frame 147: 0.0441 seconds
Time taken to process frame 161: 0.2148 seconds
Time taken to process frame 148: 0.0477 seconds
Time taken to process frame 144: 0.1913 seconds
Queue size: 0
Time taken to process frame 151: 0.6193 seconds
Time taken to process frame 153: 0.4664 seconds
Time taken to process frame 145: 0.1150 seconds
Time taken to process frame 149: 0.1893 seconds
Time taken to process frame 161: 0.5473 seconds
Time taken to process frame 141: 0.5968 seconds
Time taken to process frame 154: 0.1026 seconds
Queue size: 0
Time taken to process frame 150: 1.1082 seconds
Time taken to process frame 142: 0.0951 seconds
Time taken to process frame 162: 0.4446 seconds
Time taken to process frame 162: 0.3853 seconds
Time taken to process frame 162: 0.1823 seconds
Time taken to process frame 152: 0.3481 seconds
Queue size: 0
Time taken to process frame 163: 0.5615 seconds
Time taken to process frame 151: 0.6849 seconds
Time taken to process frame 150: 0.3719 seconds
Time taken to process frame 153: 0.1408 seconds
Time taken to process frame 163: 0.2415 seconds
Time taken to process frame 163: 0.2255 seconds
Time taken to process frame 164: 0.1490 seconds
Time taken to process frame 155: 0.3872 seconds
Time taken to process frame 152: 0.1368 seconds
Time taken to process frame 163: 0.2520 seconds
Queue size: 1
Time taken to process frame 143: 0.3327 seconds
Time taken to process frame 151: 0.3722 seconds
Time taken to process frame 146: 0.5583 seconds
Time taken to process frame 164: 0.1429 seconds
Time taken to process frame 151: 0.1251 seconds
Time taken to process frame 164: 0.1523 seconds
Time taken to process frame 153: 0.1475 seconds
Time taken to process frame 154: 0.2337 seconds
Time taken to process frame 152: 0.0968 seconds
Queue size: 4
Time taken to process frame 164: 0.2447 seconds
Time taken to process frame 152: 0.1776 seconds
Time taken to process frame 165: 0.3398 seconds
Time taken to process frame 154: 0.2152 seconds
Queue size: 0
Time taken to process frame 147: 0.2698 seconds
Time taken to process frame 144: 0.3262 seconds
Time taken to process frame 165: 0.2355 seconds
Time taken to process frame 165: 0.3212 seconds
Time taken to process frame 156: 0.4759 seconds
Time taken to process frame 155: 0.3593 seconds
Time taken to process frame 148: 0.1846 seconds
Time taken to process frame 153: 0.2839 seconds
Time taken to process frame 153: 0.3728 seconds
Queue size: 2
Time taken to process frame 155: 0.2632 seconds
Time taken to process frame 166: 0.3232 seconds
Time taken to process frame 157: 0.1474 seconds
Time taken to process frame 166: 0.2066 seconds
Time taken to process frame 145: 0.2430 seconds
Time taken to process frame 166: 0.2323 seconds
Time taken to process frame 149: 0.0950 seconds
Time taken to process frame 156: 0.1691 seconds
Time taken to process frame 165: 0.4691 seconds
Time taken to process frame 156: 0.0900 seconds
Queue size: 0
Time taken to process frame 146: 0.0596 seconds
Time taken to process frame 158: 0.1414 seconds
Time taken to process frame 167: 0.1530 seconds
Time taken to process frame 167: 0.2027 seconds
Time taken to process frame 157: 0.2020 seconds
Time taken to process frame 150: 0.1713 seconds
Time taken to process frame 154: 0.1388 seconds
Queue size: 0
Time taken to process frame 168: 0.0618 seconds
Time taken to process frame 159: 0.1190 seconds
Time taken to process frame 154: 0.1415 seconds
Time taken to process frame 167: 0.2670 seconds
Time taken to process frame 168: 0.1520 seconds
Time taken to process frame 157: 0.2155 seconds
Time taken to process frame 166: 0.2640 seconds
Time taken to process frame 151: 0.1469 seconds
Time taken to process frame 158: 0.0878 seconds
Queue size: 0
Time taken to process frame 155: 0.1233 seconds
Time taken to process frame 169: 0.1656 seconds
Time taken to process frame 158: 0.1100 seconds
Time taken to process frame 168: 0.2302 seconds
Time taken to process frame 147: 0.1154 seconds
Time taken to process frame 155: 0.2897 seconds
Time taken to process frame 169: 0.1929 seconds
Time taken to process frame 160: 0.2169 seconds
Queue size: 0
Time taken to process frame 156: 0.1339 seconds
Time taken to process frame 152: 0.1689 seconds
Time taken to process frame 159: 0.2179 seconds
Time taken to process frame 170: 0.1585 seconds
Time taken to process frame 161: 0.0630 seconds
Time taken to process frame 153: 0.0425 seconds
Time taken to process frame 159: 0.1325 seconds
Time taken to process frame 148: 0.1075 seconds
Queue size: 0
Time taken to process frame 167: 0.0447 seconds
Time taken to process frame 156: 0.2078 seconds
Time taken to process frame 171: 0.0618 seconds
Time taken to process frame 169: 0.2092 seconds
Time taken to process frame 157: 0.1804 seconds
Time taken to process frame 170: 0.2211 seconds
Time taken to process frame 162: 0.1314 seconds
Time taken to process frame 154: 0.1170 seconds
Time taken to process frame 149: 0.0958 seconds
Queue size: 0
Time taken to process frame 160: 0.1748 seconds
Time taken to process frame 172: 0.1210 seconds
Time taken to process frame 160: 0.2769 seconds
Time taken to process frame 168: 0.1945 seconds
Time taken to process frame 158: 0.1056 seconds
Time taken to process frame 171: 0.1397 seconds
Time taken to process frame 157: 0.2554 seconds
Queue size: 0
Time taken to process frame 173: 0.0915 seconds
Time taken to process frame 163: 0.1731 seconds
Time taken to process frame 150: 0.2015 seconds
Time taken to process frame 170: 0.2873 seconds
Time taken to process frame 161: 0.1188 seconds
Time taken to process frame 159: 0.0901 seconds
Time taken to process frame 155: 0.2165 seconds
Time taken to process frame 161: 0.2134 seconds
Time taken to process frame 164: 0.1134 seconds
Time taken to process frame 172: 0.1546 seconds
Time taken to process frame 169: 0.2250 seconds
Queue size: 0
Time taken to process frame 162: 0.0354 seconds
Time taken to process frame 160: 0.1800 seconds
Time taken to process frame 174: 0.2783 seconds
Time taken to process frame 162: 0.2567 seconds
Time taken to process frame 171: 0.2307 seconds
Time taken to process frame 151: 0.2624 seconds
Queue size: 2
Time taken to process frame 158: 0.4077 seconds
Time taken to process frame 170: 0.2192 seconds
Time taken to process frame 163: 0.2170 seconds
Time taken to process frame 156: 0.3428 seconds
Time taken to process frame 165: 0.2705 seconds
Time taken to process frame 173: 0.3526 seconds
Queue size: 0
Time taken to process frame 161: 0.2640 seconds
Time taken to process frame 159: 0.1688 seconds
Time taken to process frame 164: 0.1512 seconds
Time taken to process frame 152: 0.2743 seconds
Time taken to process frame 172: 0.3223 seconds
Time taken to process frame 171: 0.2668 seconds
Time taken to process frame 157: 0.2110 seconds
Time taken to process frame 174: 0.2126 seconds
Time taken to process frame 175: 0.4476 seconds
Queue size: 2
Time taken to process frame 166: 0.2768 seconds
Time taken to process frame 163: 0.4693 seconds
Time taken to process frame 165: 0.1943 seconds
Time taken to process frame 162: 0.2673 seconds
Time taken to process frame 160: 0.2880 seconds
Time taken to process frame 173: 0.1987 seconds
Time taken to process frame 167: 0.1085 seconds
Queue size: 0
Time taken to process frame 153: 0.3018 seconds
Time taken to process frame 172: 0.2744 seconds
Time taken to process frame 164: 0.2083 seconds
Time taken to process frame 166: 0.2164 seconds
Time taken to process frame 158: 0.3064 seconds
Time taken to process frame 176: 0.2474 seconds
Time taken to process frame 168: 0.1083 seconds
Time taken to process frame 177: 0.0496 seconds
Time taken to process frame 163: 0.2618 seconds
Time taken to process frame 174: 0.2516 seconds
Queue size: 0
Time taken to process frame 175: 0.4273 seconds
Time taken to process frame 167: 0.1408 seconds
Time taken to process frame 173: 0.2234 seconds
Time taken to process frame 168: 0.0715 seconds
Time taken to process frame 169: 0.1896 seconds
Time taken to process frame 178: 0.1916 seconds
Time taken to process frame 154: 0.3509 seconds
Time taken to process frame 176: 0.1571 seconds
Time taken to process frame 165: 0.3261 seconds
Time taken to process frame 164: 0.2063 seconds
Time taken to process frame 161: 0.4965 seconds
Queue size: 5
Time taken to process frame 169: 0.1305 seconds
Time taken to process frame 174: 0.1932 seconds
Time taken to process frame 175: 0.3101 seconds
Time taken to process frame 159: 0.4125 seconds
Time taken to process frame 179: 0.2035 seconds
Time taken to process frame 166: 0.1459 seconds
Queue size: 0
Time taken to process frame 165: 0.1752 seconds
Time taken to process frame 177: 0.1764 seconds
Time taken to process frame 176: 0.0946 seconds
Time taken to process frame 162: 0.2404 seconds
Time taken to process frame 170: 0.3812 seconds
Time taken to process frame 180: 0.1808 seconds
Time taken to process frame 155: 0.4068 seconds
Queue size: 0
Time taken to process frame 178: 0.2010 seconds
Time taken to process frame 163: 0.1274 seconds
Time taken to process frame 166: 0.2474 seconds
Time taken to process frame 177: 0.2065 seconds
Time taken to process frame 167: 0.2709 seconds
Time taken to process frame 160: 0.3434 seconds
Time taken to process frame 181: 0.1836 seconds
Time taken to process frame 170: 0.4936 seconds
Time taken to process frame 164: 0.1204 seconds
Queue size: 0
Time taken to process frame 178: 0.1005 seconds
Time taken to process frame 175: 0.5178 seconds
Time taken to process frame 179: 0.1805 seconds
Time taken to process frame 161: 0.1239 seconds
Time taken to process frame 171: 0.3471 seconds
Time taken to process frame 171: 0.0948 seconds
Time taken to process frame 156: 0.3254 seconds
Time taken to process frame 182: 0.1793 seconds
Time taken to process frame 167: 0.2708 seconds
Queue size: 0
Time taken to process frame 179: 0.2115 seconds
Time taken to process frame 183: 0.0485 seconds
Time taken to process frame 168: 0.1821 seconds
Time taken to process frame 162: 0.2263 seconds
Time taken to process frame 168: 0.1057 seconds
Time taken to process frame 165: 0.3666 seconds
Time taken to process frame 180: 0.1306 seconds
Time taken to process frame 172: 0.2211 seconds
Time taken to process frame 157: 0.2014 seconds
Queue size: 0
Time taken to process frame 172: 0.2591 seconds
Time taken to process frame 176: 0.3821 seconds
Time taken to process frame 180: 0.3082 seconds
Time taken to process frame 158: 0.0675 seconds
Time taken to process frame 169: 0.1840 seconds
Time taken to process frame 173: 0.0630 seconds
Time taken to process frame 163: 0.1709 seconds
Time taken to process frame 184: 0.2454 seconds
Time taken to process frame 173: 0.0580 seconds
Time taken to process frame 166: 0.1665 seconds
Time taken to process frame 169: 0.2054 seconds
Queue size: 0Time taken to process frame 181: 0.1440 seconds

Time taken to process frame 181: 0.1261 seconds
Time taken to process frame 159: 0.1452 seconds
Time taken to process frame 174: 0.1476 seconds
Time taken to process frame 170: 0.2402 seconds
Time taken to process frame 174: 0.1878 seconds
Time taken to process frame 170: 0.2128 seconds
Time taken to process frame 164: 0.1611 seconds
Queue size: 3
Time taken to process frame 167: 0.0875 seconds
Time taken to process frame 177: 0.1697 seconds
Time taken to process frame 185: 0.1627 seconds
Time taken to process frame 182: 0.1376 seconds
Time taken to process frame 171: 0.0817 seconds
Time taken to process frame 182: 0.2264 seconds
Time taken to process frame 171: 0.0771 seconds
Time taken to process frame 186: 0.0599 seconds
Time taken to process frame 175: 0.1727 seconds
Time taken to process frame 175: 0.1532 seconds
Time taken to process frame 168: 0.1239 seconds
Queue size: 1
Time taken to process frame 183: 0.0783 seconds
Time taken to process frame 160: 0.2954 seconds
Time taken to process frame 165: 0.2258 seconds
Time taken to process frame 172: 0.1427 seconds
Time taken to process frame 183: 0.1681 seconds
Time taken to process frame 176: 0.1471 seconds
Time taken to process frame 187: 0.1559 seconds
Time taken to process frame 172: 0.1385 seconds
Time taken to process frame 178: 0.1195 seconds
Queue size: 0
Time taken to process frame 169: 0.1291 seconds
Time taken to process frame 161: 0.0475 seconds
Time taken to process frame 176: 0.1135 seconds
Time taken to process frame 184: 0.1297 seconds
Time taken to process frame 166: 0.1160 seconds
Time taken to process frame 177: 0.0534 seconds
Time taken to process frame 173: 0.1100 seconds
Time taken to process frame 188: 0.0458 seconds
Time taken to process frame 173: 0.0365 seconds
Time taken to process frame 184: 0.0870 seconds
Time taken to process frame 179: 0.0770 seconds
Queue size: 0
Time taken to process frame 170: 0.0939 seconds
Time taken to process frame 162: 0.1009 seconds
Time taken to process frame 177: 0.1242 seconds
Time taken to process frame 185: 0.1177 seconds
Time taken to process frame 178: 0.1239 seconds
Time taken to process frame 189: 0.1209 seconds
Time taken to process frame 174: 0.1241 seconds
Time taken to process frame 174: 0.1146 seconds
Queue size: 0
Time taken to process frame 171: 0.0400 seconds
Time taken to process frame 167: 0.0901 seconds
Time taken to process frame 180: 0.0871 seconds
Time taken to process frame 186: 0.0310 seconds
Time taken to process frame 163: 0.0615 seconds
Time taken to process frame 185: 0.1707 seconds
Time taken to process frame 178: 0.0370 seconds
Time taken to process frame 179: 0.0991 seconds
Time taken to process frame 168: 0.0420 seconds
Time taken to process frame 190: 0.1378 seconds
Queue size: 1
Time taken to process frame 172: 0.1213 seconds
Time taken to process frame 175: 0.1058 seconds
Time taken to process frame 175: 0.1498 seconds
Time taken to process frame 181: 0.1065 seconds
Time taken to process frame 164: 0.1156 seconds
Time taken to process frame 186: 0.1050 seconds
Time taken to process frame 187: 0.1352 seconds
Time taken to process frame 173: 0.0310 seconds
Queue size: 0
Time taken to process frame 191: 0.0734 seconds
Time taken to process frame 176: 0.0557 seconds
Time taken to process frame 169: 0.1473 seconds
Time taken to process frame 179: 0.2019 seconds
Time taken to process frame 188: 0.0470 seconds
Time taken to process frame 182: 0.1067 seconds
Time taken to process frame 180: 0.1949 seconds
Time taken to process frame 176: 0.0418 seconds
Time taken to process frame 187: 0.1610 seconds
Queue size: 0
Time taken to process frame 174: 0.1336 seconds
Time taken to process frame 165: 0.2166 seconds
Time taken to process frame 192: 0.1120 seconds
Time taken to process frame 177: 0.1461 seconds
Time taken to process frame 181: 0.1303 seconds
Time taken to process frame 189: 0.1731 seconds
Time taken to process frame 177: 0.1403 seconds
Time taken to process frame 170: 0.2148 seconds
Queue size: 2
Time taken to process frame 180: 0.2796 seconds
Time taken to process frame 166: 0.1054 seconds
Time taken to process frame 188: 0.1990 seconds
Time taken to process frame 193: 0.2076 seconds
Time taken to process frame 182: 0.1323 seconds
Time taken to process frame 183: 0.2855 seconds
Queue size: 0
Time taken to process frame 178: 0.2441 seconds
Time taken to process frame 181: 0.1736 seconds
Time taken to process frame 178: 0.2081 seconds
Time taken to process frame 171: 0.2207 seconds
Time taken to process frame 194: 0.1582 seconds
Time taken to process frame 183: 0.1771 seconds
Time taken to process frame 189: 0.2410 seconds
Time taken to process frame 179: 0.1121 seconds
Time taken to process frame 179: 0.0844 seconds
Time taken to process frame 175: 0.4217 seconds
Time taken to process frame 182: 0.1127 seconds
Queue size: 0
Time taken to process frame 195: 0.1186 seconds
Time taken to process frame 184: 0.2719 seconds
Time taken to process frame 172: 0.1576 seconds
Time taken to process frame 167: 0.3910 seconds
Time taken to process frame 190: 0.5113 seconds
Time taken to process frame 173: 0.0801 seconds
Time taken to process frame 183: 0.1546 seconds
Queue size: 4
Time taken to process frame 196: 0.1596 seconds
Time taken to process frame 190: 0.2474 seconds
Time taken to process frame 184: 0.2803 seconds
Time taken to process frame 185: 0.2039 seconds
Time taken to process frame 174: 0.1009 seconds
Time taken to process frame 191: 0.1535 seconds
Time taken to process frame 197: 0.0775 seconds
Time taken to process frame 168: 0.2466 seconds
Queue size: 0
Time taken to process frame 176: 0.3775 seconds
Time taken to process frame 198: 0.0760 seconds
Time taken to process frame 180: 0.3255 seconds
Time taken to process frame 184: 0.2319 seconds
Time taken to process frame 175: 0.1280 seconds
Time taken to process frame 186: 0.1675 seconds
Time taken to process frame 192: 0.1563 seconds
Time taken to process frame 181: 0.0643 seconds
Time taken to process frame 199: 0.1303 seconds
Queue size: 0
Time taken to process frame 187: 0.0490 seconds
Time taken to process frame 169: 0.2743 seconds
Time taken to process frame 191: 0.3957 seconds
Time taken to process frame 180: 0.4755 seconds
Time taken to process frame 188: 0.0837 seconds
Time taken to process frame 185: 0.4527 seconds
Time taken to process frame 182: 0.1738 seconds
Queue size: 0
Time taken to process frame 185: 0.3840 seconds
Time taken to process frame 200: 0.2481 seconds
Time taken to process frame 176: 0.3162 seconds
Time taken to process frame 192: 0.1833 seconds
Time taken to process frame 189: 0.1920 seconds
Time taken to process frame 170: 0.2823 seconds
Time taken to process frame 193: 0.3721 seconds
Queue size: 0
Time taken to process frame 183: 0.2337 seconds
Time taken to process frame 177: 0.1717 seconds
Time taken to process frame 190: 0.1252 seconds
Time taken to process frame 181: 0.3870 seconds
Time taken to process frame 194: 0.1442 seconds
Time taken to process frame 171: 0.1722 seconds
Time taken to process frame 186: 0.3888 seconds
Time taken to process frame 201: 0.2845 seconds
Time taken to process frame 177: 0.3516 seconds
Time taken to process frame 184: 0.1613 seconds
Time taken to process frame 193: 0.2510 seconds
Time taken to process frame 178: 0.1135 seconds
Queue size: 0
Time taken to process frame 182: 0.1490 seconds
Time taken to process frame 191: 0.1842 seconds
Time taken to process frame 186: 0.4525 seconds
Time taken to process frame 187: 0.1380 seconds
Time taken to process frame 172: 0.1692 seconds
Time taken to process frame 202: 0.1525 seconds
Time taken to process frame 195: 0.2571 seconds
Queue size: 0
Time taken to process frame 178: 0.2068 seconds
Time taken to process frame 185: 0.1773 seconds
Time taken to process frame 192: 0.0988 seconds
Time taken to process frame 187: 0.1842 seconds
Time taken to process frame 194: 0.2869 seconds
Time taken to process frame 203: 0.1461 seconds
Queue size: 0
Time taken to process frame 188: 0.2531 seconds
Time taken to process frame 173: 0.3008 seconds
Time taken to process frame 183: 0.3302 seconds
Time taken to process frame 179: 0.2373 seconds
Time taken to process frame 188: 0.1710 seconds
Time taken to process frame 196: 0.3328 seconds
Queue size: 0
Time taken to process frame 189: 0.1833 seconds
Time taken to process frame 179: 0.4025 seconds
Time taken to process frame 193: 0.2878 seconds
Time taken to process frame 184: 0.2023 seconds
Time taken to process frame 195: 0.2822 seconds
Time taken to process frame 189: 0.1319 seconds
Time taken to process frame 174: 0.2228 seconds
Time taken to process frame 186: 0.3617 seconds
Time taken to process frame 204: 0.3393 seconds
Time taken to process frame 197: 0.2099 seconds
Time taken to process frame 180: 0.3036 seconds
Queue size: 0
Time taken to process frame 187: 0.1402 seconds
Time taken to process frame 196: 0.2614 seconds
Time taken to process frame 188: 0.0668 seconds
Time taken to process frame 185: 0.3442 seconds
Time taken to process frame 194: 0.2713 seconds
Time taken to process frame 180: 0.3727 seconds
Queue size: 0Time taken to process frame 198: 0.2252 seconds

Time taken to process frame 190: 0.4405 seconds
Time taken to process frame 189: 0.0958 seconds
Time taken to process frame 175: 0.4198 seconds
Time taken to process frame 197: 0.2236 seconds
Time taken to process frame 181: 0.3894 seconds
Time taken to process frame 199: 0.1505 seconds
Time taken to process frame 186: 0.2090 seconds
Queue size: 0
Time taken to process frame 176: 0.0816 seconds
Time taken to process frame 190: 0.5533 secondsTime taken to process frame 195: 0.2088 seconds

Time taken to process frame 205: 0.5173 seconds
Time taken to process frame 198: 0.1521 seconds
Time taken to process frame 191: 0.0786 seconds
Time taken to process frame 181: 0.3135 seconds
Time taken to process frame 182: 0.1771 seconds
Time taken to process frame 177: 0.1725 seconds
Queue size: 0
Time taken to process frame 187: 0.1696 seconds
Time taken to process frame 190: 0.3612 seconds
Time taken to process frame 191: 0.3893 seconds
Time taken to process frame 206: 0.1880 seconds
Time taken to process frame 196: 0.2239 seconds
Time taken to process frame 199: 0.1997 seconds
Time taken to process frame 178: 0.1336 seconds
Time taken to process frame 182: 0.1976 seconds
Time taken to process frame 183: 0.1918 seconds
Time taken to process frame 192: 0.2519 seconds
Queue size: 0
Time taken to process frame 191: 0.1877 seconds
Time taken to process frame 200: 0.3693 seconds
Time taken to process frame 192: 0.2076 seconds
Time taken to process frame 207: 0.1928 seconds
Time taken to process frame 188: 0.2930 seconds
Time taken to process frame 197: 0.1664 seconds
Time taken to process frame 193: 0.0672 seconds
Queue size: 0
Time taken to process frame 184: 0.1964 seconds
Time taken to process frame 192: 0.1697 seconds
Time taken to process frame 183: 0.2584 seconds
Time taken to process frame 193: 0.2359 seconds
Time taken to process frame 179: 0.2723 seconds
Time taken to process frame 200: 0.3534 seconds
Time taken to process frame 208: 0.0566 seconds
Time taken to process frame 201: 0.1472 seconds
Time taken to process frame 194: 0.1515 seconds
Time taken to process frame 194: 0.1236 seconds
Queue size: 0
Time taken to process frame 193: 0.1251 seconds
Time taken to process frame 184: 0.1448 seconds
Time taken to process frame 185: 0.2721 seconds
Time taken to process frame 189: 0.2051 seconds
Time taken to process frame 198: 0.1830 seconds
Time taken to process frame 202: 0.1540 seconds
Queue size: 2
Time taken to process frame 186: 0.0850 seconds
Time taken to process frame 209: 0.2552 seconds
Time taken to process frame 180: 0.3089 seconds
Time taken to process frame 194: 0.1582 seconds
Time taken to process frame 201: 0.3344 seconds
Time taken to process frame 185: 0.1901 seconds
Time taken to process frame 203: 0.1150 seconds
Queue size: 0
Time taken to process frame 187: 0.1534 seconds
Time taken to process frame 195: 0.3268 seconds
Time taken to process frame 181: 0.1199 seconds
Time taken to process frame 186: 0.1267 seconds
Time taken to process frame 188: 0.1067 seconds
Time taken to process frame 195: 0.4611 seconds
Time taken to process frame 202: 0.2195 seconds
Time taken to process frame 195: 0.2565 seconds
Time taken to process frame 204: 0.2115 seconds
Time taken to process frame 199: 0.3630 seconds
Time taken to process frame 182: 0.1344 seconds
Queue size: 0
Time taken to process frame 196: 0.1851 seconds
Time taken to process frame 210: 0.3595 seconds
Time taken to process frame 203: 0.0818 seconds
Time taken to process frame 187: 0.1904 seconds
Time taken to process frame 211: 0.0680 seconds
Time taken to process frame 189: 0.2609 seconds
Queue size: 0
Time taken to process frame 196: 0.2458 seconds
Time taken to process frame 197: 0.1416 seconds
Time taken to process frame 190: 0.6466 seconds
Time taken to process frame 204: 0.1046 seconds
Time taken to process frame 196: 0.1855 seconds
Time taken to process frame 183: 0.2632 seconds
Time taken to process frame 191: 0.0654 seconds
Time taken to process frame 200: 0.3940 seconds
Time taken to process frame 184: 0.0726 seconds
Queue size: 0
Time taken to process frame 205: 0.2000 seconds
Time taken to process frame 197: 0.2440 seconds
Time taken to process frame 212: 0.2935 seconds
Time taken to process frame 198: 0.0340 seconds
Time taken to process frame 206: 0.0670 seconds
Time taken to process frame 213: 0.0360 seconds
Time taken to process frame 188: 0.3915 seconds
Queue size: 0
Time taken to process frame 201: 0.2241 seconds
Time taken to process frame 198: 0.4280 seconds
Time taken to process frame 190: 0.4776 seconds
Time taken to process frame 214: 0.1536 seconds
Time taken to process frame 205: 0.7462 seconds
Time taken to process frame 202: 0.1645 seconds
Time taken to process frame 189: 0.2185 seconds
Time taken to process frame 199: 0.1409 seconds
Queue size: 0
Time taken to process frame 192: 0.4015 seconds
Time taken to process frame 197: 0.4635 seconds
Time taken to process frame 185: 0.4567 seconds
Time taken to process frame 207: 0.3793 seconds
Time taken to process frame 199: 0.3993 seconds
Time taken to process frame 190: 0.1274 seconds
Time taken to process frame 206: 0.1929 seconds
Time taken to process frame 198: 0.1155 seconds
Time taken to process frame 191: 0.3088 seconds
Time taken to process frame 215: 0.2947 seconds
Time taken to process frame 203: 0.0290 seconds
Queue size: 5
Time taken to process frame 193: 0.2067 seconds
Time taken to process frame 186: 0.2397 seconds
Time taken to process frame 192: 0.1259 seconds
Time taken to process frame 200: 0.3376 seconds
Time taken to process frame 191: 0.1847 seconds
Time taken to process frame 208: 0.0540 seconds
Queue size: 2
Time taken to process frame 193: 0.0865 seconds
Time taken to process frame 204: 0.2141 seconds
Time taken to process frame 209: 0.1146 seconds
Time taken to process frame 194: 0.2574 seconds
Time taken to process frame 216: 0.3292 seconds
Time taken to process frame 201: 0.1998 seconds
Queue size: 0
Time taken to process frame 192: 0.2504 seconds
Time taken to process frame 199: 0.1629 seconds
Time taken to process frame 207: 0.4852 seconds
Time taken to process frame 217: 0.1022 seconds
Time taken to process frame 194: 0.2445 seconds
Time taken to process frame 187: 0.4132 seconds
Time taken to process frame 200: 0.2833 seconds
Queue size: 0
Time taken to process frame 210: 0.2939 seconds
Time taken to process frame 195: 0.2093 seconds
Time taken to process frame 208: 0.1597 seconds
Time taken to process frame 202: 0.2869 seconds
Time taken to process frame 201: 0.0653 seconds
Time taken to process frame 188: 0.1750 seconds
Time taken to process frame 205: 0.4203 seconds
Time taken to process frame 193: 0.2801 seconds
Time taken to process frame 196: 0.0763 seconds
Time taken to process frame 218: 0.1519 seconds
Time taken to process frame 203: 0.0360 seconds
Time taken to process frame 209: 0.1130 seconds
Queue size: 0
Time taken to process frame 211: 0.2108 seconds
Time taken to process frame 195: 0.3334 seconds
Time taken to process frame 202: 0.1669 seconds
Time taken to process frame 219: 0.1712 seconds
Time taken to process frame 189: 0.2529 seconds
Time taken to process frame 196: 0.0475 seconds
Time taken to process frame 206: 0.1896 seconds
Time taken to process frame 204: 0.2235 seconds
Time taken to process frame 200: 0.5406 seconds
Queue size: 2
Time taken to process frame 210: 0.1681 seconds
Time taken to process frame 194: 0.1771 seconds
Time taken to process frame 212: 0.2251 seconds
Time taken to process frame 197: 0.3139 seconds
Time taken to process frame 220: 0.1669 seconds
Queue size: 0
Time taken to process frame 213: 0.0958 seconds
Time taken to process frame 203: 0.3040 seconds
Time taken to process frame 207: 0.2476 seconds
Time taken to process frame 204: 0.0305 seconds
Time taken to process frame 221: 0.1721 seconds
Time taken to process frame 201: 0.2604 seconds
Time taken to process frame 211: 0.3189 seconds
Time taken to process frame 214: 0.1768 seconds
Queue size: 0
Time taken to process frame 195: 0.3390 seconds
Time taken to process frame 205: 0.4116 seconds
Time taken to process frame 212: 0.0742 seconds
Time taken to process frame 197: 0.4991 seconds
Time taken to process frame 222: 0.1662 seconds
Time taken to process frame 190: 0.5487 seconds
Time taken to process frame 202: 0.1678 seconds
Time taken to process frame 198: 0.4048 seconds
Time taken to process frame 208: 0.3095 seconds
Time taken to process frame 205: 0.2537 seconds
Queue size: 0
Time taken to process frame 206: 0.1686 seconds
Time taken to process frame 213: 0.1522 seconds
Time taken to process frame 199: 0.0440 seconds
Time taken to process frame 191: 0.1500 seconds
Time taken to process frame 203: 0.1766 seconds
Time taken to process frame 198: 0.2712 seconds
Time taken to process frame 196: 0.3437 seconds
Queue size: 0
Time taken to process frame 206: 0.2192 seconds
Time taken to process frame 215: 0.4268 seconds
Time taken to process frame 207: 0.1964 seconds
Time taken to process frame 223: 0.1790 seconds
Time taken to process frame 200: 0.1536 seconds
Time taken to process frame 209: 0.2877 seconds
Time taken to process frame 214: 0.2262 seconds
Time taken to process frame 204: 0.2002 seconds
Time taken to process frame 224: 0.0981 seconds
Time taken to process frame 199: 0.1825 seconds
Queue size: 0
Time taken to process frame 197: 0.2336 seconds
Time taken to process frame 207: 0.1661 seconds
Time taken to process frame 216: 0.2131 seconds
Time taken to process frame 192: 0.3217 seconds
Time taken to process frame 208: 0.2211 seconds
Time taken to process frame 225: 0.1065 seconds
Time taken to process frame 201: 0.2357 seconds
Time taken to process frame 210: 0.2157 seconds
Time taken to process frame 215: 0.1955 seconds
Time taken to process frame 208: 0.1151 seconds
Queue size: 0
Time taken to process frame 217: 0.1875 seconds
Time taken to process frame 209: 0.0302 seconds
Time taken to process frame 205: 0.3219 seconds
Time taken to process frame 193: 0.1960 seconds
Queue size: 0
Time taken to process frame 216: 0.2409 seconds
Time taken to process frame 200: 0.4073 seconds
Time taken to process frame 217: 0.0391 seconds
Time taken to process frame 202: 0.2129 seconds
Time taken to process frame 210: 0.1973 seconds
Time taken to process frame 218: 0.2534 seconds
Time taken to process frame 211: 0.0259 seconds
Time taken to process frame 226: 0.3921 seconds
Time taken to process frame 218: 0.0992 seconds
Time taken to process frame 211: 0.3683 seconds
Time taken to process frame 198: 0.2290 seconds
Time taken to process frame 203: 0.1192 seconds
Queue size: 1
Time taken to process frame 209: 0.4529 seconds
Time taken to process frame 206: 0.3575 seconds
Time taken to process frame 194: 0.3233 seconds
Time taken to process frame 199: 0.1324 seconds
Time taken to process frame 227: 0.2180 seconds
Time taken to process frame 219: 0.2227 seconds
Queue size: 0
Time taken to process frame 201: 0.4052 seconds
Time taken to process frame 212: 0.2822 seconds
Time taken to process frame 207: 0.2050 seconds
Time taken to process frame 219: 0.3626 seconds
Time taken to process frame 204: 0.2970 seconds
Time taken to process frame 210: 0.3080 seconds
Time taken to process frame 202: 0.1525 seconds
Queue size: 0
Time taken to process frame 228: 0.2335 seconds
Time taken to process frame 212: 0.2802 seconds
Time taken to process frame 200: 0.3344 seconds
Time taken to process frame 195: 0.4020 seconds
Time taken to process frame 229: 0.1061 seconds
Time taken to process frame 213: 0.0964 seconds
Time taken to process frame 213: 0.3146 seconds
Queue size: 2Time taken to process frame 203: 0.2182 seconds

Time taken to process frame 220: 0.4293 seconds
Time taken to process frame 208: 0.3396 seconds
Time taken to process frame 211: 0.3173 seconds
Time taken to process frame 201: 0.2079 seconds
Time taken to process frame 220: 0.4009 seconds
Time taken to process frame 205: 0.3696 seconds
Time taken to process frame 204: 0.1003 seconds
Time taken to process frame 230: 0.2080 seconds
Time taken to process frame 214: 0.1891 seconds
Time taken to process frame 214: 0.1599 seconds
Time taken to process frame 196: 0.2469 seconds
Queue size: 0
Time taken to process frame 221: 0.1556 seconds
Time taken to process frame 221: 0.1547 seconds
Time taken to process frame 206: 0.1560 seconds
Time taken to process frame 209: 0.2538 seconds
Time taken to process frame 212: 0.2458 seconds
Time taken to process frame 202: 0.2346 seconds
Queue size: 0Time taken to process frame 231: 0.1792 seconds
Time taken to process frame 197: 0.0574 seconds

Time taken to process frame 215: 0.2327 seconds
Time taken to process frame 215: 0.2787 seconds
Time taken to process frame 205: 0.3075 seconds
Time taken to process frame 222: 0.2608 seconds
Time taken to process frame 222: 0.2244 seconds
Time taken to process frame 207: 0.2114 seconds
Time taken to process frame 203: 0.2071 seconds
Time taken to process frame 210: 0.2391 seconds
Time taken to process frame 213: 0.1347 seconds
Queue size: 0
Time taken to process frame 216: 0.1099 seconds
Time taken to process frame 232: 0.2394 seconds
Time taken to process frame 216: 0.1952 seconds
Time taken to process frame 198: 0.2738 seconds
Time taken to process frame 214: 0.1838 seconds
Time taken to process frame 217: 0.0902 seconds
Time taken to process frame 217: 0.1412 seconds
Queue size: 0
Time taken to process frame 223: 0.3123 seconds
Time taken to process frame 206: 0.3047 seconds
Time taken to process frame 204: 0.2545 seconds
Time taken to process frame 224: 0.0562 seconds
Time taken to process frame 208: 0.3592 seconds
Time taken to process frame 223: 0.3664 seconds
Time taken to process frame 209: 0.0298 seconds
Time taken to process frame 218: 0.1900 seconds
Time taken to process frame 218: 0.1916 seconds
Time taken to process frame 211: 0.3884 seconds
Queue size: 3
Time taken to process frame 219: 0.0579 seconds
Time taken to process frame 199: 0.3083 seconds
Time taken to process frame 233: 0.4154 seconds
Time taken to process frame 207: 0.2188 seconds
Time taken to process frame 219: 0.0772 seconds
Time taken to process frame 225: 0.2508 seconds
Time taken to process frame 224: 0.2355 seconds
Time taken to process frame 234: 0.1047 seconds
Time taken to process frame 205: 0.3488 seconds
Queue size: 4
Time taken to process frame 215: 0.4697 seconds
Time taken to process frame 212: 0.1220 seconds
Time taken to process frame 210: 0.3529 seconds
Time taken to process frame 220: 0.2575 seconds
Time taken to process frame 220: 0.2234 seconds
Time taken to process frame 213: 0.1129 seconds
Queue size: 0
Time taken to process frame 206: 0.1792 seconds
Time taken to process frame 208: 0.3844 seconds
Time taken to process frame 216: 0.1954 seconds
Time taken to process frame 200: 0.3262 seconds
Time taken to process frame 225: 0.2731 seconds
Time taken to process frame 235: 0.2583 seconds
Time taken to process frame 217: 0.0739 seconds
Time taken to process frame 226: 0.4308 seconds
Queue size: 0
Time taken to process frame 209: 0.0567 seconds
Time taken to process frame 211: 0.2119 seconds
Time taken to process frame 214: 0.0287 seconds
Time taken to process frame 218: 0.1714 seconds
Time taken to process frame 207: 0.2883 seconds
Queue size: 0
Time taken to process frame 201: 0.2657 seconds
Time taken to process frame 210: 0.2477 seconds
Time taken to process frame 221: 0.3726 seconds
Time taken to process frame 208: 0.1011 seconds
Time taken to process frame 227: 0.2850 seconds
Time taken to process frame 219: 0.1594 seconds
Time taken to process frame 215: 0.2429 seconds
Time taken to process frame 226: 0.3883 seconds
Time taken to process frame 202: 0.1454 seconds
Time taken to process frame 212: 0.3344 seconds
Queue size: 0
Time taken to process frame 221: 0.5492 seconds
Time taken to process frame 236: 0.3665 seconds
Time taken to process frame 216: 0.1611 seconds
Time taken to process frame 211: 0.2720 seconds
Time taken to process frame 227: 0.1741 seconds
Time taken to process frame 203: 0.1914 seconds
Time taken to process frame 228: 0.2858 seconds
Time taken to process frame 209: 0.2870 seconds
Queue size: 0
Time taken to process frame 237: 0.1289 seconds
Time taken to process frame 222: 0.3574 seconds
Time taken to process frame 213: 0.2534 seconds
Time taken to process frame 212: 0.1346 seconds
Time taken to process frame 217: 0.1763 seconds
Time taken to process frame 220: 0.3529 seconds
Time taken to process frame 222: 0.2693 seconds
Time taken to process frame 228: 0.1601 seconds
Time taken to process frame 204: 0.1901 seconds
Time taken to process frame 238: 0.1546 seconds
Time taken to process frame 214: 0.1451 seconds
Queue size: 0
Time taken to process frame 213: 0.1475 seconds
Time taken to process frame 221: 0.1236 seconds
Time taken to process frame 229: 0.2718 seconds
Time taken to process frame 218: 0.1731 seconds
Time taken to process frame 229: 0.1107 seconds
Time taken to process frame 205: 0.1360 seconds
Time taken to process frame 223: 0.2411 seconds
Time taken to process frame 239: 0.1925 seconds
Queue size: 0
Time taken to process frame 223: 0.1722 seconds
Time taken to process frame 230: 0.1172 seconds
Time taken to process frame 219: 0.1519 seconds
Time taken to process frame 206: 0.1214 seconds
Time taken to process frame 214: 0.3335 seconds
Time taken to process frame 224: 0.1657 seconds
Time taken to process frame 230: 0.2811 seconds
Queue size: 0
Time taken to process frame 210: 0.3634 seconds
Time taken to process frame 207: 0.1357 seconds
Time taken to process frame 231: 0.1694 seconds
Time taken to process frame 222: 0.3486 seconds
Time taken to process frame 240: 0.2214 seconds
Time taken to process frame 224: 0.2661 seconds
Time taken to process frame 232: 0.0265 seconds
Time taken to process frame 215: 0.5113 seconds
Time taken to process frame 231: 0.1126 seconds
Time taken to process frame 220: 0.3202 seconds
Queue size: 0
Time taken to process frame 208: 0.2179 seconds
Time taken to process frame 225: 0.2512 seconds
Time taken to process frame 225: 0.1662 seconds
Time taken to process frame 241: 0.2146 seconds
Time taken to process frame 232: 0.1782 seconds
Time taken to process frame 223: 0.1461 seconds
Time taken to process frame 233: 0.2233 seconds
Time taken to process frame 211: 0.3107 seconds
Time taken to process frame 216: 0.1537 seconds
Time taken to process frame 215: 0.4044 seconds
Time taken to process frame 209: 0.0904 seconds
Queue size: 3
Time taken to process frame 221: 0.2026 seconds
Time taken to process frame 242: 0.0661 seconds
Time taken to process frame 233: 0.2156 seconds
Time taken to process frame 234: 0.1854 seconds
Time taken to process frame 243: 0.0706 seconds
Queue size: 1
Time taken to process frame 226: 0.1778 seconds
Time taken to process frame 222: 0.1091 seconds
Time taken to process frame 224: 0.2440 seconds
Time taken to process frame 212: 0.2358 seconds
Time taken to process frame 227: 0.0276 seconds
Time taken to process frame 244: 0.1071 seconds
Time taken to process frame 223: 0.1037 seconds
Time taken to process frame 217: 0.3225 seconds
Time taken to process frame 210: 0.2869 seconds
Time taken to process frame 226: 0.4275 seconds
Time taken to process frame 216: 0.3191 seconds
Time taken to process frame 234: 0.2512 seconds
Time taken to process frame 228: 0.1190 seconds
Queue size: 1
Time taken to process frame 217: 0.0383 seconds
Time taken to process frame 213: 0.2321 seconds
Time taken to process frame 227: 0.1096 seconds
Time taken to process frame 224: 0.1765 seconds
Time taken to process frame 229: 0.0819 seconds
Time taken to process frame 218: 0.0768 seconds
Time taken to process frame 225: 0.3324 seconds
Time taken to process frame 235: 0.4596 seconds
Queue size: 2
Time taken to process frame 245: 0.3363 seconds
Time taken to process frame 214: 0.1549 seconds
Time taken to process frame 225: 0.1491 seconds
Time taken to process frame 219: 0.1343 seconds
Time taken to process frame 218: 0.4129 seconds
Time taken to process frame 226: 0.1653 seconds
Time taken to process frame 228: 0.2450 seconds
Time taken to process frame 211: 0.3414 seconds
Time taken to process frame 235: 0.3664 seconds
Queue size: 0
Time taken to process frame 230: 0.2791 seconds
Time taken to process frame 212: 0.0447 seconds
Time taken to process frame 215: 0.1892 seconds
Time taken to process frame 236: 0.3520 seconds
Time taken to process frame 220: 0.2492 seconds
Time taken to process frame 229: 0.1966 seconds
Time taken to process frame 226: 0.2852 seconds
Time taken to process frame 219: 0.2489 seconds
Time taken to process frame 246: 0.3711 seconds
Queue size: 4
Time taken to process frame 213: 0.1607 seconds
Time taken to process frame 237: 0.1016 seconds
Time taken to process frame 227: 0.2551 seconds
Time taken to process frame 227: 0.0919 seconds
Time taken to process frame 236: 0.2972 seconds
Time taken to process frame 230: 0.1499 seconds
Time taken to process frame 247: 0.1234 seconds
Time taken to process frame 231: 0.3018 seconds
Time taken to process frame 228: 0.0745 seconds
Time taken to process frame 216: 0.3054 seconds
Queue size: 3
Time taken to process frame 221: 0.1535 seconds
Time taken to process frame 214: 0.2302 seconds
Time taken to process frame 232: 0.1215 seconds
Time taken to process frame 228: 0.1714 seconds
Time taken to process frame 231: 0.1772 seconds
Time taken to process frame 238: 0.2450 seconds
Time taken to process frame 237: 0.2113 seconds
Queue size: 0
Time taken to process frame 248: 0.2712 seconds
Time taken to process frame 229: 0.2051 seconds
Time taken to process frame 215: 0.1731 seconds
Time taken to process frame 222: 0.2013 seconds
Time taken to process frame 217: 0.2998 seconds
Time taken to process frame 229: 0.1923 seconds
Time taken to process frame 220: 0.5062 seconds
Time taken to process frame 233: 0.2053 seconds
Queue size: 0
Time taken to process frame 239: 0.1663 seconds
Time taken to process frame 249: 0.1489 seconds
Time taken to process frame 238: 0.2693 seconds
Time taken to process frame 216: 0.1730 seconds
Time taken to process frame 218: 0.2456 seconds
Time taken to process frame 230: 0.1970 seconds
Queue size: 0
Time taken to process frame 232: 0.2300 seconds
Time taken to process frame 250: 0.1650 seconds
Time taken to process frame 221: 0.2795 seconds
Time taken to process frame 239: 0.1740 seconds
Time taken to process frame 234: 0.2274 seconds
Time taken to process frame 230: 0.4495 seconds
Time taken to process frame 217: 0.1897 seconds
Time taken to process frame 219: 0.1737 seconds
Time taken to process frame 222: 0.1099 seconds
Time taken to process frame 231: 0.0505 seconds
Queue size: 0
Time taken to process frame 233: 0.1801 seconds
Time taken to process frame 251: 0.1874 seconds
Time taken to process frame 223: 0.4087 seconds
Time taken to process frame 218: 0.1308 seconds
Time taken to process frame 240: 0.2258 seconds
Time taken to process frame 231: 0.4015 seconds
Queue size: 3
Time taken to process frame 234: 0.1776 seconds
Time taken to process frame 252: 0.1763 seconds
Time taken to process frame 235: 0.3669 seconds
Time taken to process frame 240: 0.2367 seconds
Time taken to process frame 232: 0.1483 seconds
Time taken to process frame 224: 0.2063 seconds
Time taken to process frame 220: 0.3793 seconds
Time taken to process frame 232: 0.0976 seconds
Time taken to process frame 223: 0.1458 seconds
Time taken to process frame 219: 0.1723 seconds
Queue size: 0
Time taken to process frame 253: 0.0379 seconds
Time taken to process frame 236: 0.0945 seconds
Time taken to process frame 241: 0.2504 seconds
Time taken to process frame 241: 0.1620 seconds
Time taken to process frame 235: 0.2362 seconds
Time taken to process frame 225: 0.1463 seconds
Time taken to process frame 224: 0.0334 seconds
Time taken to process frame 233: 0.1447 seconds
Queue size: 0
Time taken to process frame 221: 0.1355 seconds
Time taken to process frame 233: 0.1195 seconds
Time taken to process frame 254: 0.0994 seconds
Time taken to process frame 237: 0.1086 seconds
Time taken to process frame 220: 0.1570 seconds
Time taken to process frame 242: 0.0954 seconds
Time taken to process frame 236: 0.0449 seconds
Time taken to process frame 242: 0.1037 seconds
Time taken to process frame 226: 0.0348 seconds
Queue size: 1
Time taken to process frame 234: 0.0898 seconds
Time taken to process frame 225: 0.0802 seconds
Time taken to process frame 234: 0.0507 seconds
Time taken to process frame 222: 0.0774 seconds
Time taken to process frame 237: 0.0972 seconds
Time taken to process frame 243: 0.0432 seconds
Queue size: 1
Time taken to process frame 243: 0.0623 seconds
Time taken to process frame 255: 0.1394 seconds
Time taken to process frame 238: 0.0515 seconds
Time taken to process frame 221: 0.0839 seconds
Time taken to process frame 227: 0.0994 seconds
Time taken to process frame 226: 0.0669 seconds
Time taken to process frame 235: 0.0955 seconds
Queue size: 0
Time taken to process frame 235: 0.1707 seconds
Time taken to process frame 238: 0.0648 seconds
Time taken to process frame 223: 0.0931 seconds
Time taken to process frame 244: 0.0373 seconds
Time taken to process frame 244: 0.1039 seconds
Time taken to process frame 256: 0.0606 seconds
Time taken to process frame 239: 0.1003 seconds
Time taken to process frame 222: 0.0867 seconds
Time taken to process frame 227: 0.0296 seconds
Queue size: 0
Time taken to process frame 228: 0.0672 seconds
Time taken to process frame 236: 0.0581 seconds
Time taken to process frame 224: 0.0379 seconds
Time taken to process frame 236: 0.1110 seconds
Time taken to process frame 239: 0.0625 seconds
Time taken to process frame 257: 0.0361 seconds
Time taken to process frame 245: 0.1275 seconds
Queue size: 0
Time taken to process frame 223: 0.0730 seconds
Time taken to process frame 245: 0.1571 seconds
Time taken to process frame 228: 0.1097 seconds
Time taken to process frame 229: 0.1157 seconds
Time taken to process frame 237: 0.0342 seconds
Time taken to process frame 237: 0.1160 seconds
Time taken to process frame 240: 0.2171 seconds
Time taken to process frame 258: 0.0321 seconds
Queue size: 1
Time taken to process frame 225: 0.1525 seconds
Time taken to process frame 240: 0.1253 seconds
Time taken to process frame 246: 0.1053 seconds
Time taken to process frame 224: 0.0853 seconds
Time taken to process frame 246: 0.0753 seconds
Time taken to process frame 229: 0.0851 seconds
Time taken to process frame 238: 0.0453 seconds
Time taken to process frame 238: 0.0743 seconds
Queue size: 0
Time taken to process frame 230: 0.1403 seconds
Time taken to process frame 241: 0.0490 seconds
Time taken to process frame 259: 0.0924 seconds
Time taken to process frame 226: 0.0659 seconds
Time taken to process frame 241: 0.0889 seconds
Time taken to process frame 247: 0.0950 seconds
Time taken to process frame 225: 0.1073 seconds
Queue size: 0
Time taken to process frame 247: 0.1180 seconds
Time taken to process frame 239: 0.0301 seconds
Time taken to process frame 230: 0.1037 seconds
Time taken to process frame 239: 0.0944 seconds
Time taken to process frame 231: 0.0957 seconds
Time taken to process frame 242: 0.1017 seconds
Time taken to process frame 242: 0.0596 seconds
Time taken to process frame 227: 0.0988 seconds
Queue size: 0
Time taken to process frame 248: 0.1154 seconds
Time taken to process frame 260: 0.2352 seconds
Time taken to process frame 248: 0.1450 seconds
Time taken to process frame 240: 0.1313 seconds
Time taken to process frame 226: 0.2079 seconds
Time taken to process frame 243: 0.0239 seconds
Queue size: 0
Time taken to process frame 231: 0.2111 seconds
Time taken to process frame 232: 0.2105 seconds
Time taken to process frame 243: 0.1988 seconds
Time taken to process frame 240: 0.2997 seconds
Time taken to process frame 249: 0.1433 seconds
Time taken to process frame 261: 0.1183 seconds
Time taken to process frame 249: 0.1045 seconds
Time taken to process frame 232: 0.0475 seconds
Time taken to process frame 244: 0.1319 seconds
Time taken to process frame 228: 0.2280 seconds
Queue size: 0Time taken to process frame 227: 0.0979 seconds

Time taken to process frame 244: 0.0497 seconds
Time taken to process frame 241: 0.1764 seconds
Time taken to process frame 262: 0.0605 seconds
Time taken to process frame 233: 0.1367 seconds
Time taken to process frame 229: 0.0322 seconds
Time taken to process frame 241: 0.1433 seconds
Time taken to process frame 250: 0.1395 seconds
Queue size: 0
Time taken to process frame 250: 0.1443 seconds
Time taken to process frame 245: 0.2065 seconds
Time taken to process frame 245: 0.1410 seconds
Time taken to process frame 242: 0.0857 seconds
Time taken to process frame 234: 0.0585 seconds
Time taken to process frame 233: 0.0422 seconds
Time taken to process frame 263: 0.1487 seconds
Time taken to process frame 242: 0.0837 seconds
Time taken to process frame 228: 0.0900 seconds
Queue size: 0
Time taken to process frame 230: 0.0947 seconds
Time taken to process frame 251: 0.0907 seconds
Time taken to process frame 251: 0.1513 seconds
Time taken to process frame 246: 0.1414 seconds
Time taken to process frame 235: 0.1456 seconds
Time taken to process frame 243: 0.1296 seconds
Time taken to process frame 234: 0.1087 seconds
Queue size: 0Time taken to process frame 264: 0.0645 seconds

Time taken to process frame 246: 0.1077 seconds
Time taken to process frame 243: 0.0675 seconds
Time taken to process frame 252: 0.0462 seconds
Time taken to process frame 231: 0.0894 seconds
Time taken to process frame 252: 0.0519 seconds
Time taken to process frame 229: 0.0714 seconds
Time taken to process frame 247: 0.0523 seconds
Queue size: 0
Time taken to process frame 236: 0.0965 seconds
Time taken to process frame 265: 0.0854 seconds
Time taken to process frame 244: 0.0848 seconds
Time taken to process frame 232: 0.0725 seconds
Time taken to process frame 244: 0.1097 seconds
Time taken to process frame 247: 0.1463 seconds
Time taken to process frame 253: 0.1041 seconds
Time taken to process frame 235: 0.2030 seconds
Time taken to process frame 253: 0.0968 seconds
Queue size: 0
Time taken to process frame 248: 0.0716 seconds
Time taken to process frame 237: 0.0506 seconds
Time taken to process frame 230: 0.1239 seconds
Time taken to process frame 233: 0.0717 seconds
Time taken to process frame 266: 0.1406 seconds
Time taken to process frame 248: 0.1124 seconds
Queue size: 0
Time taken to process frame 249: 0.0736 seconds
Time taken to process frame 254: 0.0671 seconds
Time taken to process frame 245: 0.2178 seconds
Time taken to process frame 245: 0.1887 seconds
Time taken to process frame 236: 0.1562 seconds
Time taken to process frame 254: 0.0305 seconds
Time taken to process frame 238: 0.1208 seconds
Time taken to process frame 231: 0.1116 seconds
Time taken to process frame 267: 0.0349 seconds
Time taken to process frame 234: 0.1061 seconds
Queue size: 0
Time taken to process frame 249: 0.0941 seconds
Time taken to process frame 237: 0.0595 seconds
Time taken to process frame 250: 0.1304 seconds
Time taken to process frame 255: 0.1398 seconds
Time taken to process frame 246: 0.1222 seconds
Time taken to process frame 232: 0.0348 seconds
Time taken to process frame 255: 0.1090 seconds
Time taken to process frame 246: 0.1499 seconds
Queue size: 5
Time taken to process frame 268: 0.1220 seconds
Time taken to process frame 239: 0.0677 seconds
Time taken to process frame 235: 0.1228 seconds
Time taken to process frame 251: 0.1108 seconds
Time taken to process frame 250: 0.1548 seconds
Time taken to process frame 238: 0.1251 seconds
Time taken to process frame 247: 0.1052 seconds
Time taken to process frame 233: 0.0405 seconds
Queue size: 0
Time taken to process frame 256: 0.1111 seconds
Time taken to process frame 256: 0.0500 seconds
Time taken to process frame 269: 0.0421 seconds
Time taken to process frame 247: 0.0868 seconds
Time taken to process frame 236: 0.0386 seconds
Time taken to process frame 240: 0.0778 seconds
Time taken to process frame 252: 0.0390 seconds
Time taken to process frame 251: 0.0550 seconds
Time taken to process frame 248: 0.0712 seconds
Queue size: 3
Time taken to process frame 234: 0.0409 seconds
Time taken to process frame 239: 0.0943 seconds
Time taken to process frame 257: 0.1101 seconds
Time taken to process frame 248: 0.0455 seconds
Time taken to process frame 257: 0.1010 seconds
Time taken to process frame 270: 0.0938 seconds
Queue size: 0
Time taken to process frame 237: 0.1033 seconds
Time taken to process frame 241: 0.0630 seconds
Time taken to process frame 253: 0.0931 seconds
Time taken to process frame 249: 0.0292 seconds
Time taken to process frame 252: 0.1039 seconds
Time taken to process frame 235: 0.0821 seconds
Time taken to process frame 240: 0.0886 seconds
Time taken to process frame 258: 0.0820 seconds
Time taken to process frame 258: 0.0617 seconds
Time taken to process frame 271: 0.0534 seconds
Queue size: 2
Time taken to process frame 249: 0.1253 seconds
Time taken to process frame 254: 0.0855 seconds
Time taken to process frame 238: 0.1229 seconds
Time taken to process frame 242: 0.1244 seconds
Time taken to process frame 250: 0.1102 seconds
Time taken to process frame 259: 0.0430 seconds
Queue size: 1
Time taken to process frame 241: 0.0835 seconds
Time taken to process frame 259: 0.0807 seconds
Queue size: 0
Time taken to process frame 253: 0.3209 seconds
Time taken to process frame 272: 0.2609 seconds
Time taken to process frame 254: 0.0465 seconds
Time taken to process frame 242: 0.1940 seconds
Time taken to process frame 243: 0.2926 seconds
Queue size: 0
Time taken to process frame 260: 0.2685 seconds
Time taken to process frame 243: 0.0380 seconds
Time taken to process frame 239: 0.3376 seconds
Time taken to process frame 251: 0.3432 seconds
Time taken to process frame 273: 0.2813 seconds
Time taken to process frame 236: 0.6720 seconds
Time taken to process frame 260: 0.4081 seconds
Time taken to process frame 244: 0.1539 seconds
Queue size: 1
Time taken to process frame 244: 0.2221 seconds
Time taken to process frame 240: 0.1981 seconds
Time taken to process frame 274: 0.0962 seconds
Time taken to process frame 237: 0.0653 seconds
Time taken to process frame 255: 0.3998 seconds
Time taken to process frame 255: 0.6901 seconds
Time taken to process frame 252: 0.2805 seconds
Queue size: 0
Time taken to process frame 250: 0.8146 seconds
Time taken to process frame 238: 0.1184 seconds
Time taken to process frame 245: 0.2011 seconds
Time taken to process frame 261: 0.5641 seconds
Time taken to process frame 253: 0.2102 seconds
Time taken to process frame 246: 0.1391 seconds
Time taken to process frame 261: 0.3928 seconds
Time taken to process frame 275: 0.3187 seconds
Queue size: 0
Time taken to process frame 239: 0.1829 seconds
Time taken to process frame 256: 0.3838 seconds
Time taken to process frame 262: 0.1830 seconds
Time taken to process frame 251: 0.3454 seconds
Time taken to process frame 256: 0.4545 seconds
Queue size: 0
Time taken to process frame 241: 0.5551 seconds
Time taken to process frame 245: 0.6630 seconds
Time taken to process frame 257: 0.2055 seconds
Time taken to process frame 242: 0.1236 seconds
Time taken to process frame 254: 0.2691 seconds
Time taken to process frame 240: 0.2999 seconds
Queue size: 0
Time taken to process frame 247: 0.1543 seconds
Time taken to process frame 257: 0.2260 seconds
Time taken to process frame 262: 0.2810 seconds
Time taken to process frame 276: 0.3255 seconds
Time taken to process frame 252: 0.3084 seconds
Time taken to process frame 246: 0.2073 seconds
Time taken to process frame 243: 0.2188 seconds
Queue size: 0
Time taken to process frame 258: 0.1023 seconds
Time taken to process frame 258: 0.2506 seconds
Time taken to process frame 263: 0.2583 seconds
Time taken to process frame 259: 0.0340 seconds
Time taken to process frame 277: 0.1324 seconds
Time taken to process frame 248: 0.2798 seconds
Time taken to process frame 263: 0.2846 seconds
Time taken to process frame 264: 0.0694 seconds
Time taken to process frame 244: 0.1522 seconds
Time taken to process frame 247: 0.2024 seconds
Time taken to process frame 259: 0.1357 seconds
Queue size: 0
Time taken to process frame 255: 0.4098 seconds
Time taken to process frame 249: 0.1203 seconds
Time taken to process frame 264: 0.1323 seconds
Time taken to process frame 253: 0.3358 seconds
Time taken to process frame 248: 0.1231 seconds
Time taken to process frame 260: 0.2951 seconds
Time taken to process frame 265: 0.2271 seconds
Time taken to process frame 241: 0.5857 seconds
Queue size: 0
Time taken to process frame 256: 0.2132 seconds
Time taken to process frame 278: 0.3478 seconds
Time taken to process frame 260: 0.2447 seconds
Time taken to process frame 254: 0.1949 seconds
Time taken to process frame 279: 0.0603 seconds
Time taken to process frame 265: 0.2530 seconds
Time taken to process frame 245: 0.4508 seconds
Time taken to process frame 250: 0.3688 seconds
Queue size: 1
Time taken to process frame 242: 0.2310 seconds
Time taken to process frame 249: 0.3021 seconds
Time taken to process frame 257: 0.1943 seconds
Time taken to process frame 261: 0.3381 seconds
Time taken to process frame 255: 0.2102 seconds
Time taken to process frame 266: 0.3571 seconds
Time taken to process frame 261: 0.2699 secondsTime taken to process frame 251: 0.1597 seconds

Time taken to process frame 266: 0.2369 seconds
Time taken to process frame 246: 0.2031 seconds
Queue size: 0
Time taken to process frame 258: 0.1421 seconds
Time taken to process frame 243: 0.1897 seconds
Time taken to process frame 280: 0.3069 seconds
Time taken to process frame 256: 0.1773 seconds
Time taken to process frame 244: 0.0520 seconds
Time taken to process frame 262: 0.1505 seconds
Time taken to process frame 281: 0.0508 seconds
Time taken to process frame 262: 0.2657 seconds
Time taken to process frame 267: 0.1470 seconds
Time taken to process frame 259: 0.1508 seconds
Queue size: 0
Time taken to process frame 252: 0.2614 seconds
Time taken to process frame 247: 0.2345 seconds
Time taken to process frame 250: 0.5058 seconds
Time taken to process frame 267: 0.4009 seconds
Time taken to process frame 268: 0.0730 seconds
Time taken to process frame 263: 0.1605 seconds
Time taken to process frame 263: 0.1235 seconds
Time taken to process frame 245: 0.2223 seconds
Time taken to process frame 282: 0.2135 seconds
Time taken to process frame 257: 0.2708 seconds
Queue size: 0
Time taken to process frame 251: 0.0673 seconds
Time taken to process frame 253: 0.1507 seconds
Time taken to process frame 258: 0.0520 seconds
Time taken to process frame 260: 0.1887 seconds
Time taken to process frame 248: 0.1608 seconds
Time taken to process frame 268: 0.1268 seconds
Time taken to process frame 264: 0.0531 seconds
Time taken to process frame 283: 0.1518 seconds
Queue size: 0
Time taken to process frame 246: 0.0435 seconds
Time taken to process frame 264: 0.0956 seconds
Time taken to process frame 254: 0.0733 seconds
Time taken to process frame 252: 0.1097 seconds
Time taken to process frame 261: 0.0698 seconds
Time taken to process frame 269: 0.0352 secondsTime taken to process frame 259: 0.0987 seconds

Time taken to process frame 249: 0.0983 seconds
Time taken to process frame 284: 0.0330 seconds
Queue size: 0
Time taken to process frame 265: 0.0862 seconds
Time taken to process frame 247: 0.0911 seconds
Time taken to process frame 265: 0.1379 seconds
Time taken to process frame 253: 0.0456 seconds
Time taken to process frame 269: 0.1172 seconds
Time taken to process frame 255: 0.1072 seconds
Time taken to process frame 262: 0.0821 seconds
Queue size: 0
Time taken to process frame 270: 0.0979 seconds
Time taken to process frame 260: 0.1190 seconds
Time taken to process frame 266: 0.0336 seconds
Time taken to process frame 250: 0.1174 seconds
Time taken to process frame 248: 0.0350 seconds
Time taken to process frame 285: 0.1082 seconds
Time taken to process frame 256: 0.0591 seconds
Time taken to process frame 266: 0.0958 seconds
Queue size: 0
Time taken to process frame 263: 0.0290 seconds
Time taken to process frame 254: 0.0901 seconds
Time taken to process frame 270: 0.0817 seconds
Time taken to process frame 271: 0.0244 seconds
Time taken to process frame 261: 0.0594 seconds
Time taken to process frame 251: 0.0288 seconds
Time taken to process frame 267: 0.1010 seconds
Time taken to process frame 249: 0.1048 seconds
Queue size: 0
Time taken to process frame 286: 0.0621 seconds
Time taken to process frame 267: 0.0300 seconds
Time taken to process frame 257: 0.0905 seconds
Time taken to process frame 264: 0.0924 seconds
Time taken to process frame 271: 0.0687 seconds
Time taken to process frame 272: 0.1039 seconds
Time taken to process frame 255: 0.1419 seconds
Queue size: 0
Time taken to process frame 262: 0.1068 seconds
Time taken to process frame 268: 0.0630 seconds
Time taken to process frame 252: 0.1115 seconds
Time taken to process frame 287: 0.0991 seconds
Time taken to process frame 250: 0.1386 seconds
Time taken to process frame 258: 0.0781 seconds
Time taken to process frame 268: 0.1358 seconds
Queue size: 0
Time taken to process frame 272: 0.1144 seconds
Time taken to process frame 256: 0.0838 seconds
Time taken to process frame 265: 0.1952 seconds
Time taken to process frame 263: 0.0964 seconds
Time taken to process frame 273: 0.2199 seconds
Time taken to process frame 253: 0.0851 seconds
Time taken to process frame 269: 0.1377 seconds
Time taken to process frame 288: 0.1099 seconds
Queue size: 0
Time taken to process frame 251: 0.1545 seconds
Time taken to process frame 257: 0.1259 seconds
Time taken to process frame 273: 0.1141 seconds
Queue size: 0
Time taken to process frame 269: 0.2010 seconds
Time taken to process frame 259: 0.2237 seconds
Time taken to process frame 274: 0.0462 seconds
Time taken to process frame 289: 0.1143 seconds
Time taken to process frame 266: 0.2904 seconds
Time taken to process frame 264: 0.2778 seconds
Time taken to process frame 274: 0.2766 seconds
Queue size: 0
Time taken to process frame 254: 0.2574 seconds
Time taken to process frame 275: 0.1248 seconds
Time taken to process frame 275: 0.2896 seconds
Queue size: 0
Time taken to process frame 290: 0.3139 seconds
Time taken to process frame 267: 0.2695 seconds
Time taken to process frame 276: 0.0749 seconds
Time taken to process frame 270: 0.4766 seconds
Time taken to process frame 252: 0.5560 seconds
Time taken to process frame 277: 0.0729 seconds
Time taken to process frame 270: 0.6398 seconds
Time taken to process frame 260: 0.5218 seconds
Time taken to process frame 265: 0.4167 seconds
Queue size: 0
Time taken to process frame 276: 0.2799 seconds
Time taken to process frame 268: 0.1935 seconds
Time taken to process frame 266: 0.0575 seconds
Time taken to process frame 277: 0.0540 seconds
Time taken to process frame 271: 0.0968 seconds
Time taken to process frame 261: 0.1392 seconds
Time taken to process frame 291: 0.2765 seconds
Time taken to process frame 278: 0.2140 seconds
Time taken to process frame 258: 0.8064 seconds
Time taken to process frame 255: 0.5719 seconds
Time taken to process frame 271: 0.3124 seconds
Queue size: 6
Time taken to process frame 253: 0.3043 seconds
Time taken to process frame 278: 0.1348 seconds
Time taken to process frame 269: 0.1478 seconds
Time taken to process frame 272: 0.1461 seconds
Queue size: 0
Time taken to process frame 259: 0.2361 seconds
Time taken to process frame 272: 0.1064 seconds
Time taken to process frame 279: 0.1307 seconds
Time taken to process frame 256: 0.2653 seconds
Time taken to process frame 279: 0.1306 seconds
Time taken to process frame 267: 0.2559 seconds
Time taken to process frame 292: 0.2459 seconds
Time taken to process frame 262: 0.3260 seconds
Queue size: 0
Time taken to process frame 270: 0.2449 seconds
Time taken to process frame 273: 0.2372 seconds
Time taken to process frame 268: 0.0928 seconds
Time taken to process frame 293: 0.1504 seconds
Time taken to process frame 263: 0.1746 seconds
Time taken to process frame 257: 0.2662 seconds
Queue size: 0
Time taken to process frame 280: 0.3587 seconds
Time taken to process frame 274: 0.1974 seconds
Time taken to process frame 271: 0.2376 seconds
Time taken to process frame 254: 0.5736 seconds
Time taken to process frame 273: 0.4967 seconds
Time taken to process frame 281: 0.1011 seconds
Time taken to process frame 260: 0.4944 seconds
Time taken to process frame 269: 0.3178 seconds
Queue size: 0
Time taken to process frame 294: 0.3158 seconds
Time taken to process frame 280: 0.4972 seconds
Time taken to process frame 274: 0.2070 seconds
Time taken to process frame 264: 0.4074 seconds
Time taken to process frame 272: 0.3245 seconds
Queue size: 0
Time taken to process frame 275: 0.3805 seconds
Time taken to process frame 282: 0.2851 seconds
Time taken to process frame 270: 0.2671 seconds
Time taken to process frame 281: 0.2598 seconds
Time taken to process frame 261: 0.3108 seconds
Time taken to process frame 275: 0.1762 seconds
Time taken to process frame 258: 0.5703 seconds
Time taken to process frame 295: 0.3263 seconds
Time taken to process frame 255: 0.4086 seconds
Queue size: 0
Time taken to process frame 276: 0.1149 seconds
Time taken to process frame 273: 0.2730 seconds
Time taken to process frame 265: 0.3190 seconds
Time taken to process frame 276: 0.1435 seconds
Time taken to process frame 256: 0.1270 seconds
Time taken to process frame 262: 0.0856 seconds
Queue size: 0
Time taken to process frame 259: 0.2844 seconds
Time taken to process frame 271: 0.2281 seconds
Time taken to process frame 274: 0.1422 seconds
Time taken to process frame 283: 0.0983 seconds
Time taken to process frame 266: 0.1587 seconds
Time taken to process frame 277: 0.2106 seconds
Time taken to process frame 296: 0.2467 seconds
Queue size: 0
Time taken to process frame 263: 0.1819 seconds
Time taken to process frame 282: 0.2805 seconds
Time taken to process frame 272: 0.1702 seconds
Time taken to process frame 284: 0.1782 seconds
Time taken to process frame 267: 0.1736 seconds
Time taken to process frame 297: 0.1753 seconds
Time taken to process frame 257: 0.3547 seconds
Time taken to process frame 275: 0.2575 seconds
Time taken to process frame 283: 0.0909 seconds
Time taken to process frame 277: 0.3375 seconds
Queue size: 0
Time taken to process frame 278: 0.2528 seconds
Time taken to process frame 298: 0.1006 seconds
Time taken to process frame 285: 0.1433 seconds
Time taken to process frame 260: 0.3134 seconds
Time taken to process frame 273: 0.2565 seconds
Time taken to process frame 278: 0.1672 seconds
Queue size: 0
Time taken to process frame 268: 0.2773 seconds
Time taken to process frame 284: 0.2169 seconds
Time taken to process frame 258: 0.2579 seconds
Time taken to process frame 274: 0.0715 seconds
Time taken to process frame 279: 0.1794 seconds
Time taken to process frame 264: 0.4598 seconds
Time taken to process frame 279: 0.1123 seconds
Time taken to process frame 261: 0.1770 seconds
Time taken to process frame 269: 0.1113 seconds
Queue size: 0
Time taken to process frame 299: 0.2883 seconds
Time taken to process frame 259: 0.1574 seconds
Time taken to process frame 276: 0.4189 seconds
Time taken to process frame 286: 0.4181 seconds
Time taken to process frame 262: 0.1556 seconds
Time taken to process frame 270: 0.1858 seconds
Time taken to process frame 275: 0.2513 seconds
Time taken to process frame 285: 0.3528 seconds
Queue size: 4
Time taken to process frame 277: 0.2131 seconds
Time taken to process frame 276: 0.1136 seconds
Time taken to process frame 271: 0.1312 seconds
Time taken to process frame 287: 0.2243 seconds
Time taken to process frame 280: 0.4040 seconds
Time taken to process frame 260: 0.3260 seconds
Time taken to process frame 300: 0.3190 seconds
Time taken to process frame 265: 0.3807 seconds
Queue size: 3
Time taken to process frame 280: 0.5336 seconds
Time taken to process frame 286: 0.2225 seconds
Time taken to process frame 278: 0.1400 seconds
Time taken to process frame 263: 0.2853 seconds
Time taken to process frame 281: 0.1458 seconds
Time taken to process frame 264: 0.0789 seconds
Time taken to process frame 288: 0.1824 seconds
Time taken to process frame 266: 0.1491 seconds
Time taken to process frame 287: 0.1284 seconds
Time taken to process frame 272: 0.2529 seconds
Time taken to process frame 301: 0.2039 seconds
Queue size: 1
Time taken to process frame 261: 0.2687 seconds
Time taken to process frame 282: 0.1478 seconds
Time taken to process frame 277: 0.3897 seconds
Time taken to process frame 281: 0.2900 seconds
Time taken to process frame 273: 0.1393 seconds
Time taken to process frame 302: 0.1200 seconds
Time taken to process frame 265: 0.2109 seconds
Queue size: 0
Time taken to process frame 288: 0.1926 seconds
Time taken to process frame 289: 0.1581 seconds
Time taken to process frame 267: 0.2374 seconds
Time taken to process frame 279: 0.3255 seconds
Time taken to process frame 278: 0.1191 seconds
Time taken to process frame 283: 0.1794 seconds
Time taken to process frame 303: 0.1313 seconds
Time taken to process frame 274: 0.1605 seconds
Time taken to process frame 262: 0.2570 seconds
Queue size: 0
Time taken to process frame 284: 0.0947 seconds
Time taken to process frame 282: 0.2539 seconds
Time taken to process frame 279: 0.1531 seconds
Time taken to process frame 268: 0.1404 seconds
Time taken to process frame 263: 0.0981 seconds
Time taken to process frame 289: 0.2657 seconds
Time taken to process frame 266: 0.3235 seconds
Time taken to process frame 280: 0.3105 seconds
Time taken to process frame 304: 0.2258 seconds
Time taken to process frame 283: 0.1494 secondsTime taken to process frame 290: 0.2574 seconds

Queue size: 0
Time taken to process frame 285: 0.1736 seconds
Time taken to process frame 284: 0.1127 seconds
Time taken to process frame 290: 0.1758 seconds
Time taken to process frame 281: 0.1574 seconds
Time taken to process frame 280: 0.2810 seconds
Time taken to process frame 264: 0.2446 seconds
Time taken to process frame 291: 0.1346 seconds
Time taken to process frame 269: 0.2919 seconds
Time taken to process frame 275: 0.3486 seconds
Queue size: 0
Time taken to process frame 286: 0.0936 seconds
Time taken to process frame 285: 0.0838 seconds
Time taken to process frame 267: 0.1496 seconds
Time taken to process frame 305: 0.2657 seconds
Time taken to process frame 276: 0.0395 seconds
Time taken to process frame 281: 0.0853 seconds
Time taken to process frame 282: 0.1155 seconds
Queue size: 0
Time taken to process frame 286: 0.1317 seconds
Time taken to process frame 291: 0.0913 seconds
Time taken to process frame 306: 0.1056 seconds
Time taken to process frame 268: 0.1979 seconds
Time taken to process frame 270: 0.2659 seconds
Time taken to process frame 282: 0.1471 seconds
Time taken to process frame 292: 0.1870 seconds
Time taken to process frame 265: 0.2405 seconds
Time taken to process frame 283: 0.1863 seconds
Time taken to process frame 292: 0.1335 seconds
Queue size: 0
Time taken to process frame 277: 0.2109 seconds
Time taken to process frame 287: 0.2499 seconds
Time taken to process frame 307: 0.1662 seconds
Time taken to process frame 269: 0.1403 seconds
Time taken to process frame 283: 0.1214 seconds
Time taken to process frame 293: 0.0411 seconds
Time taken to process frame 266: 0.0925 seconds
Time taken to process frame 271: 0.1558 seconds
Time taken to process frame 293: 0.0279 seconds
Time taken to process frame 287: 0.1568 seconds
Time taken to process frame 284: 0.0809 seconds
Time taken to process frame 288: 0.0450 seconds
Queue size: 0
Time taken to process frame 308: 0.0410 seconds
Time taken to process frame 278: 0.0337 seconds
Time taken to process frame 294: 0.0909 seconds
Time taken to process frame 270: 0.1200 seconds
Time taken to process frame 267: 0.0940 seconds
Time taken to process frame 284: 0.1027 seconds
Queue size: 0
Time taken to process frame 294: 0.0946 seconds
Time taken to process frame 288: 0.0641 seconds
Time taken to process frame 272: 0.1026 seconds
Time taken to process frame 289: 0.1010 seconds
Time taken to process frame 285: 0.1394 seconds
Time taken to process frame 309: 0.0880 seconds
Time taken to process frame 279: 0.0880 seconds
Time taken to process frame 271: 0.0580 seconds
Time taken to process frame 295: 0.1174 seconds
Time taken to process frame 268: 0.0511 seconds
Queue size: 0
Time taken to process frame 286: 0.0437 seconds
Time taken to process frame 289: 0.1191 seconds
Time taken to process frame 273: 0.1246 seconds
Time taken to process frame 295: 0.1716 seconds
Time taken to process frame 285: 0.2026 seconds
Time taken to process frame 290: 0.1143 seconds
Queue size: 1
Time taken to process frame 310: 0.1143 seconds
Time taken to process frame 296: 0.0378 seconds
Time taken to process frame 272: 0.1072 seconds
Time taken to process frame 280: 0.1423 seconds
Time taken to process frame 269: 0.0831 seconds
Time taken to process frame 287: 0.0831 seconds
Time taken to process frame 296: 0.0424 seconds
Time taken to process frame 286: 0.0624 seconds
Queue size: 2
Time taken to process frame 290: 0.1248 seconds
Time taken to process frame 274: 0.1072 seconds
Time taken to process frame 291: 0.0975 seconds
Time taken to process frame 281: 0.0385 seconds
Time taken to process frame 297: 0.1071 seconds
Time taken to process frame 273: 0.0297 seconds
Time taken to process frame 311: 0.1048 seconds
Time taken to process frame 288: 0.0271 seconds
Queue size: 0
Time taken to process frame 270: 0.0989 seconds
Time taken to process frame 291: 0.0277 seconds
Time taken to process frame 275: 0.1082 seconds
Time taken to process frame 287: 0.0993 seconds
Time taken to process frame 298: 0.0360 seconds
Time taken to process frame 297: 0.0960 seconds
Time taken to process frame 292: 0.0855 seconds
Time taken to process frame 282: 0.0803 seconds
Time taken to process frame 312: 0.0274 seconds
Time taken to process frame 274: 0.0727 seconds
Queue size: 0
Time taken to process frame 271: 0.0560 seconds
Time taken to process frame 289: 0.0911 seconds
Time taken to process frame 276: 0.0320 seconds
Time taken to process frame 288: 0.0332 seconds
Time taken to process frame 292: 0.0921 seconds
Time taken to process frame 298: 0.0226 seconds
Time taken to process frame 293: 0.0276 seconds
Time taken to process frame 299: 0.0657 seconds
Time taken to process frame 283: 0.0382 seconds
Queue size: 0
Time taken to process frame 313: 0.0781 seconds
Time taken to process frame 272: 0.0918 seconds
Time taken to process frame 275: 0.1351 seconds
Time taken to process frame 277: 0.0949 secondsTime taken to process frame 290: 0.1220 seconds

Time taken to process frame 289: 0.0808 seconds
Queue size: 0
Time taken to process frame 293: 0.0805 seconds
Time taken to process frame 299: 0.0958 seconds
Time taken to process frame 294: 0.0938 seconds
Time taken to process frame 300: 0.0783 seconds
Time taken to process frame 284: 0.1155 seconds
Time taken to process frame 273: 0.0912 seconds
Time taken to process frame 314: 0.0806 seconds
Time taken to process frame 276: 0.0545 seconds
Queue size: 0
Time taken to process frame 291: 0.0789 seconds
Time taken to process frame 278: 0.0769 seconds
Time taken to process frame 294: 0.0754 seconds
Time taken to process frame 301: 0.0386 seconds
Time taken to process frame 290: 0.1280 seconds
Queue size: 0
Time taken to process frame 295: 0.1767 seconds
Time taken to process frame 274: 0.1341 seconds
Time taken to process frame 300: 0.2376 seconds
Time taken to process frame 285: 0.1964 seconds
Time taken to process frame 279: 0.1042 seconds
Time taken to process frame 315: 0.1766 seconds
Time taken to process frame 277: 0.1618 seconds
Time taken to process frame 291: 0.0582 seconds
Time taken to process frame 292: 0.1321 seconds
Queue size: 0
Time taken to process frame 295: 0.1243 seconds
Time taken to process frame 302: 0.1078 seconds
Time taken to process frame 275: 0.0971 seconds
Time taken to process frame 296: 0.0626 seconds
Time taken to process frame 301: 0.1036 seconds
Time taken to process frame 286: 0.0355 seconds
Time taken to process frame 316: 0.0345 seconds
Time taken to process frame 278: 0.0657 seconds
Time taken to process frame 280: 0.1364 seconds
Queue size: 0
Time taken to process frame 292: 0.1167 seconds
Time taken to process frame 296: 0.0727 seconds
Time taken to process frame 293: 0.1040 seconds
Time taken to process frame 303: 0.0610 seconds
Time taken to process frame 302: 0.0876 seconds
Time taken to process frame 297: 0.0865 seconds
Time taken to process frame 287: 0.0967 seconds
Time taken to process frame 276: 0.0737 seconds
Time taken to process frame 281: 0.0382 seconds
Queue size: 0Time taken to process frame 317: 0.1022 seconds

Time taken to process frame 279: 0.1012 seconds
Time taken to process frame 293: 0.0615 seconds
Time taken to process frame 294: 0.0886 seconds
Time taken to process frame 303: 0.0310 seconds
Time taken to process frame 297: 0.0836 seconds
Time taken to process frame 298: 0.0310 seconds
Time taken to process frame 304: 0.0830 seconds
Time taken to process frame 288: 0.0621 seconds
Queue size: 2
Time taken to process frame 277: 0.0924 seconds
Time taken to process frame 282: 0.0963 seconds
Time taken to process frame 318: 0.0645 seconds
Time taken to process frame 280: 0.1491 seconds
Time taken to process frame 294: 0.0975 seconds
Time taken to process frame 298: 0.0325 seconds
Time taken to process frame 304: 0.0897 seconds
Queue size: 0
Time taken to process frame 295: 0.1297 seconds
Time taken to process frame 299: 0.0941 seconds
Time taken to process frame 278: 0.0711 seconds
Time taken to process frame 305: 0.1241 seconds
Time taken to process frame 283: 0.0350 seconds
Time taken to process frame 289: 0.1021 seconds
Time taken to process frame 281: 0.0261 seconds
Time taken to process frame 319: 0.0757 seconds
Queue size: 0
Time taken to process frame 295: 0.1036 seconds
Time taken to process frame 299: 0.0886 seconds
Time taken to process frame 296: 0.0648 seconds
Time taken to process frame 300: 0.1371 seconds
Time taken to process frame 306: 0.0474 seconds
Time taken to process frame 279: 0.1179 seconds
Time taken to process frame 305: 0.2113 secondsTime taken to process frame 284: 0.0996 seconds

Queue size: 0
Time taken to process frame 296: 0.0344 seconds
Time taken to process frame 282: 0.0912 seconds
Time taken to process frame 290: 0.1705 seconds
Time taken to process frame 320: 0.1471 seconds
Time taken to process frame 300: 0.1300 seconds
Time taken to process frame 297: 0.1054 seconds
Time taken to process frame 301: 0.0914 seconds
Queue size: 0
Time taken to process frame 285: 0.0930 seconds
Time taken to process frame 307: 0.1340 seconds
Time taken to process frame 306: 0.0985 seconds
Time taken to process frame 280: 0.1535 seconds
Time taken to process frame 283: 0.1106 seconds
Time taken to process frame 301: 0.0320 seconds
Time taken to process frame 297: 0.1472 seconds
Time taken to process frame 291: 0.1112 seconds
Time taken to process frame 321: 0.1093 seconds
Queue size: 0
Time taken to process frame 302: 0.0836 seconds
Time taken to process frame 298: 0.0741 seconds
Time taken to process frame 286: 0.0822 seconds
Time taken to process frame 308: 0.0802 seconds
Time taken to process frame 281: 0.0650 seconds
Time taken to process frame 307: 0.1157 seconds
Time taken to process frame 284: 0.0911 seconds
Time taken to process frame 292: 0.0300 seconds
Time taken to process frame 302: 0.0866 seconds
Queue size: 0
Time taken to process frame 298: 0.0771 seconds
Time taken to process frame 303: 0.0277 seconds
Time taken to process frame 322: 0.1004 seconds
Time taken to process frame 299: 0.1032 seconds
Time taken to process frame 287: 0.0999 seconds
Time taken to process frame 309: 0.1008 seconds
Time taken to process frame 282: 0.0818 seconds
Time taken to process frame 308: 0.0681 seconds
Queue size: 2
Time taken to process frame 303: 0.0544 seconds
Time taken to process frame 293: 0.1196 seconds
Time taken to process frame 285: 0.1416 seconds
Time taken to process frame 299: 0.1026 seconds
Time taken to process frame 323: 0.0660 seconds
Time taken to process frame 304: 0.0976 seconds
Queue size: 0
Time taken to process frame 309: 0.1100 seconds
Time taken to process frame 300: 0.2150 seconds
Time taken to process frame 294: 0.0576 seconds
Time taken to process frame 283: 0.1819 seconds
Time taken to process frame 288: 0.2540 seconds
Time taken to process frame 310: 0.2415 seconds
Queue size: 1
Time taken to process frame 324: 0.0895 seconds
Time taken to process frame 304: 0.2304 seconds
Time taken to process frame 286: 0.2572 seconds
Time taken to process frame 284: 0.1457 seconds
Queue size: 0
Time taken to process frame 311: 0.1904 seconds
Time taken to process frame 295: 0.2497 seconds
Time taken to process frame 325: 0.1894 seconds
Time taken to process frame 289: 0.1700 seconds
Time taken to process frame 300: 0.4629 seconds
Queue size: 0
Time taken to process frame 305: 0.4535 seconds
Time taken to process frame 301: 0.4369 seconds
Time taken to process frame 287: 0.2951 seconds
Time taken to process frame 312: 0.2312 seconds
Time taken to process frame 310: 0.5394 seconds
Time taken to process frame 326: 0.2485 seconds
Time taken to process frame 305: 0.4336 seconds
Time taken to process frame 313: 0.0650 seconds
Queue size: 2
Time taken to process frame 301: 0.2849 seconds
Time taken to process frame 306: 0.1181 seconds
Time taken to process frame 311: 0.1536 seconds
Time taken to process frame 306: 0.3325 seconds
Time taken to process frame 296: 0.4276 seconds
Queue size: 0
Time taken to process frame 288: 0.3292 seconds
Time taken to process frame 327: 0.2518 seconds
Time taken to process frame 302: 0.3854 seconds
Time taken to process frame 285: 0.6853 seconds
Time taken to process frame 307: 0.1758 seconds
Time taken to process frame 312: 0.2406 seconds
Time taken to process frame 302: 0.2982 seconds
Time taken to process frame 314: 0.4012 seconds
Queue size: 0
Time taken to process frame 297: 0.2324 seconds
Time taken to process frame 307: 0.3714 seconds
Time taken to process frame 303: 0.1038 seconds
Time taken to process frame 289: 0.3563 seconds
Queue size: 0Time taken to process frame 313: 0.2415 seconds

Time taken to process frame 290: 0.8819 seconds
Time taken to process frame 286: 0.3534 seconds
Time taken to process frame 304: 0.2124 seconds
Time taken to process frame 290: 0.1904 seconds
Time taken to process frame 314: 0.1699 seconds
Queue size: 0
Time taken to process frame 308: 0.3503 seconds
Time taken to process frame 328: 0.6109 seconds
Time taken to process frame 308: 0.5322 seconds
Time taken to process frame 287: 0.2420 seconds
Time taken to process frame 291: 0.2835 seconds
Time taken to process frame 303: 0.7004 seconds
Time taken to process frame 305: 0.2183 seconds
Time taken to process frame 329: 0.0990 seconds
Time taken to process frame 315: 0.1797 seconds
Time taken to process frame 291: 0.2238 seconds
Queue size: 0
Time taken to process frame 288: 0.1288 seconds
Time taken to process frame 289: 0.0250 seconds
Time taken to process frame 316: 0.1013 seconds
Time taken to process frame 304: 0.1432 seconds
Time taken to process frame 315: 0.7406 seconds
Time taken to process frame 292: 0.2284 seconds
Time taken to process frame 309: 0.3099 seconds
Time taken to process frame 292: 0.1876 seconds
Queue size: 0
Time taken to process frame 316: 0.1101 seconds
Time taken to process frame 309: 0.4360 seconds
Time taken to process frame 290: 0.1851 seconds
Time taken to process frame 330: 0.3031 seconds
Time taken to process frame 298: 0.8976 seconds
Time taken to process frame 305: 0.1865 seconds
Time taken to process frame 317: 0.2248 seconds
Time taken to process frame 310: 0.1493 seconds
Time taken to process frame 293: 0.2001 seconds
Time taken to process frame 306: 0.3519 seconds
Time taken to process frame 306: 0.0675 seconds
Queue size: 0
Time taken to process frame 293: 0.2225 seconds
Time taken to process frame 331: 0.1375 seconds
Time taken to process frame 318: 0.0835 seconds
Time taken to process frame 317: 0.1922 seconds
Time taken to process frame 310: 0.2170 seconds
Time taken to process frame 311: 0.1300 seconds
Time taken to process frame 332: 0.1195 seconds
Time taken to process frame 294: 0.1856 seconds
Time taken to process frame 299: 0.2871 seconds
Queue size: 0
Time taken to process frame 294: 0.1602 seconds
Time taken to process frame 291: 0.1422 seconds
Time taken to process frame 311: 0.1401 seconds
Time taken to process frame 307: 0.1881 seconds
Time taken to process frame 319: 0.1781 seconds
Time taken to process frame 333: 0.1255 seconds
Time taken to process frame 307: 0.2622 seconds
Time taken to process frame 318: 0.0410 seconds
Time taken to process frame 295: 0.1325 seconds
Queue size: 0
Time taken to process frame 312: 0.2709 seconds
Time taken to process frame 292: 0.1912 seconds
Time taken to process frame 334: 0.1307 seconds
Time taken to process frame 308: 0.1506 seconds
Time taken to process frame 296: 0.1185 seconds
Time taken to process frame 320: 0.1967 seconds
Time taken to process frame 295: 0.3062 seconds
Time taken to process frame 313: 0.0794 seconds
Time taken to process frame 308: 0.0974 seconds
Time taken to process frame 293: 0.0611 seconds
Time taken to process frame 300: 0.2818 seconds
Time taken to process frame 319: 0.2201 seconds
Queue size: 0
Time taken to process frame 321: 0.0548 seconds
Time taken to process frame 335: 0.1393 seconds
Time taken to process frame 309: 0.1327 seconds
Time taken to process frame 301: 0.0556 seconds
Time taken to process frame 297: 0.1168 seconds
Time taken to process frame 296: 0.0346 seconds
Time taken to process frame 309: 0.1216 seconds
Time taken to process frame 312: 0.1085 seconds
Queue size: 0
Time taken to process frame 294: 0.1041 seconds
Time taken to process frame 314: 0.1172 seconds
Time taken to process frame 336: 0.0454 seconds
Time taken to process frame 320: 0.1306 seconds
Time taken to process frame 322: 0.1176 seconds
Time taken to process frame 298: 0.0320 seconds
Time taken to process frame 310: 0.1159 seconds
Time taken to process frame 302: 0.0960 seconds
Queue size: 0
Time taken to process frame 297: 0.0798 seconds
Time taken to process frame 313: 0.0360 seconds
Time taken to process frame 310: 0.1268 seconds
Time taken to process frame 295: 0.1349 seconds
Time taken to process frame 321: 0.0415 seconds
Time taken to process frame 337: 0.1323 seconds
Time taken to process frame 323: 0.0975 seconds
Time taken to process frame 315: 0.1316 seconds
Queue size: 0
Time taken to process frame 299: 0.1050 seconds
Time taken to process frame 303: 0.0930 seconds
Time taken to process frame 311: 0.1118 seconds
Time taken to process frame 298: 0.0948 seconds
Time taken to process frame 314: 0.1053 seconds
Time taken to process frame 311: 0.0925 seconds
Time taken to process frame 296: 0.0948 seconds
Time taken to process frame 338: 0.0843 seconds
Queue size: 0Time taken to process frame 322: 0.0782 seconds

Time taken to process frame 316: 0.0935 seconds
Time taken to process frame 324: 0.0762 seconds
Time taken to process frame 300: 0.0961 seconds
Time taken to process frame 299: 0.0426 seconds
Time taken to process frame 304: 0.1082 seconds
Time taken to process frame 312: 0.0488 seconds
Time taken to process frame 312: 0.0278 seconds
Queue size: 0
Time taken to process frame 323: 0.0514 seconds
Time taken to process frame 315: 0.1052 seconds
Time taken to process frame 339: 0.0412 seconds
Time taken to process frame 297: 0.0911 seconds
Time taken to process frame 317: 0.0282 seconds
Time taken to process frame 301: 0.0245 seconds
Time taken to process frame 325: 0.1087 seconds
Queue size: 0
Time taken to process frame 300: 0.1015 seconds
Time taken to process frame 305: 0.1154 seconds
Time taken to process frame 324: 0.0311 seconds
Time taken to process frame 313: 0.0987 seconds
Time taken to process frame 313: 0.0974 seconds
Time taken to process frame 316: 0.0485 seconds
Time taken to process frame 298: 0.0455 seconds
Queue size: 0
Time taken to process frame 340: 0.1015 seconds
Time taken to process frame 318: 0.0955 seconds
Time taken to process frame 326: 0.0395 seconds
Time taken to process frame 301: 0.0280 seconds
Time taken to process frame 302: 0.0855 seconds
Time taken to process frame 306: 0.0565 seconds
Time taken to process frame 325: 0.0767 seconds
Time taken to process frame 314: 0.0517 seconds
Time taken to process frame 314: 0.0549 seconds
Queue size: 0
Time taken to process frame 317: 0.1070 seconds
Time taken to process frame 341: 0.0724 seconds
Time taken to process frame 299: 0.1134 seconds
Time taken to process frame 319: 0.0476 seconds
Time taken to process frame 327: 0.0931 seconds
Time taken to process frame 303: 0.0487 seconds
Time taken to process frame 302: 0.0921 seconds
Time taken to process frame 307: 0.1113 seconds
Queue size: 0
Time taken to process frame 315: 0.1207 seconds
Time taken to process frame 326: 0.1315 seconds
Time taken to process frame 318: 0.0944 seconds
Time taken to process frame 315: 0.1361 seconds
Time taken to process frame 328: 0.1236 seconds
Queue size: 0
Time taken to process frame 342: 0.1746 seconds
Time taken to process frame 320: 0.1296 seconds
Time taken to process frame 300: 0.2286 seconds
Time taken to process frame 304: 0.1268 seconds
Time taken to process frame 303: 0.1455 seconds
Time taken to process frame 316: 0.1435 seconds
Time taken to process frame 308: 0.1806 seconds
Time taken to process frame 319: 0.1350 seconds
Time taken to process frame 316: 0.0940 seconds
Time taken to process frame 327: 0.1365 seconds
Queue size: 0
Time taken to process frame 321: 0.0634 seconds
Time taken to process frame 329: 0.1330 seconds
Time taken to process frame 343: 0.0874 seconds
Time taken to process frame 304: 0.1260 seconds
Time taken to process frame 301: 0.1689 seconds
Time taken to process frame 309: 0.1260 seconds
Time taken to process frame 305: 0.2674 seconds
Queue size: 4
Time taken to process frame 317: 0.1665 seconds
Time taken to process frame 328: 0.0845 seconds
Time taken to process frame 317: 0.1554 seconds
Time taken to process frame 322: 0.1842 seconds
Time taken to process frame 344: 0.1610 seconds
Queue size: 0
Time taken to process frame 302: 0.1503 seconds
Time taken to process frame 320: 0.2976 seconds
Time taken to process frame 318: 0.0342 seconds
Time taken to process frame 305: 0.2091 seconds
Time taken to process frame 330: 0.1599 seconds
Time taken to process frame 318: 0.0998 seconds
Time taken to process frame 310: 0.2107 seconds
Time taken to process frame 306: 0.1949 seconds
Time taken to process frame 306: 0.0297 seconds
Time taken to process frame 329: 0.1428 seconds
Time taken to process frame 323: 0.1442 seconds
Queue size: 3
Time taken to process frame 331: 0.0491 seconds
Time taken to process frame 303: 0.1426 seconds
Time taken to process frame 321: 0.1208 seconds
Time taken to process frame 319: 0.0808 seconds
Time taken to process frame 319: 0.0926 seconds
Time taken to process frame 307: 0.1262 seconds
Time taken to process frame 345: 0.1481 seconds
Queue size: 0
Time taken to process frame 324: 0.1235 seconds
Time taken to process frame 330: 0.1616 seconds
Time taken to process frame 307: 0.1241 seconds
Time taken to process frame 332: 0.1041 seconds
Time taken to process frame 311: 0.0290 seconds
Time taken to process frame 304: 0.0991 seconds
Time taken to process frame 322: 0.0874 seconds
Queue size: 0
Time taken to process frame 320: 0.1320 seconds
Time taken to process frame 308: 0.1123 seconds
Time taken to process frame 320: 0.1516 seconds
Time taken to process frame 346: 0.1063 seconds
Time taken to process frame 308: 0.0465 seconds
Time taken to process frame 331: 0.0310 seconds
Time taken to process frame 333: 0.0260 seconds
Time taken to process frame 325: 0.1027 seconds
Time taken to process frame 323: 0.0469 seconds
Queue size: 0
Time taken to process frame 312: 0.1110 seconds
Time taken to process frame 321: 0.0694 seconds
Time taken to process frame 305: 0.1372 seconds
Time taken to process frame 309: 0.0549 seconds
Time taken to process frame 347: 0.0344 seconds
Time taken to process frame 321: 0.0235 seconds
Time taken to process frame 309: 0.0240 seconds
Time taken to process frame 332: 0.0750 seconds
Time taken to process frame 326: 0.0275 seconds
Time taken to process frame 334: 0.0855 seconds
Time taken to process frame 313: 0.0383 seconds
Queue size: 1
Time taken to process frame 324: 0.0880 seconds
Time taken to process frame 306: 0.0362 seconds
Time taken to process frame 322: 0.0926 seconds
Time taken to process frame 348: 0.0986 seconds
Time taken to process frame 310: 0.0905 seconds
Time taken to process frame 322: 0.0856 seconds
Queue size: 0
Time taken to process frame 333: 0.0487 seconds
Time taken to process frame 310: 0.1041 seconds
Time taken to process frame 327: 0.1048 seconds
Time taken to process frame 314: 0.1521 seconds
Queue size: 0
Time taken to process frame 349: 0.0839 seconds
Time taken to process frame 307: 0.1503 seconds
Time taken to process frame 335: 0.2537 seconds
Time taken to process frame 323: 0.0671 seconds
Time taken to process frame 325: 0.2239 seconds
Time taken to process frame 323: 0.2551 seconds
Time taken to process frame 328: 0.1126 seconds
Time taken to process frame 311: 0.1689 seconds
Time taken to process frame 315: 0.1056 seconds
Time taken to process frame 311: 0.2139 seconds
Time taken to process frame 308: 0.0946 seconds
Queue size: 0
Time taken to process frame 334: 0.1844 seconds
Time taken to process frame 350: 0.0979 seconds
Time taken to process frame 336: 0.0641 seconds
Time taken to process frame 326: 0.0410 seconds
Time taken to process frame 316: 0.0427 seconds
Time taken to process frame 324: 0.0857 seconds
Time taken to process frame 312: 0.0591 seconds
Time taken to process frame 324: 0.1555 seconds
Time taken to process frame 312: 0.0980 seconds
Queue size: 0
Time taken to process frame 351: 0.0305 seconds
Time taken to process frame 309: 0.0895 seconds
Time taken to process frame 329: 0.0878 seconds
Time taken to process frame 327: 0.0918 seconds
Time taken to process frame 335: 0.1156 seconds
Time taken to process frame 337: 0.1146 seconds
Time taken to process frame 317: 0.1155 seconds
Queue size: 0
Time taken to process frame 313: 0.0355 seconds
Time taken to process frame 325: 0.1348 seconds
Time taken to process frame 325: 0.1258 seconds
Time taken to process frame 313: 0.0999 seconds
Time taken to process frame 352: 0.1042 seconds
Time taken to process frame 328: 0.0432 seconds
Time taken to process frame 310: 0.1202 seconds
Time taken to process frame 330: 0.1232 seconds
Time taken to process frame 338: 0.0360 seconds
Time taken to process frame 318: 0.0305 seconds
Time taken to process frame 336: 0.0988 seconds
Queue size: 0
Time taken to process frame 326: 0.0280 seconds
Time taken to process frame 326: 0.0220 seconds
Time taken to process frame 314: 0.0716 seconds
Time taken to process frame 353: 0.0275 seconds
Time taken to process frame 314: 0.0793 seconds
Time taken to process frame 311: 0.0325 seconds
Time taken to process frame 331: 0.0284 seconds
Time taken to process frame 329: 0.0860 seconds
Queue size: 0
Time taken to process frame 339: 0.0858 seconds
Time taken to process frame 337: 0.0340 seconds
Time taken to process frame 319: 0.0850 seconds
Time taken to process frame 327: 0.0995 seconds
Time taken to process frame 327: 0.1017 seconds
Queue size: 0
Time taken to process frame 315: 0.1409 seconds
Time taken to process frame 354: 0.1259 seconds
Time taken to process frame 312: 0.1152 seconds
Time taken to process frame 315: 0.1450 seconds
Time taken to process frame 330: 0.1317 seconds
Time taken to process frame 332: 0.1055 seconds
Time taken to process frame 338: 0.1091 seconds
Time taken to process frame 340: 0.1363 seconds
Time taken to process frame 328: 0.0663 seconds
Time taken to process frame 328: 0.0621 seconds
Queue size: 1
Time taken to process frame 316: 0.0351 seconds
Time taken to process frame 320: 0.1553 seconds
Time taken to process frame 313: 0.0350 seconds
Time taken to process frame 316: 0.0275 seconds
Time taken to process frame 355: 0.1247 seconds
Time taken to process frame 333: 0.0277 seconds
Time taken to process frame 331: 0.0398 seconds
Time taken to process frame 341: 0.0440 seconds
Time taken to process frame 339: 0.0494 seconds
Queue size: 0
Time taken to process frame 329: 0.0886 seconds
Time taken to process frame 329: 0.1037 seconds
Time taken to process frame 321: 0.0638 seconds
Time taken to process frame 317: 0.1128 seconds
Time taken to process frame 314: 0.0924 seconds
Time taken to process frame 317: 0.0830 seconds
Time taken to process frame 356: 0.0285 seconds
Time taken to process frame 334: 0.0845 seconds
Queue size: 0
Time taken to process frame 332: 0.0922 seconds
Time taken to process frame 342: 0.0898 seconds
Time taken to process frame 322: 0.0322 seconds
Time taken to process frame 340: 0.1047 seconds
Time taken to process frame 318: 0.0350 seconds
Time taken to process frame 330: 0.1276 seconds
Time taken to process frame 318: 0.0300 seconds
Queue size: 0
Time taken to process frame 315: 0.1027 seconds
Time taken to process frame 330: 0.1339 seconds
Time taken to process frame 343: 0.0290 seconds
Time taken to process frame 357: 0.0850 seconds
Time taken to process frame 333: 0.0273 seconds
Time taken to process frame 323: 0.0310 seconds
Time taken to process frame 335: 0.1006 seconds
Time taken to process frame 341: 0.0329 seconds
Time taken to process frame 319: 0.0844 seconds
Time taken to process frame 331: 0.0290 seconds
Queue size: 0
Time taken to process frame 316: 0.0250 seconds
Time taken to process frame 331: 0.0253 seconds
Time taken to process frame 319: 0.0693 seconds
Time taken to process frame 358: 0.0279 seconds
Time taken to process frame 344: 0.0858 seconds
Time taken to process frame 324: 0.0310 seconds
Time taken to process frame 336: 0.0260 seconds
Time taken to process frame 334: 0.0903 seconds
Queue size: 0
Time taken to process frame 342: 0.0859 seconds
Time taken to process frame 320: 0.1004 seconds
Time taken to process frame 332: 0.0952 seconds
Time taken to process frame 317: 0.0924 seconds
Time taken to process frame 332: 0.1091 seconds
Time taken to process frame 320: 0.1216 seconds
Queue size: 1
Time taken to process frame 359: 0.1157 seconds
Time taken to process frame 325: 0.1017 seconds
Time taken to process frame 337: 0.0939 seconds
Time taken to process frame 345: 0.1499 seconds
Time taken to process frame 343: 0.0559 seconds
Time taken to process frame 335: 0.1465 seconds
Time taken to process frame 333: 0.1288 seconds
Time taken to process frame 321: 0.1118 seconds
Queue size: 2
Time taken to process frame 318: 0.1168 seconds
Time taken to process frame 321: 0.1072 seconds
Time taken to process frame 326: 0.0622 seconds
Time taken to process frame 338: 0.0925 seconds
Time taken to process frame 333: 0.1606 seconds
Time taken to process frame 346: 0.0717 seconds
Time taken to process frame 336: 0.0342 seconds
Time taken to process frame 360: 0.1772 seconds
Time taken to process frame 344: 0.0994 seconds
Queue size: 0
Time taken to process frame 334: 0.1043 seconds
Time taken to process frame 322: 0.0942 seconds
Time taken to process frame 319: 0.0953 seconds
Time taken to process frame 339: 0.0304 seconds
Time taken to process frame 322: 0.0912 seconds
Time taken to process frame 334: 0.0952 seconds
Time taken to process frame 327: 0.1020 seconds
Queue size: 0
Time taken to process frame 347: 0.1079 seconds
Time taken to process frame 361: 0.0375 seconds
Time taken to process frame 337: 0.0975 seconds
Time taken to process frame 323: 0.0624 seconds
Time taken to process frame 345: 0.1194 seconds
Time taken to process frame 323: 0.0608 seconds
Time taken to process frame 335: 0.1373 seconds
Time taken to process frame 340: 0.1059 seconds
Time taken to process frame 320: 0.1393 seconds
Queue size: 0
Time taken to process frame 328: 0.0560 seconds
Time taken to process frame 348: 0.0632 seconds
Time taken to process frame 335: 0.1554 seconds
Time taken to process frame 338: 0.0919 seconds
Time taken to process frame 362: 0.0986 seconds
Time taken to process frame 346: 0.0820 seconds
Time taken to process frame 324: 0.1050 seconds
Time taken to process frame 341: 0.0720 seconds
Queue size: 0
Time taken to process frame 336: 0.1620 seconds
Time taken to process frame 324: 0.1120 seconds
Time taken to process frame 321: 0.1440 seconds
Time taken to process frame 329: 0.1164 seconds
Time taken to process frame 349: 0.1136 seconds
Time taken to process frame 339: 0.0903 seconds
Time taken to process frame 336: 0.0678 seconds
Time taken to process frame 363: 0.0666 seconds
Time taken to process frame 347: 0.0362 seconds
Queue size: 1
Time taken to process frame 342: 0.1143 seconds
Time taken to process frame 322: 0.1251 seconds
Time taken to process frame 325: 0.2334 seconds
Time taken to process frame 337: 0.1165 seconds
Queue size: 0
Time taken to process frame 325: 0.1592 seconds
Time taken to process frame 364: 0.1459 seconds
Time taken to process frame 330: 0.2409 seconds
Time taken to process frame 337: 0.1442 seconds
Time taken to process frame 343: 0.1093 seconds
Time taken to process frame 340: 0.2336 seconds
Time taken to process frame 350: 0.2842 seconds
Time taken to process frame 348: 0.1788 seconds
Queue size: 3
Time taken to process frame 323: 0.1102 seconds
Time taken to process frame 326: 0.0954 seconds
Time taken to process frame 326: 0.0858 seconds
Time taken to process frame 338: 0.1101 seconds
Time taken to process frame 338: 0.1068 seconds
Time taken to process frame 349: 0.0811 seconds
Time taken to process frame 331: 0.1464 seconds
Time taken to process frame 341: 0.0825 seconds
Time taken to process frame 344: 0.1102 seconds
Queue size: 0
Time taken to process frame 327: 0.1344 seconds
Time taken to process frame 365: 0.2265 seconds
Time taken to process frame 324: 0.1240 seconds
Time taken to process frame 339: 0.1084 seconds
Time taken to process frame 327: 0.0950 seconds
Time taken to process frame 350: 0.0835 seconds
Time taken to process frame 351: 0.0539 seconds
Time taken to process frame 342: 0.0938 seconds
Queue size: 0
Time taken to process frame 339: 0.1100 seconds
Time taken to process frame 332: 0.1286 seconds
Time taken to process frame 352: 0.0267 seconds
Time taken to process frame 345: 0.2419 seconds
Time taken to process frame 328: 0.1741 seconds
Time taken to process frame 366: 0.1626 seconds
Queue size: 0
Time taken to process frame 340: 0.2397 seconds
Time taken to process frame 325: 0.2391 seconds
Time taken to process frame 328: 0.1964 seconds
Time taken to process frame 351: 0.2292 seconds
Time taken to process frame 346: 0.1054 seconds
Time taken to process frame 367: 0.0753 seconds
Queue size: 3
Time taken to process frame 343: 0.2393 seconds
Time taken to process frame 353: 0.1648 seconds
Time taken to process frame 340: 0.2453 seconds
Time taken to process frame 329: 0.1651 seconds
Time taken to process frame 326: 0.1055 seconds
Time taken to process frame 333: 0.3237 seconds
Time taken to process frame 329: 0.1991 seconds
Time taken to process frame 341: 0.2359 seconds
Time taken to process frame 368: 0.1282 seconds
Time taken to process frame 347: 0.1148 seconds
Queue size: 0
Time taken to process frame 354: 0.0848 seconds
Time taken to process frame 352: 0.2108 seconds
Time taken to process frame 341: 0.0491 seconds
Time taken to process frame 344: 0.1348 seconds
Time taken to process frame 334: 0.0408 seconds
Time taken to process frame 327: 0.1257 seconds
Time taken to process frame 330: 0.1979 seconds
Time taken to process frame 369: 0.0579 seconds
Time taken to process frame 353: 0.0325 seconds
Time taken to process frame 330: 0.1412 seconds
Time taken to process frame 342: 0.1075 seconds
Queue size: 0
Time taken to process frame 355: 0.0902 seconds
Time taken to process frame 348: 0.0495 seconds
Time taken to process frame 345: 0.1144 seconds
Time taken to process frame 342: 0.1040 seconds
Time taken to process frame 335: 0.0840 seconds
Time taken to process frame 328: 0.0740 seconds
Time taken to process frame 331: 0.0609 seconds
Queue size: 0
Time taken to process frame 370: 0.0842 seconds
Time taken to process frame 354: 0.0851 seconds
Time taken to process frame 331: 0.0526 seconds
Time taken to process frame 356: 0.0270 seconds
Time taken to process frame 343: 0.0576 seconds
Time taken to process frame 349: 0.0875 seconds
Time taken to process frame 336: 0.0724 seconds
Time taken to process frame 346: 0.0607 seconds
Queue size: 0
Time taken to process frame 343: 0.1137 seconds
Time taken to process frame 332: 0.0975 seconds
Time taken to process frame 371: 0.0557 seconds
Time taken to process frame 329: 0.0944 seconds
Time taken to process frame 332: 0.0846 seconds
Time taken to process frame 344: 0.0915 seconds
Time taken to process frame 357: 0.1016 seconds
Time taken to process frame 355: 0.1383 seconds
Queue size: 2
Time taken to process frame 337: 0.1227 seconds
Time taken to process frame 350: 0.1447 seconds
Time taken to process frame 347: 0.1246 seconds
Time taken to process frame 333: 0.0389 seconds
Time taken to process frame 344: 0.1096 seconds
Time taken to process frame 372: 0.0994 seconds
Time taken to process frame 333: 0.0305 seconds
Queue size: 0Time taken to process frame 330: 0.1258 seconds
Time taken to process frame 356: 0.0499 seconds

Time taken to process frame 345: 0.1011 seconds
Time taken to process frame 358: 0.0621 seconds
Time taken to process frame 348: 0.0315 seconds
Time taken to process frame 338: 0.0867 seconds
Time taken to process frame 351: 0.0720 seconds
Time taken to process frame 334: 0.1006 seconds
Time taken to process frame 345: 0.1582 seconds
Queue size: 2
Time taken to process frame 331: 0.0315 seconds
Time taken to process frame 373: 0.0868 seconds
Time taken to process frame 334: 0.1195 seconds
Time taken to process frame 357: 0.0958 seconds
Time taken to process frame 346: 0.0417 seconds
Time taken to process frame 349: 0.1218 seconds
Time taken to process frame 359: 0.1119 seconds
Time taken to process frame 346: 0.0312 seconds
Time taken to process frame 339: 0.0960 seconds
Queue size: 0
Time taken to process frame 352: 0.0890 seconds
Time taken to process frame 374: 0.0300 seconds
Time taken to process frame 335: 0.1118 seconds
Time taken to process frame 358: 0.0394 seconds
Time taken to process frame 332: 0.0954 seconds
Time taken to process frame 335: 0.1207 seconds
Queue size: 0
Time taken to process frame 347: 0.1015 seconds
Time taken to process frame 350: 0.1593 seconds
Time taken to process frame 360: 0.1422 seconds
Time taken to process frame 347: 0.1198 seconds
Time taken to process frame 353: 0.1033 seconds
Time taken to process frame 336: 0.0678 seconds
Time taken to process frame 359: 0.0518 seconds
Time taken to process frame 375: 0.1094 seconds
Time taken to process frame 340: 0.1536 seconds
Time taken to process frame 333: 0.0399 seconds
Time taken to process frame 348: 0.0227 seconds
Time taken to process frame 336: 0.0478 seconds
Queue size: 0
Time taken to process frame 361: 0.0233 seconds
Time taken to process frame 351: 0.0448 seconds
Time taken to process frame 348: 0.0283 seconds
Time taken to process frame 376: 0.0375 seconds
Time taken to process frame 337: 0.0929 seconds
Time taken to process frame 341: 0.0288 seconds
Time taken to process frame 354: 0.0923 seconds
Queue size: 0
Time taken to process frame 360: 0.1201 seconds
Time taken to process frame 334: 0.1091 seconds
Time taken to process frame 349: 0.1039 seconds
Time taken to process frame 337: 0.0951 seconds
Time taken to process frame 362: 0.1008 seconds
Time taken to process frame 349: 0.1009 seconds
Time taken to process frame 352: 0.1099 seconds
Time taken to process frame 338: 0.0290 seconds
Queue size: 0
Time taken to process frame 377: 0.0885 seconds
Time taken to process frame 342: 0.1065 seconds
Time taken to process frame 361: 0.0530 seconds
Time taken to process frame 338: 0.0357 seconds
Time taken to process frame 355: 0.1112 seconds
Time taken to process frame 335: 0.1118 seconds
Time taken to process frame 350: 0.1373 seconds
Time taken to process frame 353: 0.0268 seconds
Queue size: 0
Time taken to process frame 363: 0.1078 seconds
Time taken to process frame 339: 0.1076 seconds
Time taken to process frame 378: 0.0257 seconds
Time taken to process frame 350: 0.0661 seconds
Time taken to process frame 343: 0.0271 seconds
Time taken to process frame 336: 0.0360 seconds
Time taken to process frame 339: 0.0897 seconds
Time taken to process frame 356: 0.0382 seconds
Time taken to process frame 362: 0.0936 seconds
Queue size: 0
Time taken to process frame 354: 0.0769 seconds
Time taken to process frame 351: 0.0456 seconds
Time taken to process frame 364: 0.0466 seconds
Time taken to process frame 379: 0.0752 seconds
Time taken to process frame 351: 0.1184 seconds
Time taken to process frame 340: 0.1680 seconds
Time taken to process frame 344: 0.1347 seconds
Queue size: 2
Time taken to process frame 337: 0.1067 seconds
Time taken to process frame 340: 0.1549 seconds
Time taken to process frame 363: 0.0803 seconds
Time taken to process frame 357: 0.1168 seconds
Time taken to process frame 352: 0.0926 seconds
Time taken to process frame 352: 0.0410 seconds
Time taken to process frame 365: 0.1036 seconds
Time taken to process frame 355: 0.1634 seconds
Queue size: 0
Time taken to process frame 380: 0.1523 seconds
Time taken to process frame 341: 0.0310 seconds
Time taken to process frame 338: 0.0669 seconds
Time taken to process frame 341: 0.1258 seconds
Time taken to process frame 345: 0.1176 seconds
Time taken to process frame 364: 0.0981 seconds
Time taken to process frame 356: 0.0610 seconds
Time taken to process frame 353: 0.0887 seconds
Time taken to process frame 353: 0.0699 seconds
Queue size: 0
Time taken to process frame 358: 0.1623 seconds
Time taken to process frame 381: 0.1149 seconds
Time taken to process frame 366: 0.1466 seconds
Queue size: 0
Time taken to process frame 342: 0.2374 seconds
Time taken to process frame 346: 0.1795 seconds
Time taken to process frame 339: 0.2806 seconds
Time taken to process frame 359: 0.1359 seconds
Queue size: 0
Time taken to process frame 357: 0.3459 seconds
Time taken to process frame 367: 0.1885 seconds
Time taken to process frame 343: 0.1690 seconds
Time taken to process frame 354: 0.3072 seconds
Time taken to process frame 342: 0.4365 seconds
Time taken to process frame 358: 0.0750 seconds
Time taken to process frame 347: 0.2430 seconds
Time taken to process frame 354: 0.4588 seconds
Time taken to process frame 382: 0.3609 seconds
Time taken to process frame 368: 0.1480 seconds
Time taken to process frame 340: 0.3155 seconds
Queue size: 0
Time taken to process frame 365: 0.5072 seconds
Time taken to process frame 344: 0.1900 seconds
Time taken to process frame 343: 0.1811 seconds
Time taken to process frame 359: 0.1781 seconds
Time taken to process frame 360: 0.3930 seconds
Time taken to process frame 383: 0.1156 seconds
Time taken to process frame 348: 0.1987 seconds
Time taken to process frame 355: 0.1955 seconds
Queue size: 0
Time taken to process frame 384: 0.1108 seconds
Time taken to process frame 369: 0.1338 seconds
Time taken to process frame 355: 0.3807 seconds
Time taken to process frame 341: 0.1403 seconds
Time taken to process frame 385: 0.1434 seconds
Time taken to process frame 356: 0.1155 seconds
Time taken to process frame 361: 0.2702 seconds
Queue size: 0
Time taken to process frame 344: 0.2772 seconds
Time taken to process frame 366: 0.2779 seconds
Time taken to process frame 345: 0.2509 seconds
Time taken to process frame 370: 0.2370 seconds
Time taken to process frame 357: 0.1336 seconds
Time taken to process frame 356: 0.1577 seconds
Time taken to process frame 342: 0.0975 seconds
Time taken to process frame 362: 0.1062 seconds
Queue size: 0
Time taken to process frame 349: 0.1441 seconds
Time taken to process frame 367: 0.1126 seconds
Time taken to process frame 357: 0.0460 seconds
Time taken to process frame 346: 0.1268 seconds
Time taken to process frame 345: 0.1968 seconds
Time taken to process frame 386: 0.1776 seconds
Time taken to process frame 343: 0.1035 seconds
Time taken to process frame 371: 0.1779 seconds
Time taken to process frame 360: 0.2892 seconds
Time taken to process frame 346: 0.0389 seconds
Queue size: 0
Time taken to process frame 368: 0.1088 seconds
Time taken to process frame 363: 0.1714 seconds
Time taken to process frame 358: 0.2456 seconds
Time taken to process frame 350: 0.1866 seconds
Time taken to process frame 361: 0.0752 seconds
Time taken to process frame 358: 0.1614 seconds
Time taken to process frame 344: 0.1569 seconds
Time taken to process frame 372: 0.1630 seconds
Time taken to process frame 387: 0.0737 seconds
Time taken to process frame 347: 0.2417 seconds
Queue size: 0
Time taken to process frame 347: 0.1601 seconds
Time taken to process frame 369: 0.1371 seconds
Time taken to process frame 359: 0.1316 seconds
Time taken to process frame 359: 0.0725 seconds
Time taken to process frame 364: 0.0410 seconds
Time taken to process frame 362: 0.1101 seconds
Time taken to process frame 351: 0.0341 seconds
Time taken to process frame 373: 0.0323 seconds
Queue size: 0
Time taken to process frame 348: 0.0410 seconds
Time taken to process frame 388: 0.0860 seconds
Time taken to process frame 345: 0.1273 seconds
Time taken to process frame 348: 0.0423 seconds
Time taken to process frame 370: 0.1375 seconds
Time taken to process frame 363: 0.0910 seconds
Time taken to process frame 360: 0.1352 seconds
Queue size: 0
Time taken to process frame 352: 0.1174 seconds
Time taken to process frame 365: 0.1235 seconds
Time taken to process frame 360: 0.1925 seconds
Time taken to process frame 389: 0.0997 seconds
Time taken to process frame 374: 0.1278 seconds
Time taken to process frame 346: 0.0415 seconds
Time taken to process frame 349: 0.1117 seconds
Time taken to process frame 349: 0.0840 seconds
Time taken to process frame 371: 0.0855 seconds
Queue size: 0
Time taken to process frame 361: 0.0665 seconds
Time taken to process frame 364: 0.1050 seconds
Time taken to process frame 353: 0.0678 seconds
Time taken to process frame 366: 0.0695 seconds
Time taken to process frame 361: 0.0412 seconds
Time taken to process frame 390: 0.1133 seconds
Time taken to process frame 347: 0.1150 seconds
Queue size: 0
Time taken to process frame 375: 0.2111 seconds
Time taken to process frame 372: 0.1286 seconds
Time taken to process frame 350: 0.1261 seconds
Time taken to process frame 350: 0.2057 seconds
Time taken to process frame 362: 0.1252 seconds
Time taken to process frame 365: 0.1232 seconds
Time taken to process frame 354: 0.0962 seconds
Time taken to process frame 391: 0.0309 seconds
Time taken to process frame 367: 0.1003 seconds
Time taken to process frame 362: 0.1037 seconds
Queue size: 0
Time taken to process frame 376: 0.0622 seconds
Time taken to process frame 348: 0.0907 seconds
Time taken to process frame 373: 0.0893 seconds
Time taken to process frame 351: 0.0967 seconds
Time taken to process frame 351: 0.0890 seconds
Time taken to process frame 366: 0.0374 seconds
Time taken to process frame 363: 0.0884 seconds
Time taken to process frame 368: 0.0345 seconds
Time taken to process frame 355: 0.1199 seconds
Queue size: 0
Time taken to process frame 363: 0.0386 seconds
Time taken to process frame 392: 0.1074 seconds
Time taken to process frame 377: 0.1035 seconds
Time taken to process frame 349: 0.0902 seconds
Time taken to process frame 374: 0.1035 seconds
Time taken to process frame 367: 0.0953 seconds
Queue size: 0
Time taken to process frame 352: 0.0950 seconds
Time taken to process frame 364: 0.0311 seconds
Time taken to process frame 369: 0.0786 seconds
Time taken to process frame 352: 0.0571 seconds
Time taken to process frame 356: 0.0985 seconds
Time taken to process frame 393: 0.0360 seconds
Time taken to process frame 364: 0.0997 seconds
Time taken to process frame 378: 0.0691 seconds
Time taken to process frame 368: 0.0338 seconds
Queue size: 0
Time taken to process frame 375: 0.1201 seconds
Time taken to process frame 350: 0.0894 seconds
Time taken to process frame 365: 0.1124 seconds
Time taken to process frame 370: 0.1064 seconds
Time taken to process frame 353: 0.0924 seconds
Time taken to process frame 353: 0.0987 seconds
Time taken to process frame 394: 0.1017 seconds
Queue size: 0
Time taken to process frame 379: 0.0277 seconds
Time taken to process frame 357: 0.0829 seconds
Time taken to process frame 365: 0.1075 seconds
Time taken to process frame 376: 0.0296 seconds
Time taken to process frame 369: 0.0954 seconds
Time taken to process frame 366: 0.0340 seconds
Time taken to process frame 351: 0.0846 seconds
Time taken to process frame 371: 0.0366 seconds
Time taken to process frame 354: 0.0405 seconds
Time taken to process frame 354: 0.0285 seconds
Queue size: 0
Time taken to process frame 358: 0.0539 seconds
Time taken to process frame 395: 0.1151 seconds
Time taken to process frame 380: 0.1016 secondsTime taken to process frame 366: 0.0611 seconds

Time taken to process frame 377: 0.1061 seconds
Queue size: 0
Time taken to process frame 370: 0.1239 seconds
Time taken to process frame 352: 0.0390 seconds
Time taken to process frame 367: 0.1077 seconds
Time taken to process frame 372: 0.0921 seconds
Time taken to process frame 355: 0.0824 seconds
Time taken to process frame 355: 0.0833 seconds
Time taken to process frame 396: 0.0708 seconds
Time taken to process frame 381: 0.0531 seconds
Time taken to process frame 359: 0.0962 seconds
Queue size: 0
Time taken to process frame 367: 0.0935 seconds
Time taken to process frame 371: 0.0319 seconds
Time taken to process frame 378: 0.0889 seconds
Time taken to process frame 368: 0.0584 seconds
Time taken to process frame 373: 0.0310 seconds
Time taken to process frame 356: 0.0264 seconds
Time taken to process frame 353: 0.0779 seconds
Time taken to process frame 356: 0.0324 seconds
Queue size: 0
Time taken to process frame 397: 0.1096 seconds
Time taken to process frame 382: 0.1078 seconds
Time taken to process frame 368: 0.0998 seconds
Time taken to process frame 360: 0.1509 seconds
Time taken to process frame 372: 0.1052 seconds
Time taken to process frame 379: 0.1086 seconds
Time taken to process frame 369: 0.0998 seconds
Queue size: 0
Time taken to process frame 374: 0.1144 seconds
Time taken to process frame 357: 0.0941 seconds
Time taken to process frame 354: 0.1025 seconds
Time taken to process frame 357: 0.0967 seconds
Time taken to process frame 398: 0.1028 seconds
Time taken to process frame 383: 0.0869 seconds
Time taken to process frame 361: 0.0909 seconds
Time taken to process frame 369: 0.0879 seconds
Time taken to process frame 373: 0.0484 seconds
Queue size: 1
Time taken to process frame 380: 0.0760 seconds
Time taken to process frame 370: 0.1406 seconds
Time taken to process frame 375: 0.1331 seconds
Time taken to process frame 358: 0.1180 seconds
Time taken to process frame 355: 0.1100 seconds
Time taken to process frame 358: 0.0840 seconds
Time taken to process frame 384: 0.0410 seconds
Time taken to process frame 399: 0.0931 seconds
Queue size: 0
Time taken to process frame 362: 0.0841 seconds
Time taken to process frame 374: 0.0961 seconds
Time taken to process frame 370: 0.0825 seconds
Time taken to process frame 381: 0.0885 seconds
Time taken to process frame 371: 0.1005 seconds
Time taken to process frame 376: 0.0925 seconds
Queue size: 0
Time taken to process frame 356: 0.0950 seconds
Time taken to process frame 359: 0.0985 seconds
Time taken to process frame 400: 0.1425 seconds
Time taken to process frame 359: 0.1040 seconds
Time taken to process frame 363: 0.0605 seconds
Time taken to process frame 371: 0.0300 seconds
Time taken to process frame 385: 0.1146 seconds
Time taken to process frame 372: 0.0290 seconds
Time taken to process frame 375: 0.0921 seconds
Time taken to process frame 382: 0.0300 seconds
Time taken to process frame 357: 0.0310 seconds
Queue size: 1
Time taken to process frame 377: 0.0276 seconds
Time taken to process frame 401: 0.0327 seconds
Time taken to process frame 360: 0.1092 seconds
Time taken to process frame 386: 0.0275 seconds
Time taken to process frame 364: 0.0854 seconds
Queue size: 0
Time taken to process frame 360: 0.1206 seconds
Time taken to process frame 372: 0.0916 seconds
Time taken to process frame 376: 0.0717 seconds
Time taken to process frame 373: 0.1194 seconds
Time taken to process frame 358: 0.1349 seconds
Time taken to process frame 383: 0.1014 seconds
Time taken to process frame 378: 0.0961 seconds
Time taken to process frame 361: 0.0685 seconds
Time taken to process frame 402: 0.1012 seconds
Queue size: 0
Time taken to process frame 387: 0.0944 seconds
Time taken to process frame 373: 0.0678 seconds
Time taken to process frame 365: 0.1178 seconds
Time taken to process frame 377: 0.1048 seconds
Time taken to process frame 361: 0.1314 seconds
Time taken to process frame 374: 0.0886 seconds
Time taken to process frame 359: 0.0771 seconds
Queue size: 0
Time taken to process frame 379: 0.0739 seconds
Time taken to process frame 384: 0.1498 seconds
Time taken to process frame 366: 0.0752 seconds
Time taken to process frame 403: 0.1270 seconds
Time taken to process frame 388: 0.1145 seconds
Time taken to process frame 362: 0.1532 seconds
Queue size: 0
Time taken to process frame 362: 0.1233 seconds
Time taken to process frame 374: 0.1701 seconds
Time taken to process frame 367: 0.0400 seconds
Time taken to process frame 380: 0.1218 seconds
Time taken to process frame 385: 0.1057 seconds
Time taken to process frame 378: 0.2739 seconds
Queue size: 0
Time taken to process frame 389: 0.1401 seconds
Time taken to process frame 375: 0.2936 seconds
Time taken to process frame 360: 0.2579 seconds
Time taken to process frame 404: 0.1532 seconds
Time taken to process frame 386: 0.0275 seconds
Time taken to process frame 381: 0.1705 seconds
Queue size: 0
Time taken to process frame 379: 0.1540 seconds
Time taken to process frame 376: 0.1435 seconds
Time taken to process frame 363: 0.2506 seconds
Time taken to process frame 361: 0.1335 seconds
Time taken to process frame 368: 0.3560 seconds
Time taken to process frame 387: 0.2061 seconds
Time taken to process frame 377: 0.1059 seconds
Time taken to process frame 363: 0.4584 seconds
Queue size: 3
Time taken to process frame 369: 0.0660 seconds
Time taken to process frame 362: 0.1101 seconds
Time taken to process frame 375: 0.5686 seconds
Time taken to process frame 382: 0.3538 seconds
Time taken to process frame 370: 0.1116 seconds
Time taken to process frame 364: 0.2738 seconds
Queue size: 0
Time taken to process frame 388: 0.2882 seconds
Time taken to process frame 405: 0.5859 seconds
Time taken to process frame 390: 0.4630 seconds
Time taken to process frame 376: 0.2777 seconds
Queue size: 0
Time taken to process frame 377: 0.0626 seconds
Queue size: 0
Time taken to process frame 406: 0.2416 seconds
Time taken to process frame 391: 0.2793 seconds
Time taken to process frame 365: 0.5225 seconds
Time taken to process frame 380: 0.8888 seconds
Time taken to process frame 378: 0.8022 seconds
Queue size: 0
Time taken to process frame 378: 0.3163 seconds
Time taken to process frame 364: 0.8359 seconds
Time taken to process frame 381: 0.1146 seconds
Time taken to process frame 379: 0.0960 seconds
Time taken to process frame 382: 0.1060 seconds
Queue size: 0
Time taken to process frame 407: 0.3949 seconds
Time taken to process frame 392: 0.4079 seconds
Time taken to process frame 383: 0.8740 seconds
Time taken to process frame 379: 0.3026 seconds
Time taken to process frame 389: 0.8476 seconds
Time taken to process frame 383: 0.1508 seconds
Queue size: 0
Time taken to process frame 365: 0.3653 seconds
Time taken to process frame 384: 0.0949 seconds
Time taken to process frame 384: 0.0883 seconds
Time taken to process frame 408: 0.2915 seconds
Time taken to process frame 380: 0.4681 seconds
Time taken to process frame 366: 0.6878 seconds
Time taken to process frame 366: 0.1720 seconds
Queue size: 2
Time taken to process frame 390: 0.3491 seconds
Time taken to process frame 381: 0.1735 seconds
Time taken to process frame 371: 1.4475 seconds
Time taken to process frame 393: 0.5396 seconds
Queue size: 3
Time taken to process frame 363: 1.5710 seconds
Time taken to process frame 409: 0.3303 seconds
Time taken to process frame 380: 0.5337 seconds
Time taken to process frame 367: 0.2597 seconds
Time taken to process frame 385: 0.4168 seconds
Time taken to process frame 367: 0.3179 seconds
Time taken to process frame 385: 0.5280 seconds
Time taken to process frame 382: 0.2064 seconds
Time taken to process frame 394: 0.1921 seconds
Queue size: 0
Time taken to process frame 383: 0.0518 seconds
Time taken to process frame 381: 0.1430 seconds
Time taken to process frame 364: 0.2124 seconds
Time taken to process frame 384: 0.1167 seconds
Time taken to process frame 386: 0.2882 seconds
Time taken to process frame 382: 0.1682 secondsQueue size: 2

Time taken to process frame 368: 0.2233 seconds
Time taken to process frame 365: 0.2094 seconds
Time taken to process frame 395: 0.2573 seconds
Time taken to process frame 372: 0.5031 seconds
Time taken to process frame 410: 0.4575 seconds
Time taken to process frame 391: 0.6247 seconds
Time taken to process frame 368: 0.4508 seconds
Queue size: 0
Time taken to process frame 366: 0.1370 seconds
Time taken to process frame 396: 0.1239 seconds
Time taken to process frame 369: 0.1952 seconds
Time taken to process frame 411: 0.1378 seconds
Time taken to process frame 373: 0.1868 seconds
Time taken to process frame 392: 0.1825 seconds
Time taken to process frame 367: 0.1029 seconds
Time taken to process frame 387: 0.3371 seconds
Time taken to process frame 385: 0.4232 seconds
Time taken to process frame 369: 0.2147 seconds
Time taken to process frame 412: 0.1175 seconds
Queue size: 0
Time taken to process frame 368: 0.0805 seconds
Time taken to process frame 393: 0.1010 seconds
Time taken to process frame 394: 0.0710 seconds
Time taken to process frame 397: 0.2943 seconds
Time taken to process frame 369: 0.0815 seconds
Time taken to process frame 374: 0.2453 seconds
Time taken to process frame 383: 0.5490 seconds
Queue size: 0
Time taken to process frame 388: 0.1570 seconds
Time taken to process frame 370: 0.1017 seconds
Time taken to process frame 395: 0.1613 seconds
Time taken to process frame 413: 0.2705 seconds
Time taken to process frame 398: 0.1613 seconds
Time taken to process frame 370: 0.4865 seconds
Time taken to process frame 386: 0.3680 seconds
Time taken to process frame 414: 0.0365 seconds
Time taken to process frame 386: 1.0219 seconds
Time taken to process frame 371: 0.1185 seconds
Time taken to process frame 384: 0.1903 seconds
Time taken to process frame 370: 0.3974 seconds
Queue size: 2
Time taken to process frame 396: 0.1173 seconds
Time taken to process frame 389: 0.1673 seconds
Time taken to process frame 375: 0.2376 seconds
Time taken to process frame 399: 0.0943 seconds
Time taken to process frame 397: 0.0615 seconds
Time taken to process frame 387: 0.1559 seconds
Time taken to process frame 398: 0.0508 seconds
Queue size: 0
Time taken to process frame 376: 0.1094 seconds
Time taken to process frame 387: 0.2239 seconds
Time taken to process frame 372: 0.1866 seconds
Time taken to process frame 400: 0.1932 seconds
Time taken to process frame 388: 0.1147 seconds
Time taken to process frame 373: 0.0420 seconds
Time taken to process frame 371: 0.1682 seconds
Time taken to process frame 399: 0.1099 seconds
Time taken to process frame 385: 0.3337 seconds
Time taken to process frame 388: 0.1374 seconds
Time taken to process frame 415: 0.2820 seconds
Time taken to process frame 401: 0.1108 seconds
Time taken to process frame 371: 0.4579 seconds
Queue size: 4
Time taken to process frame 416: 0.0619 seconds
Time taken to process frame 402: 0.1054 seconds
Time taken to process frame 386: 0.1902 seconds
Time taken to process frame 389: 0.1892 seconds
Time taken to process frame 372: 0.1695 seconds
Time taken to process frame 389: 0.2562 seconds
Time taken to process frame 417: 0.1276 seconds
Queue size: 0
Time taken to process frame 374: 0.3227 seconds
Time taken to process frame 390: 0.2919 seconds
Time taken to process frame 387: 0.1725 seconds
Time taken to process frame 377: 0.2869 seconds
Time taken to process frame 418: 0.1301 seconds
Time taken to process frame 400: 0.2958 seconds
Time taken to process frame 375: 0.1399 seconds
Queue size: 1
Time taken to process frame 403: 0.3133 seconds
Time taken to process frame 401: 0.0493 seconds
Time taken to process frame 390: 0.2701 seconds
Time taken to process frame 373: 0.2871 seconds
Time taken to process frame 391: 0.1671 seconds
Time taken to process frame 419: 0.1208 seconds
Time taken to process frame 388: 0.1798 seconds
Time taken to process frame 376: 0.1150 seconds
Time taken to process frame 390: 0.3880 seconds
Time taken to process frame 404: 0.1195 seconds
Time taken to process frame 391: 0.1185 seconds
Time taken to process frame 378: 0.2306 seconds
Time taken to process frame 374: 0.1076 seconds
Queue size: 4
Time taken to process frame 402: 0.1853 seconds
Time taken to process frame 392: 0.1661 seconds
Time taken to process frame 377: 0.1337 seconds
Time taken to process frame 389: 0.1885 seconds
Time taken to process frame 392: 0.1836 seconds
Time taken to process frame 405: 0.2029 seconds
Time taken to process frame 372: 0.1047 seconds
Queue size: 0
Time taken to process frame 403: 0.1478 seconds
Time taken to process frame 379: 0.2885 seconds
Time taken to process frame 393: 0.1532 seconds
Time taken to process frame 393: 0.2074 seconds
Queue size: 0
Time taken to process frame 375: 0.3349 seconds
Time taken to process frame 391: 0.3580 seconds
Time taken to process frame 420: 0.4943 seconds
Time taken to process frame 373: 0.2140 seconds
Time taken to process frame 394: 0.1123 seconds
Time taken to process frame 406: 0.2369 seconds
Time taken to process frame 394: 0.1013 seconds
Time taken to process frame 404: 0.1902 seconds
Time taken to process frame 378: 0.3543 seconds
Time taken to process frame 380: 0.2343 seconds
Time taken to process frame 376: 0.1580 seconds
Time taken to process frame 392: 0.1469 seconds
Queue size: 0
Time taken to process frame 390: 0.4327 seconds
Time taken to process frame 407: 0.1268 seconds
Time taken to process frame 374: 0.2927 seconds
Queue size: 0
Time taken to process frame 381: 0.1704 seconds
Time taken to process frame 405: 0.2257 seconds
Time taken to process frame 395: 0.2564 seconds
Time taken to process frame 379: 0.2250 seconds
Time taken to process frame 421: 0.3370 seconds
Time taken to process frame 406: 0.0612 seconds
Time taken to process frame 377: 0.2443 seconds
Time taken to process frame 391: 0.2348 seconds
Time taken to process frame 393: 0.2622 seconds
Time taken to process frame 396: 0.1283 seconds
Queue size: 0
Time taken to process frame 407: 0.0998 seconds
Time taken to process frame 395: 0.5542 seconds
Time taken to process frame 392: 0.0974 seconds
Time taken to process frame 408: 0.3012 seconds
Time taken to process frame 382: 0.2856 seconds
Time taken to process frame 422: 0.2115 seconds
Time taken to process frame 397: 0.1354 seconds
Time taken to process frame 394: 0.1814 seconds
Time taken to process frame 375: 0.3890 seconds
Queue size: 0
Time taken to process frame 396: 0.1708 seconds
Time taken to process frame 393: 0.1691 seconds
Time taken to process frame 380: 0.4223 seconds
Time taken to process frame 383: 0.0688 seconds
Time taken to process frame 409: 0.1849 seconds
Time taken to process frame 408: 0.2815 seconds
Time taken to process frame 409: 0.0331 seconds
Queue size: 0
Time taken to process frame 394: 0.2021 seconds
Time taken to process frame 384: 0.1919 seconds
Time taken to process frame 378: 0.2389 seconds
Time taken to process frame 397: 0.2628 seconds
Time taken to process frame 398: 0.3310 seconds
Time taken to process frame 423: 0.3663 seconds
Time taken to process frame 410: 0.1790 seconds
Time taken to process frame 381: 0.2688 seconds
Time taken to process frame 376: 0.2435 seconds
Queue size: 0
Time taken to process frame 424: 0.0338 seconds
Time taken to process frame 411: 0.0280 seconds
Time taken to process frame 410: 0.3125 seconds
Time taken to process frame 379: 0.1205 seconds
Time taken to process frame 395: 0.2300 seconds
Time taken to process frame 411: 0.0585 seconds
Time taken to process frame 382: 0.1420 seconds
Time taken to process frame 398: 0.2524 secondsTime taken to process frame 377: 0.1612 seconds

Time taken to process frame 395: 0.3167 seconds
Queue size: 6
Time taken to process frame 399: 0.2691 seconds
Time taken to process frame 412: 0.1202 seconds
Time taken to process frame 380: 0.1947 seconds
Time taken to process frame 412: 0.2386 seconds
Time taken to process frame 385: 0.4254 seconds
Time taken to process frame 399: 0.1004 seconds
Time taken to process frame 396: 0.0790 seconds
Time taken to process frame 425: 0.2921 seconds
Time taken to process frame 396: 0.2414 seconds
Time taken to process frame 383: 0.2243 seconds
Queue size: 0
Time taken to process frame 413: 0.1041 seconds
Time taken to process frame 378: 0.2573 seconds
Time taken to process frame 400: 0.2292 seconds
Time taken to process frame 426: 0.1878 seconds
Time taken to process frame 386: 0.2331 seconds
Time taken to process frame 397: 0.1836 seconds
Time taken to process frame 413: 0.2367 seconds
Queue size: 3
Time taken to process frame 381: 0.1785 seconds
Time taken to process frame 414: 0.1349 seconds
Time taken to process frame 400: 0.2068 seconds
Time taken to process frame 397: 0.2099 seconds
Time taken to process frame 398: 0.0962 seconds
Time taken to process frame 384: 0.2184 seconds
Time taken to process frame 401: 0.1965 seconds
Time taken to process frame 387: 0.1208 seconds
Time taken to process frame 401: 0.0617 seconds
Time taken to process frame 414: 0.1363 seconds
Time taken to process frame 379: 0.2933 seconds
Time taken to process frame 398: 0.0857 seconds
Time taken to process frame 415: 0.1329 seconds
Queue size: 4
Time taken to process frame 427: 0.2494 seconds
Time taken to process frame 399: 0.1505 seconds
Time taken to process frame 382: 0.2380 seconds
Time taken to process frame 402: 0.1495 seconds
Time taken to process frame 388: 0.1403 seconds
Time taken to process frame 416: 0.0495 seconds
Queue size: 0
Time taken to process frame 399: 0.2114 seconds
Time taken to process frame 383: 0.0775 seconds
Time taken to process frame 389: 0.0646 seconds
Time taken to process frame 428: 0.1866 seconds
Time taken to process frame 385: 0.2438 seconds
Time taken to process frame 380: 0.2473 seconds
Time taken to process frame 417: 0.1160 seconds
Time taken to process frame 403: 0.1786 seconds
Time taken to process frame 415: 0.2342 seconds
Queue size: 0
Time taken to process frame 418: 0.0808 seconds
Time taken to process frame 402: 0.2381 seconds
Time taken to process frame 384: 0.1610 seconds
Time taken to process frame 400: 0.3389 seconds
Time taken to process frame 429: 0.1853 seconds
Time taken to process frame 386: 0.1008 seconds
Time taken to process frame 381: 0.2029 seconds
Time taken to process frame 400: 0.2599 seconds
Time taken to process frame 404: 0.1714 seconds
Time taken to process frame 416: 0.1903 seconds
Time taken to process frame 390: 0.1275 seconds
Queue size: 0
Time taken to process frame 403: 0.1720 seconds
Time taken to process frame 419: 0.2664 seconds
Time taken to process frame 387: 0.1596 seconds
Time taken to process frame 401: 0.2056 seconds
Time taken to process frame 417: 0.1571 seconds
Time taken to process frame 382: 0.1471 seconds
Time taken to process frame 401: 0.2029 seconds
Time taken to process frame 385: 0.3055 seconds
Time taken to process frame 391: 0.1834 seconds
Time taken to process frame 404: 0.1506 seconds
Queue size: 3
Time taken to process frame 430: 0.2945 seconds
Time taken to process frame 383: 0.1166 seconds
Time taken to process frame 420: 0.1995 seconds
Time taken to process frame 402: 0.1857 seconds
Time taken to process frame 418: 0.1830 seconds
Time taken to process frame 386: 0.1434 seconds
Time taken to process frame 405: 0.3872 seconds
Time taken to process frame 431: 0.0734 seconds
Time taken to process frame 402: 0.2192 seconds
Queue size: 0
Time taken to process frame 388: 0.1107 seconds
Time taken to process frame 384: 0.1513 seconds
Time taken to process frame 392: 0.2096 seconds
Time taken to process frame 405: 0.2674 seconds
Time taken to process frame 421: 0.1315 seconds
Time taken to process frame 403: 0.1103 seconds
Time taken to process frame 419: 0.1129 seconds
Time taken to process frame 406: 0.0900 seconds
Time taken to process frame 387: 0.0960 seconds
Time taken to process frame 403: 0.0494 seconds
Queue size: 0
Time taken to process frame 432: 0.0984 seconds
Time taken to process frame 393: 0.0545 seconds
Time taken to process frame 389: 0.0880 seconds
Time taken to process frame 406: 0.0770 seconds
Time taken to process frame 422: 0.1061 seconds
Time taken to process frame 385: 0.1687 seconds
Time taken to process frame 407: 0.0351 seconds
Time taken to process frame 404: 0.0990 seconds
Queue size: 0
Time taken to process frame 404: 0.0362 seconds
Time taken to process frame 388: 0.0797 seconds
Time taken to process frame 420: 0.1605 seconds
Time taken to process frame 433: 0.0603 seconds
Time taken to process frame 394: 0.1018 seconds
Time taken to process frame 423: 0.0675 seconds
Time taken to process frame 407: 0.1035 seconds
Queue size: 0
Time taken to process frame 408: 0.0979 seconds
Time taken to process frame 386: 0.1021 seconds
Time taken to process frame 390: 0.1909 seconds
Time taken to process frame 405: 0.1351 seconds
Time taken to process frame 421: 0.0665 seconds
Time taken to process frame 389: 0.1055 seconds
Time taken to process frame 405: 0.1628 seconds
Queue size: 0
Time taken to process frame 434: 0.0914 seconds
Time taken to process frame 395: 0.1246 seconds
Time taken to process frame 424: 0.0890 seconds
Time taken to process frame 408: 0.0904 seconds
Time taken to process frame 409: 0.0836 seconds
Time taken to process frame 387: 0.0934 seconds
Time taken to process frame 391: 0.0891 seconds
Time taken to process frame 422: 0.0957 seconds
Queue size: 0
Time taken to process frame 406: 0.0823 seconds
Time taken to process frame 406: 0.1338 seconds
Time taken to process frame 396: 0.0738 seconds
Time taken to process frame 388: 0.0552 seconds
Time taken to process frame 425: 0.1720 seconds
Time taken to process frame 390: 0.2513 seconds
Time taken to process frame 435: 0.2329 seconds
Queue size: 0
Time taken to process frame 409: 0.1765 seconds
Time taken to process frame 410: 0.1760 seconds
Time taken to process frame 392: 0.1249 seconds
Time taken to process frame 407: 0.0575 seconds
Time taken to process frame 423: 0.0985 seconds
Time taken to process frame 407: 0.1220 seconds
Time taken to process frame 426: 0.0466 seconds
Time taken to process frame 397: 0.1106 seconds
Time taken to process frame 436: 0.0222 seconds
Time taken to process frame 391: 0.0436 seconds
Time taken to process frame 389: 0.1077 seconds
Time taken to process frame 411: 0.0331 seconds
Queue size: 0
Time taken to process frame 393: 0.0440 seconds
Time taken to process frame 408: 0.0878 seconds
Time taken to process frame 410: 0.1138 seconds
Time taken to process frame 408: 0.0545 seconds
Time taken to process frame 424: 0.0988 seconds
Time taken to process frame 398: 0.0300 seconds
Time taken to process frame 427: 0.0909 seconds
Queue size: 0
Time taken to process frame 392: 0.0804 seconds
Time taken to process frame 437: 0.0755 seconds
Time taken to process frame 409: 0.0290 seconds
Time taken to process frame 412: 0.0881 seconds
Time taken to process frame 390: 0.1082 seconds
Time taken to process frame 394: 0.0868 seconds
Time taken to process frame 411: 0.0428 seconds
Queue size: 0
Time taken to process frame 428: 0.0300 seconds
Time taken to process frame 409: 0.0965 seconds
Time taken to process frame 425: 0.1228 seconds
Time taken to process frame 393: 0.0290 seconds
Time taken to process frame 399: 0.0695 seconds
Time taken to process frame 438: 0.0420 seconds
Time taken to process frame 391: 0.0231 seconds
Time taken to process frame 410: 0.0946 seconds
Time taken to process frame 413: 0.0290 seconds
Time taken to process frame 412: 0.0292 seconds
Queue size: 0
Time taken to process frame 395: 0.1385 seconds
Time taken to process frame 429: 0.0929 seconds
Time taken to process frame 426: 0.0575 seconds
Time taken to process frame 394: 0.0840 seconds
Time taken to process frame 410: 0.1046 seconds
Time taken to process frame 400: 0.1177 seconds
Queue size: 0
Time taken to process frame 439: 0.1147 seconds
Time taken to process frame 392: 0.0908 seconds
Time taken to process frame 414: 0.1048 seconds
Time taken to process frame 396: 0.0320 seconds
Time taken to process frame 411: 0.0848 seconds
Time taken to process frame 413: 0.1043 seconds
Time taken to process frame 411: 0.0372 seconds
Time taken to process frame 430: 0.1100 seconds
Time taken to process frame 395: 0.1097 seconds
Time taken to process frame 401: 0.0452 seconds
Queue size: 2
Time taken to process frame 427: 0.0900 seconds
Time taken to process frame 393: 0.0499 seconds
Time taken to process frame 412: 0.1295 seconds
Time taken to process frame 397: 0.1087 seconds
Time taken to process frame 414: 0.0778 seconds
Time taken to process frame 440: 0.1936 seconds
Queue size: 0
Time taken to process frame 415: 0.1727 seconds
Time taken to process frame 431: 0.1082 seconds
Time taken to process frame 412: 0.1352 seconds
Time taken to process frame 402: 0.1060 seconds
Time taken to process frame 396: 0.1039 seconds
Time taken to process frame 413: 0.0565 seconds
Time taken to process frame 398: 0.0465 seconds
Time taken to process frame 428: 0.1275 seconds
Time taken to process frame 394: 0.1303 seconds
Time taken to process frame 441: 0.0449 seconds
Queue size: 0
Time taken to process frame 415: 0.0794 seconds
Time taken to process frame 416: 0.0740 seconds
Time taken to process frame 432: 0.0792 seconds
Time taken to process frame 413: 0.0737 seconds
Time taken to process frame 403: 0.0823 seconds
Time taken to process frame 429: 0.0280 seconds
Time taken to process frame 397: 0.0878 seconds
Time taken to process frame 414: 0.1016 seconds
Queue size: 0
Time taken to process frame 399: 0.0766 seconds
Time taken to process frame 442: 0.1125 seconds
Time taken to process frame 416: 0.1061 seconds
Time taken to process frame 395: 0.1801 seconds
Time taken to process frame 417: 0.1235 seconds
Time taken to process frame 433: 0.0990 seconds
Time taken to process frame 414: 0.1032 seconds
Time taken to process frame 398: 0.0442 seconds
Time taken to process frame 404: 0.0900 seconds
Queue size: 0
Time taken to process frame 430: 0.0900 seconds
Time taken to process frame 443: 0.0714 seconds
Time taken to process frame 415: 0.1132 seconds
Time taken to process frame 418: 0.0488 seconds
Time taken to process frame 417: 0.0968 seconds
Time taken to process frame 400: 0.1741 seconds
Time taken to process frame 396: 0.0782 seconds
Queue size: 0
Time taken to process frame 434: 0.1077 seconds
Time taken to process frame 399: 0.0957 seconds
Time taken to process frame 431: 0.0850 seconds
Time taken to process frame 444: 0.1004 seconds
Time taken to process frame 416: 0.0976 seconds
Time taken to process frame 418: 0.0875 seconds
Queue size: 2
Time taken to process frame 419: 0.1136 seconds
Time taken to process frame 415: 0.1892 seconds
Time taken to process frame 405: 0.2527 seconds
Time taken to process frame 401: 0.1227 seconds
Time taken to process frame 397: 0.1222 seconds
Time taken to process frame 435: 0.1296 seconds
Time taken to process frame 432: 0.1185 seconds
Time taken to process frame 400: 0.1661 seconds
Queue size: 0
Time taken to process frame 417: 0.1317 seconds
Time taken to process frame 445: 0.1772 seconds
Time taken to process frame 406: 0.1467 seconds
Time taken to process frame 402: 0.1262 seconds
Time taken to process frame 416: 0.2108 seconds
Time taken to process frame 420: 0.2007 seconds
Time taken to process frame 436: 0.0489 seconds
Time taken to process frame 398: 0.1224 seconds
Time taken to process frame 433: 0.0627 seconds
Time taken to process frame 419: 0.1276 seconds
Time taken to process frame 401: 0.0668 seconds
Time taken to process frame 418: 0.0517 seconds
Queue size: 4
Time taken to process frame 403: 0.0370 seconds
Time taken to process frame 446: 0.0607 seconds
Time taken to process frame 417: 0.0306 seconds
Time taken to process frame 421: 0.0301 seconds
Time taken to process frame 437: 0.0782 seconds
Time taken to process frame 399: 0.0834 seconds
Time taken to process frame 420: 0.1056 seconds
Queue size: 0
Time taken to process frame 434: 0.0908 seconds
Time taken to process frame 402: 0.1178 seconds
Time taken to process frame 419: 0.0941 seconds
Time taken to process frame 407: 0.1053 seconds
Time taken to process frame 447: 0.1000 seconds
Time taken to process frame 404: 0.1067 seconds
Time taken to process frame 418: 0.0857 seconds
Time taken to process frame 438: 0.0513 seconds
Time taken to process frame 422: 0.0834 seconds
Queue size: 0
Time taken to process frame 421: 0.0261 seconds
Time taken to process frame 403: 0.0320 seconds
Time taken to process frame 400: 0.1121 seconds
Time taken to process frame 435: 0.1080 seconds
Time taken to process frame 408: 0.0410 seconds
Time taken to process frame 448: 0.0302 seconds
Time taken to process frame 419: 0.0264 seconds
Time taken to process frame 420: 0.1094 seconds
Queue size: 0
Time taken to process frame 423: 0.0285 seconds
Time taken to process frame 439: 0.0795 seconds
Time taken to process frame 401: 0.0233 seconds
Time taken to process frame 422: 0.0784 seconds
Time taken to process frame 436: 0.0295 seconds
Time taken to process frame 405: 0.0950 seconds
Time taken to process frame 404: 0.0932 seconds
Queue size: 0
Time taken to process frame 409: 0.0882 seconds
Time taken to process frame 449: 0.0976 seconds
Time taken to process frame 420: 0.1096 seconds
Time taken to process frame 421: 0.0951 seconds
Time taken to process frame 423: 0.0300 seconds
Time taken to process frame 424: 0.0942 seconds
Time taken to process frame 406: 0.0350 seconds
Time taken to process frame 402: 0.0803 seconds
Time taken to process frame 440: 0.1294 seconds
Queue size: 0
Time taken to process frame 437: 0.0910 seconds
Time taken to process frame 422: 0.0367 seconds
Time taken to process frame 405: 0.1091 seconds
Time taken to process frame 450: 0.1045 seconds
Time taken to process frame 421: 0.0313 seconds
Time taken to process frame 424: 0.0896 seconds
Time taken to process frame 410: 0.1616 seconds
Time taken to process frame 403: 0.0298 seconds
Time taken to process frame 425: 0.1028 seconds
Time taken to process frame 441: 0.0258 seconds
Queue size: 0
Time taken to process frame 407: 0.0916 seconds
Time taken to process frame 438: 0.0280 seconds
Time taken to process frame 406: 0.0230 seconds
Time taken to process frame 423: 0.0909 seconds
Time taken to process frame 451: 0.0840 seconds
Time taken to process frame 411: 0.0320 seconds
Time taken to process frame 422: 0.0850 seconds
Time taken to process frame 425: 0.0837 seconds
Time taken to process frame 426: 0.0307 seconds
Queue size: 0
Time taken to process frame 404: 0.0965 seconds
Time taken to process frame 408: 0.0261 seconds
Time taken to process frame 442: 0.0830 seconds
Time taken to process frame 439: 0.0849 seconds
Time taken to process frame 407: 0.0726 seconds
Time taken to process frame 452: 0.0421 seconds
Time taken to process frame 424: 0.0886 seconds
Time taken to process frame 423: 0.0492 seconds
Time taken to process frame 412: 0.0733 seconds
Time taken to process frame 426: 0.0531 seconds
Queue size: 2
Time taken to process frame 427: 0.1048 seconds
Time taken to process frame 443: 0.0495 seconds
Time taken to process frame 405: 0.1272 seconds
Time taken to process frame 409: 0.1121 seconds
Time taken to process frame 408: 0.0473 seconds
Time taken to process frame 425: 0.1022 seconds
Time taken to process frame 413: 0.0571 seconds
Time taken to process frame 440: 0.1407 seconds
Queue size: 4
Time taken to process frame 453: 0.0991 seconds
Time taken to process frame 424: 0.0912 seconds
Time taken to process frame 428: 0.0424 seconds
Time taken to process frame 427: 0.0930 seconds
Time taken to process frame 444: 0.0686 seconds
Time taken to process frame 406: 0.0353 seconds
Queue size: 0
Time taken to process frame 426: 0.0675 seconds
Time taken to process frame 409: 0.0866 seconds
Time taken to process frame 410: 0.1173 seconds
Time taken to process frame 414: 0.0574 seconds
Time taken to process frame 441: 0.1172 seconds
Time taken to process frame 429: 0.0322 seconds
Time taken to process frame 454: 0.0892 seconds
Time taken to process frame 407: 0.0290 seconds
Time taken to process frame 428: 0.0893 seconds
Queue size: 0
Time taken to process frame 425: 0.1966 seconds
Time taken to process frame 415: 0.1116 seconds
Time taken to process frame 410: 0.1547 seconds
Time taken to process frame 411: 0.1389 seconds
Time taken to process frame 427: 0.0707 seconds
Time taken to process frame 445: 0.2021 seconds
Time taken to process frame 442: 0.1122 seconds
Time taken to process frame 429: 0.0280 seconds
Time taken to process frame 430: 0.0966 seconds
Queue size: 1
Time taken to process frame 455: 0.1035 seconds
Time taken to process frame 408: 0.0987 seconds
Time taken to process frame 416: 0.0789 seconds
Time taken to process frame 426: 0.1500 seconds
Time taken to process frame 411: 0.1164 seconds
Time taken to process frame 443: 0.0635 seconds
Time taken to process frame 446: 0.1166 seconds
Time taken to process frame 428: 0.1136 seconds
Queue size: 0
Time taken to process frame 431: 0.0682 seconds
Time taken to process frame 412: 0.1223 seconds
Time taken to process frame 417: 0.0345 seconds
Time taken to process frame 409: 0.0697 seconds
Time taken to process frame 430: 0.0949 seconds
Time taken to process frame 427: 0.0962 seconds
Time taken to process frame 444: 0.0976 seconds
Time taken to process frame 412: 0.0979 seconds
Queue size: 0
Time taken to process frame 456: 0.0671 seconds
Time taken to process frame 447: 0.0895 seconds
Time taken to process frame 418: 0.0275 seconds
Time taken to process frame 429: 0.0843 seconds
Time taken to process frame 432: 0.0883 seconds
Time taken to process frame 413: 0.1494 seconds
Queue size: 0
Time taken to process frame 428: 0.1690 seconds
Time taken to process frame 431: 0.2255 seconds
Time taken to process frame 410: 0.2465 seconds
Time taken to process frame 457: 0.1781 seconds
Time taken to process frame 413: 0.2469 seconds
Time taken to process frame 430: 0.1705 seconds
Time taken to process frame 419: 0.1540 seconds
Queue size: 0
Time taken to process frame 433: 0.1500 seconds
Time taken to process frame 429: 0.1020 seconds
Time taken to process frame 448: 0.2551 seconds
Time taken to process frame 432: 0.1532 seconds
Time taken to process frame 414: 0.2247 seconds
Time taken to process frame 445: 0.3918 seconds
Time taken to process frame 431: 0.1121 seconds
Time taken to process frame 449: 0.0985 seconds
Queue size: 0
Time taken to process frame 434: 0.2002 seconds
Time taken to process frame 458: 0.2877 seconds
Time taken to process frame 430: 0.3406 seconds
Queue size: 1
Time taken to process frame 411: 0.4427 seconds
Time taken to process frame 459: 0.1247 seconds
Time taken to process frame 432: 0.2276 seconds
Time taken to process frame 446: 0.2879 seconds
Time taken to process frame 433: 0.3465 seconds
Time taken to process frame 435: 0.2225 seconds
Time taken to process frame 433: 0.0511 seconds
Time taken to process frame 412: 0.0938 seconds
Time taken to process frame 450: 0.2766 seconds
Time taken to process frame 414: 0.3418 seconds
Time taken to process frame 415: 0.4516 seconds
Time taken to process frame 431: 0.1953 seconds
Queue size: 4
Time taken to process frame 420: 0.5751 seconds
Time taken to process frame 434: 0.1666 seconds
Time taken to process frame 447: 0.2229 seconds
Time taken to process frame 451: 0.1444 seconds
Time taken to process frame 460: 0.2842 seconds
Time taken to process frame 436: 0.1230 seconds
Queue size: 0Time taken to process frame 413: 0.2758 seconds

Time taken to process frame 461: 0.0754 seconds
Time taken to process frame 448: 0.1161 seconds
Time taken to process frame 434: 0.3614 seconds
Time taken to process frame 452: 0.1326 seconds
Time taken to process frame 437: 0.1046 seconds
Time taken to process frame 432: 0.2556 seconds
Time taken to process frame 421: 0.2141 seconds
Time taken to process frame 415: 0.3818 seconds
Time taken to process frame 416: 0.3368 seconds
Time taken to process frame 462: 0.1171 seconds
Time taken to process frame 414: 0.1763 seconds
Queue size: 0
Time taken to process frame 453: 0.0996 seconds
Time taken to process frame 449: 0.1797 seconds
Time taken to process frame 435: 0.2159 seconds
Time taken to process frame 463: 0.0851 seconds
Time taken to process frame 422: 0.1502 seconds
Time taken to process frame 416: 0.0951 seconds
Time taken to process frame 433: 0.0935 seconds
Time taken to process frame 454: 0.0263 seconds
Time taken to process frame 438: 0.0971 seconds
Time taken to process frame 435: 0.2711 seconds
Time taken to process frame 417: 0.2152 seconds
Queue size: 0
Time taken to process frame 464: 0.0360 seconds
Time taken to process frame 423: 0.1454 seconds
Time taken to process frame 450: 0.1924 seconds
Time taken to process frame 417: 0.1077 seconds
Time taken to process frame 436: 0.1338 seconds
Time taken to process frame 415: 0.2776 seconds
Time taken to process frame 434: 0.1018 seconds
Queue size: 0
Time taken to process frame 455: 0.1119 seconds
Time taken to process frame 436: 0.0975 seconds
Time taken to process frame 439: 0.1263 seconds
Time taken to process frame 465: 0.1030 seconds
Time taken to process frame 418: 0.1405 seconds
Time taken to process frame 424: 0.1108 seconds
Time taken to process frame 451: 0.1031 seconds
Queue size: 0
Time taken to process frame 418: 0.0913 seconds
Time taken to process frame 437: 0.0949 seconds
Time taken to process frame 437: 0.0338 seconds
Time taken to process frame 416: 0.1049 seconds
Time taken to process frame 456: 0.0810 seconds
Time taken to process frame 435: 0.1372 seconds
Time taken to process frame 466: 0.0595 seconds
Time taken to process frame 419: 0.0440 seconds
Time taken to process frame 440: 0.1317 seconds
Queue size: 0
Time taken to process frame 419: 0.0310 seconds
Time taken to process frame 452: 0.0663 seconds
Time taken to process frame 438: 0.0653 seconds
Time taken to process frame 425: 0.1860 seconds
Time taken to process frame 417: 0.1096 seconds
Time taken to process frame 438: 0.1033 seconds
Time taken to process frame 457: 0.1021 seconds
Time taken to process frame 436: 0.0637 seconds
Time taken to process frame 467: 0.0952 seconds
Queue size: 0
Time taken to process frame 453: 0.0265 seconds
Time taken to process frame 420: 0.0836 seconds
Time taken to process frame 441: 0.0752 seconds
Time taken to process frame 426: 0.0507 seconds
Time taken to process frame 420: 0.0931 seconds
Time taken to process frame 418: 0.0388 seconds
Time taken to process frame 439: 0.0902 seconds
Time taken to process frame 439: 0.0543 seconds
Time taken to process frame 458: 0.0480 seconds
Queue size: 0Time taken to process frame 468: 0.0385 seconds

Time taken to process frame 437: 0.0965 seconds
Time taken to process frame 421: 0.0336 seconds
Time taken to process frame 454: 0.0707 seconds
Time taken to process frame 421: 0.0210 seconds
Time taken to process frame 442: 0.0560 seconds
Time taken to process frame 427: 0.1045 seconds
Queue size: 0
Time taken to process frame 419: 0.1122 seconds
Time taken to process frame 440: 0.1227 seconds
Time taken to process frame 440: 0.1047 seconds
Time taken to process frame 469: 0.0999 seconds
Time taken to process frame 438: 0.0485 seconds
Time taken to process frame 459: 0.0957 seconds
Time taken to process frame 422: 0.0952 seconds
Time taken to process frame 443: 0.0590 seconds
Time taken to process frame 422: 0.0790 seconds
Time taken to process frame 455: 0.1196 seconds
Queue size: 0
Time taken to process frame 428: 0.0874 seconds
Time taken to process frame 441: 0.0636 seconds
Time taken to process frame 441: 0.0615 seconds
Time taken to process frame 420: 0.1789 seconds
Time taken to process frame 439: 0.1059 seconds
Time taken to process frame 470: 0.1916 seconds
Time taken to process frame 423: 0.0747 seconds
Queue size: 0
Time taken to process frame 423: 0.0509 seconds
Time taken to process frame 460: 0.1340 seconds
Time taken to process frame 444: 0.1151 seconds
Time taken to process frame 456: 0.1060 seconds
Time taken to process frame 429: 0.1020 seconds
Time taken to process frame 442: 0.0875 seconds
Time taken to process frame 442: 0.0838 seconds
Time taken to process frame 421: 0.0699 seconds
Time taken to process frame 471: 0.0744 seconds
Queue size: 0
Time taken to process frame 424: 0.1020 seconds
Time taken to process frame 461: 0.1131 seconds
Time taken to process frame 424: 0.1501 seconds
Time taken to process frame 440: 0.2041 seconds
Time taken to process frame 457: 0.1047 seconds
Time taken to process frame 443: 0.0385 seconds
Time taken to process frame 445: 0.1834 seconds
Queue size: 0
Time taken to process frame 443: 0.1088 seconds
Time taken to process frame 430: 0.1368 seconds
Time taken to process frame 422: 0.0938 seconds
Time taken to process frame 472: 0.1178 seconds
Time taken to process frame 462: 0.1055 seconds
Time taken to process frame 425: 0.1356 seconds
Time taken to process frame 425: 0.0947 seconds
Time taken to process frame 458: 0.0552 seconds
Time taken to process frame 441: 0.0215 seconds
Time taken to process frame 444: 0.0687 seconds
Time taken to process frame 446: 0.0365 seconds
Queue size: 0
Time taken to process frame 431: 0.0370 seconds
Time taken to process frame 444: 0.0821 seconds
Time taken to process frame 423: 0.0920 seconds
Time taken to process frame 473: 0.0972 seconds
Time taken to process frame 426: 0.0547 seconds
Time taken to process frame 463: 0.0992 seconds
Time taken to process frame 459: 0.0295 seconds
Time taken to process frame 426: 0.0532 seconds
Queue size: 0
Time taken to process frame 442: 0.0908 seconds
Time taken to process frame 432: 0.0314 seconds
Time taken to process frame 445: 0.1151 seconds
Time taken to process frame 447: 0.1001 seconds
Time taken to process frame 424: 0.0290 seconds
Time taken to process frame 474: 0.0260 seconds
Time taken to process frame 427: 0.0250 seconds
Time taken to process frame 445: 0.1305 seconds
Time taken to process frame 464: 0.0260 seconds
Time taken to process frame 460: 0.0757 seconds
Time taken to process frame 427: 0.0261 seconds
Time taken to process frame 443: 0.0528 seconds
Time taken to process frame 446: 0.0385 seconds
Time taken to process frame 448: 0.0271 seconds
Time taken to process frame 433: 0.0798 seconds
Time taken to process frame 425: 0.0867 seconds
Time taken to process frame 475: 0.0725 seconds
Time taken to process frame 461: 0.0270 seconds
Time taken to process frame 446: 0.0460 seconds
Time taken to process frame 428: 0.0775 seconds
Time taken to process frame 444: 0.0306 seconds
Time taken to process frame 465: 0.0820 seconds
Time taken to process frame 428: 0.0908 seconds
Time taken to process frame 447: 0.0946 seconds
Time taken to process frame 449: 0.0836 seconds
Time taken to process frame 434: 0.0496 seconds
Time taken to process frame 426: 0.0252 seconds
Time taken to process frame 476: 0.0562 seconds
Time taken to process frame 447: 0.0788 seconds
Time taken to process frame 462: 0.0797 seconds
Time taken to process frame 429: 0.0646 seconds
Time taken to process frame 445: 0.0821 seconds
Time taken to process frame 466: 0.0787 seconds
Time taken to process frame 429: 0.0752 seconds
Time taken to process frame 450: 0.1208 seconds
Time taken to process frame 448: 0.1021 seconds
Time taken to process frame 448: 0.0255 seconds
Time taken to process frame 427: 0.1056 seconds
Time taken to process frame 435: 0.0886 seconds
Time taken to process frame 463: 0.0280 seconds
Time taken to process frame 477: 0.0847 seconds
Time taken to process frame 446: 0.0480 seconds
Time taken to process frame 430: 0.0942 seconds
Time taken to process frame 451: 0.0260 seconds
Time taken to process frame 467: 0.0778 seconds
Time taken to process frame 449: 0.0220 seconds
Time taken to process frame 430: 0.0812 seconds
Time taken to process frame 428: 0.0255 seconds
Time taken to process frame 449: 0.0742 seconds
Time taken to process frame 436: 0.0283 seconds
Time taken to process frame 464: 0.0807 seconds
Time taken to process frame 478: 0.0485 seconds
Time taken to process frame 431: 0.0434 seconds
Time taken to process frame 447: 0.0775 seconds
Time taken to process frame 468: 0.0402 seconds
Time taken to process frame 452: 0.0915 seconds
Time taken to process frame 431: 0.0388 seconds
Time taken to process frame 450: 0.0793 seconds
Time taken to process frame 429: 0.0815 seconds
Time taken to process frame 437: 0.0997 seconds
Time taken to process frame 450: 0.1361 seconds
Time taken to process frame 448: 0.0552 seconds
Time taken to process frame 465: 0.1442 seconds
Time taken to process frame 479: 0.1162 seconds
Time taken to process frame 432: 0.0897 seconds
Time taken to process frame 453: 0.0440 seconds
Time taken to process frame 469: 0.0825 seconds
Time taken to process frame 451: 0.0330 seconds
Time taken to process frame 432: 0.0667 seconds
Time taken to process frame 438: 0.0242 seconds
Time taken to process frame 451: 0.0500 seconds
Time taken to process frame 466: 0.0320 seconds
Time taken to process frame 430: 0.1246 seconds
Time taken to process frame 449: 0.0933 seconds
Time taken to process frame 433: 0.0289 seconds
Time taken to process frame 480: 0.1015 seconds
Time taken to process frame 454: 0.0807 seconds
Time taken to process frame 433: 0.0521 seconds
Time taken to process frame 452: 0.0978 seconds
Time taken to process frame 470: 0.1231 seconds
Time taken to process frame 439: 0.0987 seconds
Time taken to process frame 452: 0.0843 seconds
Time taken to process frame 431: 0.0458 seconds
Time taken to process frame 467: 0.0925 seconds
Time taken to process frame 481: 0.0377 seconds
Time taken to process frame 434: 0.0931 seconds
Time taken to process frame 450: 0.1244 seconds
Time taken to process frame 455: 0.1098 seconds
Time taken to process frame 471: 0.0545 seconds
Time taken to process frame 434: 0.0931 seconds
Time taken to process frame 453: 0.0509 seconds
Time taken to process frame 453: 0.0543 seconds
Time taken to process frame 468: 0.0466 seconds
Time taken to process frame 432: 0.0818 seconds
Time taken to process frame 440: 0.1453 seconds
Time taken to process frame 482: 0.0747 seconds
Time taken to process frame 451: 0.0634 seconds
Time taken to process frame 456: 0.0400 seconds
Time taken to process frame 435: 0.1467 seconds
Time taken to process frame 454: 0.0384 seconds
Time taken to process frame 472: 0.1030 seconds
Time taken to process frame 435: 0.1728 seconds
Time taken to process frame 454: 0.0835 seconds
Time taken to process frame 441: 0.0452 seconds
Time taken to process frame 483: 0.0473 seconds
Time taken to process frame 452: 0.0395 seconds
Time taken to process frame 469: 0.1148 seconds
Time taken to process frame 433: 0.0588 seconds
Time taken to process frame 436: 0.0478 seconds
Time taken to process frame 457: 0.0895 seconds
Time taken to process frame 455: 0.0753 seconds
Time taken to process frame 473: 0.0814 seconds
Time taken to process frame 436: 0.0919 seconds
Time taken to process frame 484: 0.0959 seconds
Time taken to process frame 455: 0.1459 seconds
Time taken to process frame 442: 0.1312 seconds
Time taken to process frame 453: 0.1143 seconds
Time taken to process frame 434: 0.1075 seconds
Time taken to process frame 470: 0.1788 seconds
Time taken to process frame 458: 0.0774 seconds
Time taken to process frame 437: 0.1121 seconds
Time taken to process frame 456: 0.0718 seconds
Time taken to process frame 474: 0.0818 seconds
Time taken to process frame 456: 0.0650 seconds
Time taken to process frame 437: 0.1121 seconds
Time taken to process frame 443: 0.0759 seconds
Time taken to process frame 471: 0.0469 seconds
Time taken to process frame 454: 0.0994 seconds
Time taken to process frame 485: 0.1779 seconds
Time taken to process frame 435: 0.1240 seconds
Time taken to process frame 457: 0.1155 seconds
Time taken to process frame 459: 0.1145 seconds
Time taken to process frame 438: 0.0680 seconds
Time taken to process frame 457: 0.1011 seconds
Time taken to process frame 438: 0.1596 seconds
Time taken to process frame 475: 0.1671 seconds
Time taken to process frame 444: 0.1037 seconds
Time taken to process frame 472: 0.0851 seconds
Time taken to process frame 486: 0.0613 seconds
Time taken to process frame 436: 0.0398 seconds
Time taken to process frame 455: 0.0964 seconds"""

# Use regex to extract numbers, skipping lines starting with "Queue"
processing_times = []
for line in data.splitlines():
    if line.startswith('Queue'):  # Skip lines starting with "Queue"
        continue

    match = re.search(r": ([0-9]+\.[0-9]+)", line)
    if match:
        processing_times.append(float(match.group(1)))

# Output the list to a text file
output_file = "processing_times.txt"
with open(output_file, "w") as file:
    for time in processing_times:
        file.write(f"{time}\n")

print(f"Processing times written to {output_file}")


