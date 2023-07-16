from captcha.image import ImageCaptcha
import random, string


def generate_captcha(n=4):
    image = ImageCaptcha()
    alphabet = "2345689ABCDEFGHKMRSTUXYZ"
    captcha_text = "".join(random.choices(alphabet, k=n))
    data = image.generate(captcha_text)

    return captcha_text, data
