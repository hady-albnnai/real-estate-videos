import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import time
import imageio_ffmpeg

t0 = time.time()
OUT_W, OUT_H = 720, 1280
OUT_FPS = 30.0
CROSSFADE_FRAMES = 12

KIT_DIR = '/home/user/repo/brand-identity'
AUDIO_IN = f'{KIT_DIR}/official_music_carefree.mp3'
FINAL_VID = '/home/user/شقة_طريق_ولغا_طابق_رابع_عرض_100.mp4'

font_hero = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 42)
font_title = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 34)
font_sub = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Medium.ttf', 22)
font_badge = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 20)
font_pill = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 18)
font_outro_h = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 28)
font_outro_b = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 22)
font_outro_m = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Medium.ttf', 19)
font_app = ImageFont.truetype(f'{KIT_DIR}/Tajawal-Bold.ttf', 23)

logo_src = Image.open(f'{KIT_DIR}/logo.jpg').convert('RGBA')

def draw_rtl_centered(draw, text, x_center, y, font, fill):
    bb = draw.textbbox((0, 0), text, font=font, direction='rtl', language='ar')
    w = bb[2] - bb[0]
    draw.text((int(x_center - w / 2), int(y)), text, font=font, fill=fill, direction='rtl', language='ar')

def draw_rtl_right(draw, text, x_right, y, font, fill):
    bb = draw.textbbox((0, 0), text, font=font, direction='rtl', language='ar')
    w = bb[2] - bb[0]
    draw.text((int(x_right - w), int(y)), text, font=font, fill=fill, direction='rtl', language='ar')

