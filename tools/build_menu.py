# بيبني منيو الكاشير من منيو محصول فاخر الحالي (luxurycrop.site — اتسحب 4 نوفمبر 2026)
# الأسعار والأسماء والعروض والإضافات زي ما هي على الموقع. الـid بتاع كل صنف = نفس id قاعدة بياناتهم، عشان الربط يبقى مباشر.
import io, json, os, subprocess
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
SYS = os.path.join(ROOT, '..', 'luxury-crop-system', 'assets')
OUT = os.path.join(ROOT, 'assets', 'img', 'p')
os.makedirs(OUT, exist_ok=True)
SB = 'https://qckjfyupxwctfizqdbxe.supabase.co/storage/v1/object/public/'

# (القسم، الاسم بالإنجليزي، الأيقونة، نوعه مشروب؟، مجموعة الإضافات)
SECTIONS = [
    ('matcha', 'مشروبات ماتشا', 'Matcha', 'leaf', True, 'lcDefault'),
    ('cold', 'المشروبات الباردة', 'Iced drinks', 'ice', True, 'lcCold'),
    ('hibiscus', 'كركديه', 'Hibiscus', 'leaf', True, 'lcDefault'),
    ('mojito', 'موهيتو', 'Mojitos', 'ice', True, 'lcDefault'),
    ('hot', 'المشروبات الساخنة', 'Hot drinks', 'cup', True, 'lcHot'),
    ('cold-v60', 'V60 بارد', 'Iced V60', 'drip', True, 'lcV60'),
    ('pourover', 'V60 حار', 'Hot V60', 'drip', True, 'lcV60'),
    ('espresso', 'الإسبريسو', 'Espresso', 'cup', True, 'lcDefault'),
    ('bakery', 'المخبوزات والحلا', 'Pastries & desserts', 'cake', False, 'lcBakery'),
    ('section_4682576791b34dea', 'الإفطار الصحي', 'Healthy breakfast', 'leaf', False, 'lcDefault'),
]

