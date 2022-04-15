from PIL import Image, ImageFilter
import qrcode
import cv2 as cv


class QR_Operation():
    def __init__(self, qr_name):
        self.qr_name = qr_name

    def qr_coder(self, text='Pass'):
        img = qrcode.make(text)
        img.save(self.qr_name + '.png')

    def im_to_qr(self, image_name='image'):
        im = Image.open(image_name + '.png')
        im2 = Image.open(self.qr_name + '.png')
        x, y = im2.size
        pixels_qr = im2.load()
        im = im.resize((x, y))
        pixels_im = im.load()
        im.putalpha(115)

        for i in range(1, x - 1):
            for j in range(1, y - 1):
                if pixels_qr[i, j] == 0:
                    pixels_im[i, j] = (0, 0, 0)
                else:
                    for p in range(-1, 2):
                        for t in range(-1, 2):
                            if pixels_qr[i + p, j + t] == 0:
                                pixels_im[i, j] = (255, 255, 255)
        im.save(f"qr_{image_name + '.png'}")

    def qr_decode(self):
        im = cv.imread(self.qr_name + '.png')
        det = cv.QRCodeDetector()

        retval, points, straight_qrcode = det.detectAndDecode(im)
        return retval

    def make_gif(self, name='gif', f_number=10):
        frames = []

        for i in range(1, f_number + 1):
            f = Image.open(f'gif/{name}-{i}.jpg')
            f = f.resize((500, 500))
            frames.append(f)

        frames[0].save(
            f'{name}.gif',
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=500,
            loop=0
        )

'''
x = QR_Operation()
x = QR_Operation(input('Your text '), input('File name '))
print(x.qr_decode(input('File name ')))
x.im_to_qr(input('Image name '), input('Qr name '))
x.make_gif(input('Frame names '), int(input('Frame number ')))'''
