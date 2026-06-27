import qrcode
import io


def generate_qr(amount):

    qr = qrcode.make(f"Pay MMK {amount}")

    buf = io.BytesIO()

    qr.save(buf, format="PNG")

    return buf