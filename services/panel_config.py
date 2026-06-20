def get_panel_offset(panel_name):
    mapping = {
        'top_left': 0,
        'top_right': 32,
        'mid_left': 64,
        'mid_right': 96,
        'bot_left': 128,
        'bot_right': 160
    }
    return mapping[panel_name]

# ====================== Draw Speed Split ======================
def draw_large_split_text(canvas, text, color, top_left_x, top_left_y, mid_left_x, mid_left_y):
    image = Image.new("RGB", (32, 32), "black")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=pil_font, fill=(color.red, color.green, color.blue))

    top_half = image.crop((0, 0, 32, 16))
    bottom_half = image.crop((0, 16, 32, 32))

    for y in range(top_half.size[1]):
        for x in range(top_half.size[0]):
            r, g, b = top_half.getpixel((x, y))
            canvas.SetPixel(top_left_x + x, top_left_y + y, r, g, b)

    for y in range(bottom_half.size[1]):
        for x in range(bottom_half.size[0]):
            r, g, b = bottom_half.getpixel((x, y))
            canvas.SetPixel(mid_left_x + x, mid_left_y + y, r, g, b)

def update_display(speed, speed_limit):
    canvas.Clear()

    # Choose color and alert message
    if speed <= speed_limit - 10:
        color = color_safe
        alert = "Safe Speed"
    elif speed_limit - 10 < speed <= speed_limit:
        color = color_warn
        alert = "Warning"
    else:
        color = color_alert
        alert = "SLOW DOWN!"

    # ==== Draw SPEED across top_left and mid_left ====
    speed_text = str(speed)
    draw_large_split_text(
        canvas,
        speed_text,
        color,
        get_panel_offset('top_left'),
        0,
        get_panel_offset('mid_left'),
        0
    )

    # ==== Draw 'km/h' on mid_right ====
    x_kmh = get_panel_offset('mid_right') + 2
    graphics.DrawText(canvas, font_small, x_kmh, 12, color, "km/h")

    # ==== Draw alert message across bot panels ====
    # Measure alert width
    alert_width = graphics.DrawText(canvas, font_small, 0, 0, graphics.Color(0, 0, 0), alert)
    x_alert = get_panel_offset('bot_left') + 64 - (alert_width // 2)
    graphics.DrawText(canvas, font_small, x_alert, 12, color, alert)

    matrix.SwapOnVSync(canvas)