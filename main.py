from mfrc522 import MFRC522
from machine import Pin, SPI
from utime import sleep
import pcd8544
import framebuf
import random

btn_1 = Pin(21, Pin.IN, Pin.PULL_UP)
btn_2 = Pin(26, Pin.IN, Pin.PULL_UP)
btn_3 = Pin(28, Pin.IN, Pin.PULL_UP)

spi = SPI(0)
spi.init(baudrate=2000000, polarity=0, phase=0)
print(spi)
cs = Pin(5)
dc = Pin(4)
rst = Pin(8)
lcd = pcd8544.PCD8544(spi, cs, dc, rst)
buffer = bytearray((lcd.height // 8) * lcd.width)
framebuf = framebuf.FrameBuffer(buffer, lcd.width, lcd.height, framebuf.MONO_VLSB)

xor_key=[]
entered_pin=""
pin_digit=0
key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
reader = MFRC522(spi_id=1,sck=14,miso=12,mosi=15,cs=13,rst=20)
blocks=[1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,28,29,30,32,33,34,36,37,38,40,41,42,44,45,46,48,49,50,52,53]
data=[]
wallet_types={
    "BTC ":(34,52),
    "LTC ":(34,51),
    "NANO":(60,64),
    "BAN ":(60,64),
    "DOGE":(34,51)
}
wallets=[]
wallet_index=0
wallet_page=0
secret_page=0

state=0 # CHANGE STATE TO 1000 IF YOU WANT TO WRITE DATA TO CARD

def gen_xor_key(seed):
    random.seed(seed)
    global xor_key
    xor_key=[random.randrange(256) for _ in range(64)]

def addr(t,a):
    txt=t+a
    arr=[ord(c) for c in txt]
    while len(arr)<64:
        arr.append(0)
    assert len(arr)==64
    return arr

def encr(k):
    assert len(k)<=64 and len(k)>0
    arr=[ord(k[i])^xor_key[i] for i in range(len(k))]
    while len(arr)<64:
        arr.append(0)
    return arr

def decr(k,n):
    r=""
    assert len(k)==64 and n>0 and n<=64
    for i in range(n):
        r+=chr(k[i]^xor_key[i])
    return r

def get_addr(d,t):
    a=''.join(chr(i) for i in d)[:wallet_types[t][0]]
    if t=="NANO":
        a="nano_"+a
    elif t=="BAN ":
        a="ban_"+a
    return a

def start_screen():
    global wallets
    global wallet_index
    global wallet_page
    wallets=[]
    wallet_index=0
    wallet_page=0
    framebuf.fill(0)
    if state==1000:
        framebuf.text('Writing', 0, 0, 1)
    else:
        framebuf.text('Scan the', 0, 0, 1)
    framebuf.text('card...', 0, 10, 1)
    framebuf.rect(8, 28, 68, 8, 1)
    lcd.data(buffer)

def decrypt_screen():
    framebuf.fill(0)
    framebuf.text(wallets[wallet_index][0], 0, 0, 1)
    framebuf.text("secret", 36, 0, 1)
    framebuf.line(0,8,84,8,1)
    framebuf.text("Enter pin", 6, 15, 1)
    framebuf.text("to decrypt", 2, 38, 1)
    framebuf.rect(8,25,68,11,1)
    framebuf.text("0",10,27,1)
    lcd.data(buffer)

def refresh_pin():
    framebuf.fill_rect(9,26,66,9,0)
    if entered_pin:
        framebuf.text("*"*len(entered_pin),10,27,1)
    framebuf.text(str(pin_digit),10+8*len(entered_pin),27,1)
    lcd.data(buffer)

def show_secret():
    framebuf.fill_rect(0,9,84,38,0)
    wt=wallet_types[wallets[wallet_index][0]][1]
    for y in range(1,5):
        framebuf.text(decr(wallets[wallet_index][2], wt)[(y-1)*10+40*secret_page:y*10+40*secret_page], 0, 10*y, 1)
    lcd.data(buffer)

def display_wallet():
    framebuf.fill(0)
    if wallet_index<len(wallets):
        framebuf.text(wallets[wallet_index][0], 0, 0, 1)
        framebuf.text("wallet", 36, 0, 1)
        framebuf.line(0,8,84,8,1)
        for y in range(1,5):
            framebuf.text(wallets[wallet_index][1][(y-1)*10+40*wallet_page:y*10+40*wallet_page], 0, 10*y, 1)
    else:
        framebuf.text("End", 30, 0, 1)
        framebuf.text("session?", 10, 10, 1)
        framebuf.text('Press (3)', 6, 25, 1)
        framebuf.text('to restart', 2, 35, 1)
    lcd.data(buffer)

def uidToString(uid):
    mystring = ""
    for i in uid:
        mystring = "%02X" % i + mystring
    return mystring

def write_card(uid):
    # USE THIS METHOD ONLY FOR WRITING DATA TO CARD ONLY ONCE
    # AFTER SUCCESFUL SAVING DATA TO CARD YOU SHOULD REPLACE
    # YOUR PROVIDED DATA IN THIS METHOD OR DELETE THIS METHOD AND SAVE PROGRAM TO THE PI PICO
    global data
    data=[]
    # UP TO FIVE WALLETS
    wallets_to_write=[
        ["REPLACE_WITH_TYPE_MUST_BE_4_CHARS","REPLACE_WITH_ADDRESS_UP_TO_60_CHARS","REPLACE_WITH_SEED_OR_PRIVATE_KEY_UP_TO_64_CHARS"],
        ["REPLACE_WITH_TYPE_MUST_BE_4_CHARS","REPLACE_WITH_ADDRESS_UP_TO_60_CHARS","REPLACE_WITH_SEED_OR_PRIVATE_KEY_UP_TO_64_CHARS"],
        ["REPLACE_WITH_TYPE_MUST_BE_4_CHARS","REPLACE_WITH_ADDRESS_UP_TO_60_CHARS","REPLACE_WITH_SEED_OR_PRIVATE_KEY_UP_TO_64_CHARS"],
        ["REPLACE_WITH_TYPE_MUST_BE_4_CHARS","REPLACE_WITH_ADDRESS_UP_TO_60_CHARS","REPLACE_WITH_SEED_OR_PRIVATE_KEY_UP_TO_64_CHARS"],
        ["REPLACE_WITH_TYPE_MUST_BE_4_CHARS","REPLACE_WITH_ADDRESS_UP_TO_60_CHARS","REPLACE_WITH_SEED_OR_PRIVATE_KEY_UP_TO_64_CHARS"]
    ]
    assert len(wallets_to_write)<=5
    pass_pin=30642913 #REPLACE WITH YOUR PIN, CHANGE CODE IF YOU WANT ENCRYPT EVERY PRIVATE KEY OR SEED WITH DIFFERENT PIN NUMBER
    random.seed(pass_pin)
    global xor_key
    xor_key=[random.randrange(256) for _ in range(64)]
    for w in wallets_to_write:
        data+=addr(w[0],w[1])
        data+=encr(w[2])
    for i in range(40):
        status = reader.auth(reader.AUTHENT1A, blocks[i], key, uid)
        if status != reader.OK:
            #print("Auth error with: {:02d} block".format(blocks[i]))
            framebuf.fill_rect(8+1, 28+1, 68-2, 8-2, 0)
            lcd.data(buffer)
            return False
        stat = reader.write(blocks[i],data[i*16:i*16+16])
        print(stat)
        if stat != reader.OK:
            return False
        else:
            framebuf.fill_rect(8+1, 28+1, int((68-2)*(i/40.0)), 8-2, 1)
            lcd.data(buffer)
        #print("Successful read {:02d} block".format(blocks[i]))
    #print("Card scanned")
    framebuf.fill_rect(8, 28, 68, 8, 1)
    lcd.data(buffer)
    return True

def read_card(uid):
    global data
    data=[]
    for i in range(40):
        status = reader.auth(reader.AUTHENT1A, blocks[i], key, uid)
        if status != reader.OK:
            #print("Auth error with: {:02d} block".format(blocks[i]))
            framebuf.fill_rect(8+1, 28+1, 68-2, 8-2, 0)
            lcd.data(buffer)
            return False
        block = reader.read(blocks[i])
        if block:
            data+=block
            framebuf.fill_rect(8+1, 28+1, int((68-2)*(i/40.0)), 8-2, 1)
            lcd.data(buffer)
        #print("Successful read {:02d} block".format(blocks[i]))
    #print("Card scanned")
    framebuf.fill_rect(8, 28, 68, 8, 1)
    lcd.data(buffer)
    return True

start_screen()

try:
    while True:
        if state==0:
            (stat, tag_type) = reader.request(reader.REQIDL)
            if stat == reader.OK:
                (stat, uid) = reader.SelectTagSN()
                if stat == reader.OK:
                    print("Card detected %s" % uidToString(uid))
                    if read_card(uid):
                        sleep(0.1)
                        reader.stop_crypto1()
                        state=1
                else:
                    print("Authentication error")
        elif state==-1:
            if btn_3.value()==0:
                start_screen()
                state=0
        elif state==1:
            for i in range(5):
                a=data[i*128:i*128+128]
                address_type=''.join(chr(i) for i in a[:4])
                if address_type in wallet_types:
                    print(address_type+" wallet detected")
                    wallets.append([])
                    wallets[-1].append(address_type)
                    wallets[-1].append(get_addr(a[4:64],address_type))
                    wallets[-1].append(a[64:])
            if wallets:
                #print(wallets)
                display_wallet()
                state=2
            else:
                print("No wallets detected!")
                framebuf.fill(0)
                framebuf.text('No wallets', 0, 0, 1)
                framebuf.text('detected!', 0, 10, 1)
                framebuf.text('Press (3)', 6, 25, 1)
                framebuf.text('to restart', 2, 35, 1)
                lcd.data(buffer)
                state=-1
        elif state==2:
            if btn_1.value()==0 and wallet_index!=len(wallets):
                if len(wallets[wallet_index][1])>40:
                    wallet_page=(wallet_page+1)%2
                    display_wallet()
                    sleep(0.5)
            elif btn_2.value()==0:
                wallet_index=(wallet_index+1)%(len(wallets)+1)
                wallet_page=0
                display_wallet()
                sleep(0.5)
            elif btn_3.value()==0:
                if wallet_index==len(wallets):
                    start_screen()
                    state=0
                else:
                    decrypt_screen()
                    state=3
                    sleep(0.5)
        elif state==3:
            if btn_1.value()==0:
                if entered_pin:
                    pin_digit=int(entered_pin[-1])
                    entered_pin=entered_pin[:-1]
                    refresh_pin()
                    sleep(0.5)
            elif btn_2.value()==0:
                pin_digit=(pin_digit+1)%10
                refresh_pin()
                sleep(0.5)
            elif btn_3.value()==0:
                if len(entered_pin)<7:
                    entered_pin+=str(pin_digit)
                    pin_digit=0
                    refresh_pin()
                    sleep(0.5)
                else:
                    entered_pin+=str(pin_digit)
                    gen_xor_key(int(entered_pin))
                    secret_page=0
                    pin_digit=0
                    entered_pin=""
                    show_secret()
                    state=4
                    sleep(0.5)
        elif state==4:
            if len(wallets[wallet_index][2])>40:
                if btn_1.value()==0:
                    secret_page=(secret_page-1)%2
                    show_secret()
                    sleep(0.5)
                elif btn_2.value()==0:
                    secret_page=(secret_page+1)%2
                    show_secret()
                    sleep(0.5)
            if btn_3.value()==0:
                display_wallet()
                state=2
                sleep(0.5)
        elif state==1000:
            (stat, tag_type) = reader.request(reader.REQIDL)
            if stat == reader.OK:
                (stat, uid) = reader.SelectTagSN()
                if stat == reader.OK:
                    print("Card detected %s" % uidToString(uid))
                    if write_card(uid):
                        sleep(0.1)
                        reader.stop_crypto1()
                        state=1
                else:
                    print("Authentication error")
                

except KeyboardInterrupt:
    print("Bye")




