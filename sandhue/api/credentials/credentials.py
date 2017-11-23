BRIDGE_IP = "192.168.8.104" # "192.168.1.38"
USERNAME = "slkiNPsD501zowIgkCWSzdrMrYvcYP6gKvp5uaxb"

id2name = {u'1': "Spisestue 1",
           u'2': "Spisestue 2",
           u'3': "Stue 1",
           u'4': "Hoveddor",
           u'5': "Sofa 1",
           u'6': "Entre 1"}


def getName(id):
    if id in id2name:
        return id2name[id]
    else:
        return "<id not in use>"
