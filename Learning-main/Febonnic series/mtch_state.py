class Point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
def where_is(point):
        match point:
            case Point(x=0, y=0):
                print("origin")
            case Point(x=0, y=y):
                print(f"y={y}")
            case Point(x=x, y=0):
                print(f"x={x}")
            case Point(x=x , y = y):
                print(f"x={x},y={y}")

p1=Point(0,0)
p2=Point(0,10)
p3=Point(2,0)
p4=Point("buffering",10)
where_is(p1)
where_is(p2)
where_is(p3)
where_is(p4)