# k, الاسم كما على الموقع, الاسم في الكاشير (لو محتاج توضيح), English, السعر, صورة الأطلس أو رابط الصورة
ITEMS = {
    'matcha': [
        ('170300', 'ماتشا كلاسيك', None, 'Classic Matcha', 20, 49),
        ('171003', 'ماتشا توت', None, 'Berry Matcha', 22, 51),
        ('xmrqy5f76796', 'ماتشا فراولة', None, 'Strawberry Matcha', 23, 52),
        ('170302', 'ماتشا لافندر', None, 'Lavender Matcha', 22, 50),
        ('170301', 'ماتشا بِنك', None, 'Pink Matcha', 23, 55),
        ('xmrqy33hc4ym', 'ماتشا كوكنت', None, 'Coconut Matcha', 23, 54),
        ('xmrqxmk1p6dm', 'ماتشا فانيليا', None, 'Vanilla Matcha', 22, 53),
        ('p_5bdedde9365744f6a0a604bc869494ea', 'ماتشا مانجو', None, 'Mango Matcha', 22, SB + 'product-images/p_5bdedde9365744f6a0a604bc869494ea/cover.webp?v=1792259409049'),
    ],
    'cold': [
        ('cold-honey-latte', 'آيس لاتيه بالعسل', None, 'Iced Honey Latte', 20, 'local:img/products/iced-honey-latte.jpeg'),
        ('170298', 'آيس لاتيه كراميل', None, 'Iced Caramel Latte', 18, 43),
        ('170294', 'سبانش لاتيه بارد', None, 'Iced Spanish Latte', 18, 42),
        ('170292', 'آيس أمريكانو', None, 'Iced Americano', 15, 'local:img/products/iced-americano-from-client.png'),
        ('cold-iced-tea', 'آيس تي', None, 'Iced Tea', 16, 47),
        ('170293', 'لاتيه بارد', None, 'Iced Latte', 17, 41),
        ('170299', 'آيس شوكلت', None, 'Iced Chocolate', 19, 44),
        ('170291', 'الفريدو', None, 'Freddo', 15, 5),
        ('xmqvi9e4v6gk', 'حليب فراولة (أطفال)', None, 'Strawberry Milk (Kids)', 10, 45),
        ('cold-rose-milk', 'حليب روز ( أطفال )', 'حليب روز (أطفال)', 'Rose Milk (Kids)', 10, 46),
    ],
    'hibiscus': [
        ('170305', 'كركديه كلاسيك', None, 'Classic Hibiscus', 15, 56),
        ('170306', 'كركديه روز', None, 'Rose Hibiscus', 16, 57),
        ('xmqvihblo15y', 'كركديه توت', None, 'Berry Hibiscus', 17, 58),
        ('xmrqyg3yq41s', 'كركديه فراولة', None, 'Strawberry Hibiscus', 17, 59),
    ],
    'mojito': [
        ('170303', 'موهيتو توت أزرق', None, 'Blueberry Mojito', 18, 60),
        ('170304', 'موهيتو خوخ', None, 'Peach Mojito', 18, 61),
    ],
    'hot': [
        ('170283', 'لاتيه', None, 'Latte', 17, 28),
        ('170282', 'كابتشينو', None, 'Cappuccino', 16, 27),
        ('170281', 'فلات وايت', None, 'Flat White', 15, 26),
        ('170280', 'كورتادو', None, 'Cortado', 14, 25),
        ('170278', 'إسبريسو ميكاتو', None, 'Espresso Macchiato', 14, 23),
        ('170288', 'لاتيه كراميل', None, 'Caramel Latte', 18, 'local:img/products/hot-caramel-latte-from-client.png'),
        ('170284', 'سبانش لاتيه', None, 'Spanish Latte', 18, 29),
        ('170279', 'أمريكانو حار', None, 'Hot Americano', 15, 24),
        ('hot-saudi-coffee', 'قهوة سعودية', None, 'Saudi Coffee', 6, 37),
        ('hot-turkish-coffee', 'قهوة تركية', None, 'Turkish Coffee', 10, SB + 'product-images/hot-turkish-coffee/cover.webp?v=1792259466489'),
        ('176540', 'قهوة اليوم محصول إثيوبي', None, 'Ethiopian Coffee of the Day', 9, 34),
        ('p_721e212b29bf48de88edd214a21c9379', 'قهوة تركية + حليب', None, 'Turkish Coffee with Milk', 15, SB + 'product-images/p_721e212b29bf48de88edd214a21c9379/cover.webp?v=1792259551506'),
    ],
    'cold-v60': [
        ('xmqvhwyx556j', 'كولد برو', None, 'Cold Brew', 24, 11),
        ('xmqvhqdyy46s', 'بيرياس بيرو', 'بيرياس بيرو (بارد)', 'Berrias Peru — Iced', 20, 40),
        ('xmrqzetgjap', 'وهاج اثيوبيا', 'وهاج اثيوبيا (بارد)', 'Wahaj Ethiopia — Iced', 20, 40),
        ('xmqvho8v82pn', 'سادو اثيوبيا بارد', None, 'Sado Ethiopia — Iced', 20, 40),
        ('xmqvhpbg564z', 'بينسا اثيوبيا بارد', None, 'Bensa Ethiopia — Iced', 22, 40),
        ('xmrqz90ecj4', 'لاهرموسا كولومبيا بارد', None, 'La Hermosa Colombia — Iced', 22, 40),
        ('p_877016ac0a0d4ad3867d073debdd88ea', 'يمني (فاخر)', 'يمني فاخر (بارد)', 'Yemeni Premium — Iced', 22, SB + 'product-images/p_877016ac0a0d4ad3867d073debdd88ea/cover.webp?v=1791185569344'),
        ('p_74ae5dc3707e4f2199865049a52c4e37', 'باشن فروت ( فاخر )', 'باشن فروت فاخر (بارد)', 'Passion Fruit Premium — Iced', 22, SB + 'product-images/p_74ae5dc3707e4f2199865049a52c4e37/cover.webp?v=1791185586435'),
    ],
    'pourover': [
        ('192502', 'بينسا اثيوبيا', 'بينسا اثيوبيا (حار)', 'Bensa Ethiopia — Hot', 20, 1),
        ('192998', 'بيرياس بيرو', 'بيرياس بيرو (حار)', 'Berrias Peru — Hot', 18, 2),
        ('xmrqz7bp85ct', 'وهاج اثيوبيا', 'وهاج اثيوبيا (حار)', 'Wahaj Ethiopia — Hot', 18, 4),
        ('170273', 'سادو اثيوبيا حار', None, 'Sado Ethiopia — Hot', 18, 0),
        ('xmrqz5hni2k1', 'لاهرموسا كولومبيا حار', None, 'La Hermosa Colombia — Hot', 20, 3),
        ('p_19445b044a2e4b52ac6c913db99c76d5', 'يمني (فاخر)', 'يمني فاخر (حار)', 'Yemeni Premium — Hot', 21, SB + 'product-images/p_19445b044a2e4b52ac6c913db99c76d5/cover.webp?v=1791186604223'),
        ('p_b9ee3f64bb0c45f1855b3038a27aa7fe', 'باشن فروت', 'باشن فروت (حار)', 'Passion Fruit — Hot', 21, SB + 'product-images/p_b9ee3f64bb0c45f1855b3038a27aa7fe/cover.webp?v=1791187359455'),
    ],
    'espresso': [
        ('180992', 'إسبريسو', None, 'Espresso', 12, 22),
    ],
    'bakery': [
        ('170311', 'ماتيلدا كيك شوكلاته', None, 'Matilda Chocolate Cake', 20, 15),
        ('170310', 'كوكنت مانجو', None, 'Coconut Mango Cake', 20, 16),
        ('xmqvitfx45ss', 'تشيز توت أزرق', None, 'Blueberry Cheesecake', 22, 20),
        ('dessert-red-berry-cheesecake', 'تشيز توت أحمر', None, 'Red Berry Cheesecake', 22, 21),
        ('170313', 'تراميسو', None, 'Tiramisu', 20, 18),
        ('201080', 'سينابون كلاسيك', None, 'Classic Cinnamon Roll', 16, 19),
        ('170315', 'تشيز كيك مانجو', None, 'Mango Cheesecake', 20, 17),
        ('170309', 'كوكيز فانيليا', None, 'Vanilla Cookie', 10, 13),
        ('193000', 'كوكيز شوكلت', None, 'Chocolate Cookie', 10, 14),
    ],
    'section_4682576791b34dea': [
        ('p_c2f89ae664c4463a93d376709c87bc00', 'جرانولا  كلاسيك', 'جرانولا كلاسيك', 'Classic Granola', 18, SB + 'product-images/p_c2f89ae664c4463a93d376709c87bc00/cover.webp?v=1793194411924'),
        ('p_11f3f7634e96463fa5655536a6cd4c39', 'جرانولا توت', None, 'Berry Granola', 18, SB + 'product-images/p_11f3f7634e96463fa5655536a6cd4c39/cover.webp?v=1793194817895'),
        ('p_884c12f4a4634dcaa48af0a3c3036a3d', 'جرانولا فراولة', None, 'Strawberry Granola', 18, SB + 'product-images/p_884c12f4a4634dcaa48af0a3c3036a3d/cover.webp?v=1793194880008'),
    ],
}

