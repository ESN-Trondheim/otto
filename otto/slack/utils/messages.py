import io
import qrcode
from slack_bolt import Args


def send_qr(args: Args, link_id: str):
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
    qr.add_data(f"https://links.trondheim.esn.no/{link_id}")
    qr.make(fit=True)
    image = qr.make_image(fill='black', back_color='white')
    image_content = io.BytesIO()
    image.save(image_content, format="JPEG")

    args.client.files_upload_v2(
        channel=args.body["container"]["channel_id"],
        thread_ts=args.body["container"]["thread_ts"],
        content=image_content.getvalue(),
        filename=f"{link_id}-qr.jpg",
    )