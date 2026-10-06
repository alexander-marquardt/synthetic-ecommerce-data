import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]))
moved=[k for k in set(a['types'])|set(b['types']) if a['types'].get(k)!=b['types'].get(k)]
print(f"{sys.argv[3]}: moved={sorted(moved)} whole_order_same={a['whole_order']==b['whole_order']}")
