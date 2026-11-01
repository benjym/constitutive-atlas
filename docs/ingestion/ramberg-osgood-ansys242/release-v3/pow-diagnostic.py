import math,json
s=[100000,0,0,0,0,0];m=math.fsum(s[:3])/3;d=[s[i]-(m if i<3 else 0) for i in range(6)];q=math.sqrt(1.5*math.fsum(x*x for x in d));z=q/100000
print(json.dumps({'q':q,'z':z,'pow':z**1.5,'product_sqrt':z*math.sqrt(z),'hex':[(z**1.5).hex(),(z*math.sqrt(z)).hex()]}))
