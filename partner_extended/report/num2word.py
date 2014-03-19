# -*- coding: utf-8 -*-

def ucluyuVer(sayi):
    birler = ["","bir","iki","üç","dört","bes","alti","yedi","sekiz","dokuz"]
    onlar = ["","on","yirmi","otuz","kirk","elli","altmis","yetmis","seksen","doksan"]
    yuzler = [i+"yüz" for i in birler]
    yuzler[1] = "yüz"

    basamaklar = [birler,onlar,yuzler]

    sayi = sayi[::-1]
    yazi,bs = [],0
    for i in sayi:
        rakam = sayi[bs]
        bs += 1
        if rakam != "0":
            yazi.append(basamaklar[bs-1][int(rakam)])
    return "".join(reversed(yazi))

ucluler=["","bin","milyon","milyar","trilyon","katrilyon","kentilyon",
         "sekstilyon","oktilyon","nonilyon","desilyon"]

def return_number(sayi):
	#sayi here is a number in string format
	sayi = '{:,}'.format(int(sayi))
	haneler = reversed(sayi.split(","))
	uclus,sonuc = 0,[]
	for hane in haneler:
		uclu = ucluyuVer(hane)
		if uclu != "":
			sonuc.append(uclu+""+ucluler[uclus])
		uclus+=1
	son = "".join(reversed(sonuc))
	if son.startswith('birbin'):
		son = son[3:]
	return(son.strip())
