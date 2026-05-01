# a, b=0,1 
# while a <10:
#     print(a, end=",")
#     a,b= b, a+b

#list;
# words=["books","pen","pencil"]
# for w in words:
#     print(w, len(w))

# for w in range(len(words)):
#     print(w, words[w]) 

for n in range (2,10):
    for x in range(2,n):
        if n%x==0:
            print(f"{n} is equal {x} *{n//x}")
            break

for num in range(2,10):
    if num%2==0:
        print(f"num is potive {num}")
        continue
    print(f"num is negative {num}")

for e in range(2,10):
    for c in range(2,e):
        if e%c==0:
            print(f"{e} equals to {c}*{e//c}")
    else:
            print(n, "prime number")