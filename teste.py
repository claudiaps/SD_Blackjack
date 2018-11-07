from deck import Deck

d = Deck()
d.shuffle()
c = []
for i in range(len(d)):
    c.append(d.deal())

print("c", c)
print("d", d)