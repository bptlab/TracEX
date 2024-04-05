def eins():
    list = []
    zwei(list)


def zwei(list):
    drei(list)
    print(list)


def drei(list):
    list.append(1)


eins()
