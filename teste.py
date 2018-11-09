from deck import Deck

d = Deck()
d.shuffle()
c = d.deal()
print(c)
c = str(c)

c.replace(c[2], " ")
print (c)

# print(int(c[0])+2)