def make_persistent_layers():
    top_img = Image.new('RGBA', (OUT_W, 140), (0, 0, 0, 0))
    d_top = ImageDraw.Draw(top_img, 'RGBA')
    d_top.rounded_rectangle((28, 36, 692, 128), radius=24, fill=(10, 15, 28, 228), outline=(245, 197, 66, 225), width=2)
    logo_sm = logo_src.resize((74, 74), Image.Resampling.LANCZOS)
    top_img.paste(logo_sm, (606, 45), logo_sm)
    draw_rtl_right(d_top, 'المكتب العقاري الإلكتروني - السويداء  |  العرض رقم 100', 592, 47, font_badge, (245, 197, 66, 255))
    draw_rtl_right(d_top, 'تملك شقة العمر بسعر خيالي  •  واتساب: 0934222900', 592, 83, font_pill, (255, 255, 255, 255))

    bot_img = Image.new('RGBA', (OUT_W, 70), (0, 0, 0, 0))
    d_bot = ImageDraw.Draw(bot_img, 'RGBA')
    specs = [
        'واتساب: 0934222900',
        'الطابق: الرابع',
        'المساحة: 140 م²'
    ]
    pill_widths = [212, 200, 190]
    gap = 12
    total_w = sum(pill_widths) + gap * 2
    curr_x = (OUT_W - total_w) // 2
    for sp, pw in zip(specs, pill_widths):
        d_bot.rounded_rectangle((curr_x, 8, curr_x + pw, 58), radius=14, fill=(10, 15, 28, 225), outline=(245, 197, 66, 185), width=1)
        draw_rtl_centered(d_bot, sp, curr_x + pw // 2, 22, font_pill, (255, 255, 255, 255))
        curr_x += pw + gap

    return np.array(top_img), np.array(bot_img)

def make_hook_card():
    h = 290
    img = Image.new('RGBA', (OUT_W, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    cy = 28
    draw.rounded_rectangle((34, cy, 686, cy + 245), radius=24, fill=(10, 15, 28, 232), outline=(245, 197, 66, 245), width=3)
    draw.rounded_rectangle((150, cy - 22, 570, cy + 22), radius=22, fill=(245, 197, 66, 255))
    draw_rtl_centered(draw, 'العرض رقم 100  •  تملك شقة العمر بسعر خيالي', OUT_W // 2, cy - 14, font_badge, (10, 15, 28, 255))
    draw_rtl_centered(draw, 'شقة سكنية للبيع - سوبر ديلوكس', OUT_W // 2, cy + 38, font_hero, (255, 255, 255, 255))
    draw_rtl_centered(draw, 'طريق ولغا - مفرق كازية المدينة  |  الطابق الرابع', OUT_W // 2, cy + 110, font_outro_b, (245, 197, 66, 255))
    draw_rtl_centered(draw, '140 م²  •  صالون + غرفتين + ماستر  •  إطلالة بانورامية مفتوحة', OUT_W // 2, cy + 172, font_pill, (235, 240, 250, 255))
    return np.array(img), 745

def make_room_card(title, subtitle):
    h = 135
    img = Image.new('RGBA', (OUT_W, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    draw.rounded_rectangle((34, 5, 686, 130), radius=20, fill=(10, 15, 28, 228), outline=(255, 255, 255, 80), width=1)
    draw.rounded_rectangle((662, 23, 672, 112), radius=5, fill=(245, 197, 66, 255))
    draw_rtl_right(draw, title, 646, 21, font_title, (255, 255, 255, 255))
    draw_rtl_right(draw, subtitle, 646, 77, font_sub, (245, 197, 66, 255))
    return np.array(img), 905

def make_outro_card():
    img = Image.new('RGBA', (OUT_W, OUT_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    cy = 95
    draw.rounded_rectangle((32, cy, 688, cy + 1090), radius=28, fill=(10, 15, 28, 245), outline=(245, 197, 66, 255), width=3)
    logo_lg = logo_src.resize((118, 118), Image.Resampling.LANCZOS)
    img.paste(logo_lg, ((OUT_W - 118)//2, cy + 18), logo_lg)

    draw_rtl_centered(draw, 'المكتب العقاري الإلكتروني - السويداء', OUT_W // 2, cy + 148, font_outro_b, (245, 197, 66, 255))
    draw_rtl_centered(draw, 'تملك شقة العمر بسعر خيالي (العرض رقم 100)', OUT_W // 2, cy + 188, font_outro_h, (255, 255, 255, 255))
    draw.line((80, cy + 242, 640, cy + 242), fill=(245, 197, 66, 150), width=2)

    rows = [
        ('الموقع:', 'طريق ولغا - مفرق كازية المدينة'),
        ('الطابق:', 'الرابع (إطلالة بانورامية وخصوصية تامة)'),
        ('المساحة:', '140 م²  |  الكسوة: سوبر ديلوكس'),
        ('التفصيل:', 'صالون + مطبخ + غرفتين نوم + حمام ماستر'),
        ('البلكون الأول:', 'بلكون كبير بإطلالة خضراء مفتوحة لا تُحجب'),
        ('البلكون الثاني:', 'مطل من المطبخ بتهوية وإنارة شمسية ممتازة'),
    ]
    ry = cy + 258
    for lbl, val in rows:
        draw.rounded_rectangle((52, ry, 668, ry + 64), radius=14, fill=(22, 32, 54, 225), outline=(255, 255, 255, 55), width=1)
        draw_rtl_right(draw, lbl, 650, ry + 17, font_outro_b, (245, 197, 66, 255))
        draw_rtl_right(draw, val, 478, ry + 20, font_outro_m, (255, 255, 255, 255))
        ry += 76

    app_y = cy + 725
    draw.rounded_rectangle((52, app_y, 668, app_y + 132), radius=18, fill=(18, 45, 72, 240), outline=(245, 197, 66, 255), width=2)
    draw_rtl_centered(draw, 'حمّل التطبيق لتشاهد جميع العروض لدينا مع الأسعار', OUT_W // 2, app_y + 18, font_app, (245, 197, 66, 255))
    draw_rtl_centered(draw, 'التطبيق الرسمي للمكتب العقاري الإلكتروني - السويداء (APK)', OUT_W // 2, app_y + 58, font_outro_m, (255, 255, 255, 255))
    draw_rtl_centered(draw, 'github.com/hady-albnnai/sweeda-app/releases/latest', OUT_W // 2, app_y + 92, font_pill, (160, 220, 255, 255))

    cta_y = cy + 878
    draw.rounded_rectangle((62, cta_y, 658, cta_y + 64), radius=32, fill=(245, 197, 66, 255))
    draw_rtl_centered(draw, 'للتواصل والاستفسار (واتساب): 0934222900', OUT_W // 2, cta_y + 17, font_outro_b, (10, 15, 28, 255))
    draw_rtl_centered(draw, 'facebook.com/sweedarealestate', OUT_W // 2, cy + 956, font_pill, (205, 215, 230, 255))
    return np.array(img), 0

def blend_patch(bgr, patch_rgba, y0, alpha_mult=1.0, y_shift=0):
    h = patch_rgba.shape[0]
    ty0 = y0 + y_shift
    ty1 = ty0 + h
    if ty1 <= 0 or ty0 >= OUT_H:
        return bgr
    sy0 = max(0, -ty0)
    sy1 = h - max(0, ty1 - OUT_H)
    cy0 = max(0, ty0)
    cy1 = min(OUT_H, ty1)
    sub_rgba = patch_rgba[sy0:sy1, :]
    sub_bgr = bgr[cy0:cy1, :]
    alpha = (sub_rgba[:, :, 3:4].astype(np.float32) / 255.0) * alpha_mult
    fg = sub_rgba[:, :, [2, 1, 0]].astype(np.float32)
    bg = sub_bgr.astype(np.float32)
    bgr[cy0:cy1, :] = (bg * (1.0 - alpha) + fg * alpha).astype(np.uint8)
    return bgr

def make_lut(gamma):
    return np.array([min(255, int(((i / 255.0) ** gamma) * 255)) for i in range(256)], dtype=np.uint8)

LUT_MILD = make_lut(0.88)
LUT_BATH = make_lut(0.76)

SEG_CARDS = {
    'p1': [
        (0.0, 4.8, 'hook', '', '', 'mild'),
        (4.8, 8.5, 'room', 'غرفة النوم الأولى', 'مساحة واسعة وأرضيات بورسلان وإنارة شمسية ساطعة', 'mild'),
        (8.5, 12.8, 'room', 'غرفة النوم الثانية', 'إضاءة طبيعية ممتازة وخصوصية تامة بفضل الارتفاع الطابقي', 'mild'),
        (12.8, 19.5, 'room', 'حمام ماستر + حمام ضيوف', 'كسوة سيراميك وموزاييك حديثة لحد السقف', 'bath'),
        (19.5, 26.0, 'room', 'مدخل الشقة والصالون الرئيسي', 'مساحة 140 م² بتوزيع هندسي مريح وكسوة سوبر ديلوكس', 'mild'),
    ],
    'p2': [
        (0.0, 8.0, 'room', 'ديكورات أسقف مستعارة حديثة', 'تصميم عصري أنيق للأسقف في الصالون والممرات', 'mild'),
        (8.0, 14.2, 'room', 'إنارة شمسية وتشطيب راقٍ', 'توزيع مثالي للغرف مع ديكورات سقفية مميزة', 'mild'),
        (14.2, 17.0, 'room', 'مطبخ أميركي مطل على بلكونين', 'مطل على البلكون الثاني ويوفر تهوية وإنارة من جهتين', 'mild'),
        (17.0, 20.5, 'room', 'بلكون كبير بإطلالة بانورامية مفتوحة', 'إطلالة خضراء علوية كاشفة ومفتوحة بالكامل لا تُحجب', 'mild'),
    ],
}

def main():
    top_rgba, bot_rgba = make_persistent_layers()
    hook_rgba, hook_y0 = make_hook_card()
    outro_rgba, outro_y0 = make_outro_card()

    room_cache = {}
    for seg_name, items in SEG_CARDS.items():
        for st, et, ctype, title, sub, lmode in items:
            if ctype == 'room' and (title, sub) not in room_cache:
                room_cache[(title, sub)] = make_room_card(title, sub)

    seg_names = ['p1', 'p2']
    seg_caps = [cv2.VideoCapture(f'/home/user/msad2_stab/{n}_stab.mp4') for n in seg_names]
    seg_counts = [int(c.get(cv2.CAP_PROP_FRAME_COUNT)) for c in seg_caps]
    outro_frames_count = int(6.0 * OUT_FPS)

    total_frames = sum(seg_counts) - CROSSFADE_FRAMES * (len(seg_names) - 1) + outro_frames_count
    total_dur = total_frames / OUT_FPS
    print(f"Total msad2 frames: {total_frames} ({total_dur:.2f}s)")

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    fade_out_start = max(0, total_dur - 3.0)
    cmd = [
        ffmpeg_exe, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', f'{OUT_W}x{OUT_H}',
        '-r', f'{OUT_FPS}',
        '-i', '-',
        '-i', AUDIO_IN,
        '-t', f'{total_dur:.2f}',
        '-filter_complex', f'[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out_start:.2f}:d=3.0,volume=0.85[a]',
        '-map', '0:v:0',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '21',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        FINAL_VID
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def style_raw_frame(frm, seg_name, local_t):
        items = SEG_CARDS[seg_name]
        active = items[-1]
        for it in items:
            if it[0] <= local_t <= it[1]:
                active = it
                break
        st, et, ctype, title, sub, lmode = active
        if lmode == 'mild':
            frm = cv2.LUT(frm, LUT_MILD)
        elif lmode == 'bath':
            frm = cv2.LUT(frm, LUT_BATH)
        return frm, active

    def add_ui(frm, active, local_t, global_idx):
        st, et, ctype, title, sub, lmode = active
        frm = blend_patch(frm, top_rgba, 0, 1.0, 0)
        frm = blend_patch(frm, bot_rgba, 1045, 1.0, 0)

        in_card_t = local_t - st
        rem_card_t = et - local_t
        if in_card_t < 0.35:
            anim = max(0.0, in_card_t / 0.35)
        elif rem_card_t < 0.30:
            anim = max(0.0, rem_card_t / 0.30)
        else:
            anim = 1.0
        anim_eased = 1.0 - (1.0 - anim) ** 2
        y_shift = int((1.0 - anim_eased) * 22)

        if ctype == 'hook':
            frm = blend_patch(frm, hook_rgba, hook_y0, anim_eased, y_shift)
        else:
            c_rgba, cy0 = room_cache[(title, sub)]
            frm = blend_patch(frm, c_rgba, cy0, anim_eased, y_shift)

        prog_w = int(OUT_W * (global_idx / max(1, total_frames - 1)))
        cv2.rectangle(frm, (0, OUT_H - 8), (OUT_W, OUT_H), (65, 65, 65), -1)
        cv2.rectangle(frm, (OUT_W - prog_w, OUT_H - 8), (OUT_W, OUT_H), (66, 197, 245), -1)
        return frm

    global_idx = 0
    prev_tail = []
    last_good_frame = None

    for s_i, (seg_name, cap, count) in enumerate(zip(seg_names, seg_caps, seg_counts)):
        is_last_seg = (s_i == len(seg_names) - 1)
        f_i = 0
        while True:
            ret, frm = cap.read()
            if not ret:
                break
            local_t = f_i / OUT_FPS
            frm, active = style_raw_frame(frm, seg_name, local_t)
            last_good_frame = frm

            if prev_tail and f_i < len(prev_tail):
                alpha = (f_i + 1) / (len(prev_tail) + 1)
                p_frm, p_act, p_lt = prev_tail[f_i]
                blended = cv2.addWeighted(p_frm, 1.0 - alpha, frm, alpha, 0)
                if alpha < 0.5:
                    out = add_ui(blended, p_act, p_lt, global_idx)
                else:
                    out = add_ui(blended, active, local_t, global_idx)
                proc.stdin.write(out.tobytes())
                global_idx += 1
            elif not is_last_seg and f_i >= count - CROSSFADE_FRAMES:
                if f_i == count - CROSSFADE_FRAMES:
                    prev_tail = []
                prev_tail.append((frm, active, local_t))
            else:
                out = add_ui(frm, active, local_t, global_idx)
                proc.stdin.write(out.tobytes())
                if global_idx in (30, 200, 480, 900, 1300):
                    cv2.imwrite(f'/home/user/msad2_stab/sample_{global_idx}.jpg', out)
                global_idx += 1
            f_i += 1
        cap.release()

    small = cv2.resize(last_good_frame, (180, 320))
    blurred = cv2.GaussianBlur(small, (25, 25), 0)
    bg_outro = (cv2.resize(blurred, (OUT_W, OUT_H)) * 0.42).astype(np.uint8)

    for k in range(outro_frames_count):
        frm = bg_outro.copy()
        lt = k / OUT_FPS
        anim = min(1.0, lt / 0.45)
        anim_eased = 1.0 - (1.0 - anim) ** 2
        y_shift = int((1.0 - anim_eased) * 24)
        frm = blend_patch(frm, outro_rgba, outro_y0, anim_eased, y_shift)
        prog_w = int(OUT_W * (global_idx / max(1, total_frames - 1)))
        cv2.rectangle(frm, (0, OUT_H - 8), (OUT_W, OUT_H), (65, 65, 65), -1)
        cv2.rectangle(frm, (OUT_W - prog_w, OUT_H - 8), (OUT_W, OUT_H), (66, 197, 245), -1)
        proc.stdin.write(frm.tobytes())
        if k == outro_frames_count // 2:
            cv2.imwrite('/home/user/msad2_stab/sample_outro.jpg', frm)
        global_idx += 1

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg exited with {proc.returncode}")
    print(f"Done in {time.time()-t0:.2f}s! Saved to {FINAL_VID}")

if __name__ == '__main__':
    main()
