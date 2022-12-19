
import socket

# importando as constantes e funcoes de sdtp.py
from sdtp import *

# criando um pacote SDTP usando class
pout = SDTPPacket(0, 0, 0, TH_SYN, 0)
# NOTE: será criada uma classe onde os atributos equivalem aos campos do pacote

# imprimindo o pacote
print("Pacote enviado:")
# ha 3 formas de se imprimir um pacote
# pout.print() # a partir de seus atributos
pout.print_struct() # a partir da struct criada
# print_packet(pout.to_struct()) # usar a função antiga para imprimir a struct
# criada com o método 'to_struc()' da classe
# criando um socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# enviando o pacote SDTP para o servidor
# NOTE: é preciso enviar a struct, que deverá ser criada a partir dos atributos
# da classe
s.sendto(pout.to_struct(), (IP, PORTA))

# recebendo um pacote pelo socket 's' e aguardando 2 segundos de timeout
res = recvtimeout(s, 2000) # 2000ms

while (res == -2):
    print("Erro de timeout - reenviar o pacote")
    s.sendto(pout.to_struct(), (IP, PORTA))
    res = recvtimeout(s, 2000)
    if res != -2:
        break

print("Pacote recebido:")
# NOTE: estou criando um pacote "zerado"
pin = SDTPPacket()
# e estou atribuindo seus atributos de acordo com a struct recebida
pin.from_struct(res)
pin.print_struct()

# checando se é um SYN/ACK
if pin.flags == TH_SYN | TH_ACK:
    # criando e enviando um ack
    pout = SDTPPacket(0, 0, 0, TH_ACK, 0)
    s.sendto(pout.to_struct(), (IP, PORTA))
    print("Pacote ack enviado:")
    pout.print()
    res = recvtimeout(s, 2000) # 2000ms

    while (res == -2):
        print("Erro de timeout - reenviar o pacote")
        pout = SDTPPacket(0, 0, 0, TH_ACK, 0)
        s.sendto(pout.to_struct(), (IP, PORTA))
        res = recvtimeout(s, 2000)
        if res != -2:
            break

    print("Pacote recebido:")
    # NOTE: estou criando um pacote "zerado"
    pin = SDTPPacket()
    # e estou atribuindo seus atributos de acordo com a struct recebida
    pin.from_struct(res)
    pin.print_struct()

# FIX: aqui voce deve controlar o loop de envio de todo o arquivo
file = open("../lorem_ipsum.txt", "r")

f = file.read(pin.window)
# # NOTE: estou criando um pacote "zerado"
# pack = SDTPPacket()

while (f != ''):
    # exemplo de envio de dados
    pdata = SDTPPacket()
    pdata.seqnum = pin.acknum
    pdata.data = f
    pdata.datalen = len(pdata.data)
    #pout.flags = 0x0 # NOTE: pacotes de dados possuem flag 0
    s.sendto(pdata.to_struct(), (IP, PORTA))
    pdata.print_struct()

    res = recvtimeout(s, 2000) # 2000ms

    while True:
        if (res == -2):
            print("Erro de timeout - reenviar o pacote")
            pdata.print_struct()
            s.sendto(pdata.to_struct(), (IP, PORTA))
            res = recvtimeout(s, 2000)
        else:
            print("Pacote recebido:")
            # e estou atribuindo seus atributos de acordo com a struct recebida
            pin = SDTPPacket()
            pin.from_struct(res)
            pin.print_struct()


            if(pin.flags != TH_ACK):
                print("Confirmação de recebimento não recebida - reenviar o pacote")
                pdata.print_struct()
                s.sendto(pdata.to_struct(), (IP, PORTA))
                res = recvtimeout(s, 2000)

            else:
                if (compute_checksum(res) == 0):
                    break
                else:
                    print("Pacote Corrompido - reenviar o pacote")
                    pdata.print_struct()
                    s.sendto(pdata.to_struct(), (IP, PORTA))
                    res = recvtimeout(s, 2000) # 2000ms


    f = file.read(pin.window)

pend = SDTPPacket(0, 0, 0, TH_FIN, 0)

print("Pacote FIN enviado:")
pend.print_struct()
s.sendto(pend.to_struct(), (IP, PORTA))

res = recvtimeout(s, 2000) # 2000ms

while (res == -2):
    print("Erro de timeout - reenviar o pacote FIN")
    s.sendto(pend.to_struct(), (IP, PORTA))
    res = recvtimeout(s, 2000)

print("Pacote recebido:")
# NOTE: estou criando um pacote "zerado"
pin = SDTPPacket()
# e estou atribuindo seus atributos de acordo com a struct recebida
pin.from_struct(res)
pin.print_struct()

while True:
    if (res.flags == TH_ACK):
        print("ACABOU!")
        break
    else: 
        s.sendto(pend.to_struct(), (IP, PORTA))
        res = recvtimeout(s, 2000)

print("ACABOU!")
# TODO: observe que os dados a enviar devem ser obtidos a partir do
# arquivo

# TODO: o tamanho dos dados a enviar deve respeitar o tamanho de window
# enviado pelo servidor, que é controle de fluxo

# TODO: deve-se verificar se o servidor responde um ACK, caso nao
# responda, voce deve reenviar o pacote anterior

# TODO: é preciso verificar se o arquivo finalizou, se finalizou, deve-se
# encerrar a conexao com o servidor, com um pacote FIN

# references: 
# 1. https://kytta.medium.com/tcp-packets-from-scratch-in-python-3a63f0cd59fe
# 2. https://docs.python.org/3/library/struct.html
# 3. https://wiki.python.org/moin/UdpCommunication

