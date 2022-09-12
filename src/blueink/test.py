

def lilboi(a=1, b=1, **kwargs):
    print('lb.a', a)
    print('lb.b', b)
    print('lb.kwargs', kwargs)

def bigboi(a=1, b=1, c=1, **kwargs):
    print('bb.a', a)
    print('bb.b', b)
    print('bb.c', c)
    print('bb.kwargs', kwargs)
    lilboi(a,b,c=c,**kwargs)

bigboi(2, 2, c=2)