# العروض (offers) — نفس الـid اللي في قاعدة بياناتهم
OFFERS = [
    ('c1', 'عرض LUXURY CROP', 'Luxury Crop Deal', 'قهوة اليوم + كوكيز', 16, 19, True, SB + 'offer-images/c1/cover.webp?v=1792154103623'),
    ('c3', 'تجربة المختصة', 'Specialty Tasting', 'وهاج اثيوبيا حار + ماتيلدا كيك شوكلاته', 34, 38, True, 'local:img/offers/combo-specialty.webp'),
    ('c2', 'فطور صحي', 'Healthy Breakfast Deal', 'جرانولا فاخر + زبادي يوناني + قطع فواكه', 15, 18, False, SB + 'offer-images/c2/cover.webp?v=1793194956026'),
    ('c4', 'قعدة اثنين', 'Table for Two', '٢ سبانش لاتيه حار + تراميسو', 50, 56, True, 'local:img/offers/combo-for-two.webp'),
]

# الإضافات — نفس id الإضافة في قاعدة بياناتهم (addon_hot_0 …)
ADDONS = {
    'lcHot': ('Extras', 'الإضافات', [('addon_hot_0', 'شوت إسبريسو زيادة', 'Extra shot', 4, '+SHOT'), ('addon_hot_1', 'حليب نباتي (لوز/شوفان)', 'Plant milk', 5, 'PLANT MILK'), ('addon_hot_2', 'سيرب (كراميل/فانيليا)', 'Syrup', 3, 'SYRUP'), ('addon_hot_3', 'كوكيز فانيليا جنب القهوة', 'Vanilla cookie on the side', 10, '+COOKIE')]),
    'lcCold': ('Extras', 'الإضافات', [('addon_cold_0', 'شوت إسبريسو زيادة', 'Extra shot', 4, '+SHOT'), ('addon_cold_1', 'حليب نباتي (لوز/شوفان)', 'Plant milk', 5, 'PLANT MILK'), ('addon_cold_2', 'سيرب (كراميل/فانيليا)', 'Syrup', 3, 'SYRUP')]),
    'lcV60': ('Extras', 'الإضافات', [('addon_pourover_0', 'ماء فوار جانبي', 'Sparkling water', 3, '+SPARKLING'), ('addon_pourover_1', 'كوكيز فانيليا جنب القهوة', 'Vanilla cookie on the side', 10, '+COOKIE')]),
    'lcBakery': ('Extras', 'الإضافات', [('addon_bakery_0', 'صوص شوكولاتة', 'Chocolate sauce', 3, '+CHOC'), ('addon_bakery_1', 'كريمة', 'Cream', 3, '+CREAM')]),
    'lcDefault': ('Extras', 'الإضافات', [('addon__default_0', 'كوكيز فانيليا', 'Vanilla cookie', 10, '+COOKIE'), ('addon__default_1', 'كوكيز شوكلت', 'Chocolate cookie', 10, '+CHOC COOKIE')]),
}
# أسماء إضافات قسم V60 البارد في قاعدة بياناتهم ليها id منفصل — نفس الخيار
ALIASES = {'addon_cold-v60_0': 'addon_pourover_0', 'addon_cold-v60_1': 'addon_pourover_1'}

