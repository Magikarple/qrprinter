import qrcode, os
from datetime import date
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

URL = 'https://www.erxtools.com'
with open('url.txt', 'r') as f:
    URL = f.read().strip(' \n')
    print(f'using loaded from file: {URL}\n')

current_date = date.today()
pagesize = (2550, 3300)

while 1:
    i = input(f'Use current date? (y/n)\n{current_date.strftime("%b. %d %Y")}\n').lower()
    if i == 'n':
        i = input('Input current date dd/mm/yyyy\n(April. 11th, 1948 -> 11/04/1948)\n').lower().strip().split('/')
        try:
            current_date = date(int(i[2]), int(i[1]), int(i[0]))
        except IndexError:
            pass
        
        break
    if i == 'y':
        break

try:
    with open('next_start_num.txt', 'r') as f:
        start_number = int(f.read().strip())    
        while 1:
            i = input(f'Use current serial number? (y/n)\n{start_number}\n').lower()
            if i == 'y':
                break
            if i == 'n':
                raise TypeError
except (FileNotFoundError, TypeError, ValueError):
    while 1:
        try:
            start_number = int(input('Number to start batch on: '))
        except TypeError:
            continue
        break

while 1:
    try:
        quantity = int(input('Quantity of labels to generate: '))
    except TypeError:
        continue
    break

with open('next_start_num.txt', 'w') as f:
    f.write(str(start_number + quantity))

print(f'{start_number}-{quantity + start_number - 1}, {current_date.strftime("%b. %d %Y")}\nGenerating codes...')

# h_padding = 98 + 17
# v_padding = 64 + 17
# h_offset = 244
# v_offset = 160

h_padding = 98 + 17 + 99
v_padding = 64 + 17 + 99
h_offset = 244 + 50
v_offset = 160 + 50

codes = []
for n in range(quantity):
    # Generate text content for codes
    # codes += [qrcode.make(f'SN: {n + start_number}, Date: {current_date.strftime("%b. %d %Y")}, https://www.erxtools.com', version=4, box_size=13, border=0)]
    codes += [qrcode.make(f'{URL}?serial number {n + start_number} date {current_date.strftime("%b. %d %Y")}', version=4, box_size=10, border=0)]

im_size = codes[0].size[0]
# row_limit = pagesize[0] // im_size
# col_limit = pagesize[1] // im_size
row_limit = 4
col_limit = 6
pagemax = row_limit * col_limit

print('Codes generated!\nGenerating pages...')

fnt = ImageFont.truetype('fonts/Roboto-Bold.ttf', 25)

pages = []
page_lengths = []
for n in range(((len(codes) - 1) // pagemax) + 1):
    # Add image object for each page for each group of qr codes
    pages += [Image.new('L', pagesize, 255)]
    for i in range(min(pagemax, len(codes))):
        # create draw object
        d = ImageDraw.Draw(pages[n])
        # add Serial NUmber as text above QR code
        d.text(
            (
                ((im_size + h_padding) * (i % row_limit)) + h_offset,
                ((im_size + v_padding) * (i // row_limit)) + v_offset - 35
            ),
            f'SN: {start_number + (n * pagemax) + i}',
            font=fnt
        )
        # add the QR code itself below the text
        pages[n].paste(
            codes[i].copy(),
            box=(
                ((im_size + h_padding) * (i % row_limit)) + h_offset,
                ((im_size + v_padding) * (i // row_limit)) + v_offset
            )
        )
    page_lengths += [[
        start_number + (n * pagemax),
        start_number + (n * pagemax) + min(pagemax, len(codes)) - 1
        ]]
    codes = codes[pagemax:]

print('Pages generated!\nSaving...')
img_list = []
for n in range(len(pages)):
    img_list += [f'{page_lengths[n][0]}-{page_lengths[n][1]}.png']
    pages[n].save(img_list[-1], 'png')

pdf = FPDF(unit='in', format='Letter')

while img_list:
    pdf.add_page()
    pdf.image(name=img_list[0], x=0, y=0, w=8.5, h=11, type='png')
    os.remove(img_list[0])
    img_list = img_list[1:]

try:
    with open('save_location.txt', 'r') as save_location:
        save_location = save_location.read().strip(' \n')
        pdf.output(save_location+f'\\{page_lengths[0][0]}-{page_lengths[-1][1]}.pdf')
except:
    pdf.output(f'{Path.home()}\\Desktop\\{page_lengths[0][0]}-{page_lengths[-1][1]}.pdf')
    print(f'Pages saved in {Path.home()}\\OneDrive\\Desktop\\{page_lengths[0][0]}-{page_lengths[-1][1]}.pdf')

input('Finished, press enter to close the window.\n')
