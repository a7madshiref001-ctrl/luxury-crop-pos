# بيجيب محرك DARJ من darj-pos ويبني صفحات كاشير محصول فاخر (نفس الكود، بإعدادات وهوية ومنيو العميل)
import io, os, re, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.abspath(os.path.join(ROOT, '..', 'darj-pos'))
V = '4'

for f in ['darj.css', 'darj.js', 'app.js', 'kds.js', 'link.js', 'kiosk.js']:
    shutil.copy(os.path.join(SRC, 'assets', f), os.path.join(ROOT, 'assets', f))
os.makedirs(os.path.join(ROOT, 'assets', 'audio'), exist_ok=True)
for f in ['order-up-bell.mp3', 'ORDER_BELL_LICENSE.txt']:
    shutil.copy(os.path.join(SRC, 'assets', 'audio', f), os.path.join(ROOT, 'assets', 'audio', f))
os.makedirs(os.path.join(ROOT, 'assets', 'vendor'), exist_ok=True)
vendor = os.path.join(ROOT, '..', 'luxury-crop-system', 'assets', 'vendor', 'supabase-2.116.0.js')
shutil.copy(vendor, os.path.join(ROOT, 'assets', 'vendor', 'supabase-2.116.0.js'))

FONTS = re.compile(r'<link rel="preconnect" href="https://fonts.googleapis.com">\s*<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\s*<link href="https://fonts.googleapis.com[^>]*>')
PAGES = [('app.html', 'محصول فاخر · الكاشير'), ('kds.html', 'محصول فاخر · التحضير'), ('screen.html', 'محصول فاخر · طلبك جاهز'), ('kiosk.html', 'محصول فاخر · اطلب من هنا')]
for page, title in PAGES:
    s = io.open(os.path.join(SRC, page), encoding='utf-8').read()
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s)
    s = s.replace('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">', '<link rel="icon" href="assets/brand/logo-mark.png" type="image/png">\n<link rel="apple-touch-icon" href="assets/brand/logo-mark.png">')
    s = FONTS.sub('', s)
    s = re.sub(r'<link rel="stylesheet" href="assets/darj.css\?v=\d+">', f'<link rel="stylesheet" href="assets/darj.css?v={V}">\n<link rel="stylesheet" href="assets/brand.css?v={V}">', s)
    s = s.replace('<meta name="theme-color" content="#F3EFE7">', '<meta name="theme-color" content="#F4F0E8">')
    s = re.sub(r'<script src="assets/img.js\?v=\d+"></script>', f'<script src="assets/config.js?v={V}"></script>\n<script src="assets/menu.js?v={V}"></script>', s)
    s = re.sub(r'\?v=\d+"', f'?v={V}"', s)
    if page == 'app.html':
        s = s.replace(f'<script src="assets/link.js?v={V}"></script>', f'<script src="assets/link.js?v={V}"></script>\n<script src="assets/connect.js?v={V}"></script>')
    s = s.replace('<span class="demo-tag">Demo</span>\n', '')
    io.open(os.path.join(ROOT, page), 'w', encoding='utf-8').write(s)
print('synced from darj-pos')