ATLAS = os.path.join(SYS, 'img', 'atlases')
SIZE = 360


def save_tile(src, pid):
    out = os.path.join(OUT, pid + '.jpg')
    if isinstance(src, int):
        im = Image.open(os.path.join(ATLAS, 'products-%02d.webp' % (src // 6 + 1))).convert('RGB')
        c, r = src % 3, (src % 6) // 3
        tile = im.crop((c * 400, r * 400, c * 400 + 400, r * 400 + 400))
    elif src.startswith('local:'):
        tile = Image.open(os.path.join(SYS, src[6:])).convert('RGB')
    else:
        raw = os.path.join(ROOT, 'tools', 'cache', pid + '.webp')
        os.makedirs(os.path.dirname(raw), exist_ok=True)
        if not os.path.exists(raw):
            subprocess.run(['curl', '-s', '-m', '40', '--ssl-no-revoke', '-o', raw, src], check=True)
        tile = Image.open(raw).convert('RGB')
    w, h = tile.size
    s = min(w, h)
    tile = tile.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((SIZE, SIZE), Image.LANCZOS)
    tile.save(out, quality=82, optimize=True, progressive=True)
    return 'assets/img/p/' + pid + '.jpg'


def safe_id(k):
    return k.replace('-', '_')


cats, products = [], []
for sid, ar, en, ic, drink, grp in SECTIONS:
    cats.append({'id': sid, 'ar': ar, 'en': en, 'ic': ic})
    for k, n, pos_ar, en_name, price, img in ITEMS[sid]:
        products.append({'id': k, 'cat': sid, 'ar': pos_ar or n.strip(), 'online': n, 'en': en_name, 'price': price,
                         'img': save_tile(img, safe_id(k)), 'drink': drink, 'mods': [grp], 'r': {}})
cats.append({'id': 'offers', 'ar': 'العروض', 'en': 'Offers', 'ic': 'gift'})
for oid, n, en_name, desc, price, was, drink, img in OFFERS:
    products.append({'id': oid, 'cat': 'offers', 'ar': n, 'online': n, 'en': en_name, 'desc': desc, 'price': price, 'was': was,
                     'img': save_tile(img, 'offer_' + oid), 'drink': drink, 'mods': [], 'r': {}, 'offer': 1})

mods = {}
for gid, (gen, gar, opts) in ADDONS.items():
    mods[gid] = {'en': gen, 'ar': gar, 'one': 0, 'opts': [{'id': i, 'ar': a, 'en': e, 'd': d, 'k': kk} for i, a, e, d, kk in opts]}

data = {'source': 'luxurycrop.site — 4 Nov 2026', 'cats': cats, 'products': products, 'mods': mods, 'aliases': ALIASES}
js = '/* منيو محصول فاخر — اتولّد من tools/build_menu.py (نفس أسعار وأسماء الموقع الحالي، ونفس id قاعدة البيانات) */\nwindow.DARJ_MENU = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n'
io.open(os.path.join(ROOT, 'assets', 'menu.js'), 'w', encoding='utf-8').write(js)
print(len(cats), 'sections ·', len(products), 'items')
