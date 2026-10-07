from django import template
from django.utils import translation

register = template.Library()

FA_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
EN_DIGITS = '0123456789'

RAW_PAIRS = [
    # Navigation & General UI
    ("Home", "صفحه اصلی"),
    ("Shop", "فروشگاه"),
    ("Categories", "دسته‌بندی‌ها"),
    ("Cart", "سبد خرید"),
    ("Wishlist", "علاقه‌مندی‌ها"),
    ("Profile", "پروفایل"),
    ("My Account", "حساب من"),
    ("Login / Register", "ورود / ثبت‌نام"),
    ("Login", "ورود"),
    ("Logout", "خروج"),
    ("Register", "ثبت‌نام"),
    ("Dashboard", "پنل مدیریت"),
    ("Search in thousands of products...", "جستجو در میان هزاران کالا..."),
    ("Search products, brands, categories...", "جستجو در میان محصولات، برندها و دسته‌ها..."),
    ("Search", "جستجو"),
    ("Fast express shipping", "ارسال سریع به سراسر ایران"),
    ("Special Offers", "پیشنهادات شگفت‌انگیز"),
    ("Special Offer", "پیشنهاد ویژه"),
    ("Top Deals CTA", "تخفیف‌های ویژه فصل — تا ۵۰٪ تخفیف روی برترین کالاها! هم‌اکنون خرید کنید ←"),
    ("Special Autumn Deals — Up to 50% Off! Shop Now →", "تخفیف‌های ویژه پاییزه — تا ۵۰٪ تخفیف! هم‌اکنون خرید کنید ←"),
    ("All Products", "همه محصولات"),
    ("View All", "مشاهده همه ←"),
    ("View All →", "مشاهده همه ←"),
    ("Fast shipping, authenticity guarantee & 7-day returns", "ارسال سریع، ضمانت اصالت و بازگشت ۷ روزه"),
    ("About Us", "درباره ما"),
    ("Contact Us", "تماس با ما"),
    ("FAQ", "پرسش‌های متداول"),
    ("Privacy Policy", "حریم خصوصی"),
    ("Terms of Service", "شرایط و قوانین"),
    ("Shipping Policy", "شیوه‌های ارسال"),
    ("Return Policy", "شرایط بازگشت کالا"),
    ("Cookie Policy", "سیاست کوکی‌ها"),
    ("All rights reserved", "تمامی حقوق مادی و معنوی محفوظ است."),
    ("All rights reserved.", "تمامی حقوق مادی و معنوی محفوظ است."),
    ("Fast and reliable shipping", "ارسال سریع و مطمئن"),
    ("Express delivery and nationwide shipping", "تحویل اکسپرس در سراسر کشور"),
    ("Product Authenticity Guarantee", "ضمانت اصالت کالا"),
    ("Guaranteed 100% original products", "تضمین اورجینال بودن تمام محصولات"),
    ("Secure Payment", "پرداخت امن"),
    ("Safe banking gateway with dynamic passwords", "درگاه بانکی معتبر و ایمن با رمز پویا"),
    ("7-Day Return Guarantee", "۷ روز ضمانت بازگشت"),
    ("Easy, hassle-free returns", "مرجوعی آسان، بدون دردسر"),
    ("Quick Links", "دسترسی سریع"),
    ("Order Tracking", "پیگیری سفارشات"),
    ("Help & Policies", "راهنما و قوانین"),
    ("Newsletter Subscription", "عضویت در خبرنامه"),
    ("Newsletter description", "از تخفیف‌های ویژه و محصولات جدید باخبر شوید. هر هفته، فقط بهترین‌ها."),
    ("Your email address...", "آدرس ایمیل شما..."),
    ("Subscribe", "عضویت"),
    ("Your Shopping Cart", "سبد خرید شما"),
    ("Subtotal:", "جمع کل:"),
    ("View Cart", "مشاهده سبد خرید"),
    ("Proceed to Checkout", "ادامه سفارش"),
    ("Back to Top", "بازگشت به بالا"),
    ("Close", "بستن"),
    ("Skip to main content", "پرش به محتوای اصلی"),
    ("Currency Toman", "تومان"),
    ("Toman", "تومان"),
    ("Tomans", "تومان"),
    ("Working Hours Value", "۲۴ ساعته، ۷ روز هفته"),
    ("Shop Now", "خرید کنید"),
    ("Special Autumn Deals", "تخفیف‌های ویژه پاییزه"),
    ("Cookie Consent Message", "ما برای بهبود تجربه خرید و تحلیل ترافیک از کوکی‌ها استفاده می‌کنیم. با کلیک بر روی قبول، شما با سیاست حفظ حریم خصوصی و کوکی‌ها موافقت می‌کنید."),
    ("Accept", "قبول و ادامه"),
    ("Essential Only", "فقط ضروری"),
    ("Decline", "رد کردن"),
    ("Processing...", "در حال پردازش..."),
    ("Please wait...", "لطفاً منتظر بمانید..."),
    ("Contact Address", "تهران، خیابان ولیعصر، برج نوآوری، طبقه ۶"),
    ("Support Phone", "۰۲۱-۸۸۸۸۹۹۹۹"),
    ("Support Email", "support@shop.local"),
    ("Page Not Found", "صفحه مورد نظر یافت نشد (۴۰۴)"),
    ("404 Title", "صفحه مورد نظر شما پیدا نشد!"),
    ("404 Description", "ممکن است آدرس وارد شده تغییر کرده باشد یا صفحه حذف شده باشد."),
    ("Back to Homepage", "بازگشت به صفحه اصلی فروشگاه"),
    ("Menu", "منو"),

    # Homepage Hero & Slogans
    ("A Different Shopping Experience", "تجربه خریدی متفاوت"),
    ("Fast delivery in Tehran and nationwide", "ارسال سریع تهران و شهرستانها"),
    ("Fast express delivery nationwide", "ارسال سریع به سراسر کشور"),
    ("Authenticity Guaranteed", "ضمانت اصالت کالا"),
    ("Secure payment with banking gateway", "پرداخت امن با درگاه بانکی"),
    ("24/7 Support", "پشتیبانی ۲۴ ساعته"),
    ("View Special Discounts", "مشاهده تخفیفهای ویژه"),
    ("Express Shipping", "ارسال اکسپرس"),
    ("Authenticity Guarantee", "ضمانت اصالت"),
    ("Welcome to our store", "به فروشگاه ما خوش آمدید"),
    ("Safe, fast, and enjoyable shopping for digital goods and home appliances; with authenticity guarantee and nationwide delivery.", "خرید مطمئن، سریع و لذتبخش کالای دیجیتال و لوازم خانگی؛ با ضمانت اصالت کالا و ارسال به سراسر کشور."),
    ("Start Shopping", "شروع خرید"),
    ("Store Services", "خدمات فروشگاه"),
    ("Fast & Reliable Delivery", "ارسال سریع و مطمئن"),
    ("Express Tehran, nationwide delivery", "اکسپرس تهران، ارسال به سراسر کشور"),
    ("100% genuine & verified products", "تضمین اورجینال بودن همه محصولات"),
    ("Certified banking gateway with OTP", "درگاه بانکی معتبر با رمز پویا"),
    ("24/7 Customer Care", "پاسخگویی در تمام ساعات شبانهروز"),
    ("Shop by Category", "خرید بر اساس دستهبندی"),
    ("Popular Categories", "دستهبندیهای محبوب"),
    ("All Categories", "همه دستهها"),
    ("View Products", "مشاهده محصولات"),
    ("Categories not added yet.", "دستهبندیها هنوز اضافه نشدهاند."),
    ("Today's Hot Deals", "پیشنهادهای داغ امروز"),
    ("Limited discounts on selected popular products; act before time runs out.", "تخفیفهای محدود روی منتخبی از محصولات پرطرفدار؛ تا پایان فرصت، وقت دارید."),
    ("All Offers", "همه پیشنهادها"),
    ("Off", "تخفیف"),
    ("Add to Cart", "افزودن به سبد خرید"),
    ("Add", "افزودن"),
    ("+ Add", "+ افزودن"),
    ("Why buy from us? Thousands shop with confidence every day: from genuine warranty to fast delivery, everything for a seamless experience.", "چرا خرید از ما؟ چون هزاران نفر هر روز با اطمینان از ما خرید میکنند: از گارانتی اصالت تا ارسال سریع، همهچیز برای یک خرید بیدغدغه."),
    ("7-Day Return Guarantee", "۷ روز ضمانت بازگشت"),
    ("Editor's Choice", "انتخاب سردبیر"),
    ("Store Highlights", "منتخبهای فروشگاه"),
    ("Products that are most popular and offer great value.", "محصولاتی که بیش از همه محبوباند و ارزش خرید بالایی دارند."),
    ("No products to display.", "محصولی برای نمایش وجود ندارد."),
    ("Best Sellers", "پرفروشترینها"),
    ("Customers' Most Popular Choices", "محبوبترین انتخابهای مشتریان"),
    ("View Best Sellers", "مشاهده پرفروشها"),
    ("New Arrivals", "تازه رسیدهها"),
    ("Newest Products", "جدیدترین محصولات"),
    ("View Newest", "مشاهده جدیدترینها"),
    ("Trusted Brands", "برندهای معتبر"),
    ("Shop Brands You Know", "از برندهایی که میشناسید بخرید"),
    ("Direct partnership with world-renowned brands.", "نمایندگی و ضمانت محصولات برندهای شناختهشده دنیا."),
    ("Customer Satisfaction", "رضایت مشتریان"),
    ("What Customers Say", "مشتریها چه میگویند؟"),
    ("Verified Purchase", "خرید تأییدشده"),
    ("Quick Buy", "خرید سریع"),
    ("Bestseller", "پرفروش"),
    ("Featured", "ویژه"),
    ("New", "جدید"),
    ("Verified Buyer", "خریدار تأیید شده"),
    ("Verified Buyer", "خریدار تأییدشده"),

    # Catalog & Shop Filters
    ("Product Catalog", "گالری محصولات"),
    ("Filter Products", "فیلتر محصولات"),
    ("Clear All", "حذف همه"),
    ("Brands", "برندها"),
    ("All Brands", "همه برندها"),
    ("Price Range (Toman)", "محدوده قیمت (تومان)"),
    ("From", "از"),
    ("To", "تا"),
    ("Apply Filters", "اعمال فیلتر"),
    ("In-Stock Only", "فقط کالاهای موجود"),
    ("On Sale Only", "فقط کالاهای تخفیف‌دار"),
    ("Sort By:", "مرتب‌سازی بر اساس:"),
    ("Sort by:", "مرتب‌سازی بر اساس:"),
    ("Newest", "جدیدترین"),
    ("Price: Low to High", "ارزان‌ترین"),
    ("Price: High to Low", "گران‌ترین"),
    ("Best Selling", "پرفروش‌ترین"),
    ("Most Popular", "محبوب‌ترین"),
    ("Biggest Discount", "بیشترین تخفیف"),
    ("Highest Rated", "بالاترین امتیاز"),
    ("Minimum Rating", "حداقل امتیاز"),
    ("All", "همه"),
    ("& Up", "به بالا"),
    ("In-Stock Only", "فقط کالاهای موجود در انبار"),
    ("Apply Price Filter", "اعمال فیلتر قیمت"),
    ("Showing", "نمایش"),
    ("Products", "کالا"),
    ("For query", "برای عبارت"),
    ("Quick Buy", "افزودن سریع به سبد"),
    ("No products match your selected filters.", "کالایی مطابق فیلترهای انتخابی یافت نشد."),
    ("No products match your selected filters.", "هیچ محصولی با معیارهای انتخابی شما یافت نشد!"),
    ("Please try different keywords or adjust your filter criteria.", "لطفاً کلمات کلیدی دیگری را جستجو نمایید یا فیلترهای اعمال شده را تغییر دهید."),
    ("View All Products", "مشاهده تمامی کالاها"),
    ("First", "ابتدا"),
    ("Previous", "قبلی"),
    ("Next", "بعدی"),
    ("Last", "انتها"),
    ("View Details", "مشاهده جزئیات"),
    ("Search Results for", "نتایج جستجوی"),
    ("Brand", "برند"),
    ("Products of Brand", "محصولات برند"),
    ("Search:", "جستجوی:"),

    # Product Detail
    ("Click to enlarge", "برای بزرگ‌نمایی کلیک کنید"),
    ("Category:", "دسته‌بندی:"),
    ("Brand:", "برند:"),
    ("SKU:", "کد شناسه کالا (SKU):"),
    ("Customer Reviews", "دیدگاه خریداران"),
    ("Select Variant (Color / Storage / Size):", "انتخاب تنوع محصول (رنگ / حافظه / اندازه):"),
    ("Your Price:", "قیمت نهایی برای شما:"),
    ("In Stock", "موجود در انبار"),
    ("Out of Stock", "ناموجود"),
    ("Quantity:", "تعداد:"),
    ("7-Day Money Back Guarantee", "۷ روز ضمانت بازگشت وجه"),
    ("Express Delivery in Shortest Time", "تحویل اکسپرس در کوتاه‌ترین زمان"),
    ("Safe & Secure Payment", "پرداخت امن و مطمئن"),
    ("100% Authenticity Guarantee", "تضمین ۱۰۰٪ اصالت کالا"),
    ("Specifications & Product Review", "مشخصات و نقد و بررسی محصول"),
    ("Product Overview:", "توضیحات تکمیلی:"),
    ("Technical Specifications:", "جدول مشخصات فنی:"),
    ("Customer Reviews (", "دیدگاه‌های مشتریان ("),
    ("out of 5", "از ۵"),
    ("Write a Review", "ثبت دیدگاه جدید برای این کالا"),
    ("Your Rating (1 to 5 stars):", "امتیاز شما (از ۱ تا ۵ ستاره):"),
    ("5 Stars - Excellent", "۵ ستاره - عالی"),
    ("4 Stars - Good", "۴ ستاره - خوب"),
    ("3 Stars - Average", "۳ ستاره - معمولی"),
    ("2 Stars - Poor", "۲ ستاره - ضعیف"),
    ("1 Star - Very Poor", "۱ ستاره - بسیار ضعیف"),
    ("Review Title:", "عنوان دیدگاه:"),
    ("Your Review:", "متن نظر شما:"),
    ("Submit Review", "ثبت دیدگاه"),
    ("Please sign in to your account to submit a review.", "برای ثبت دیدگاه و امتیاز ابتدا باید وارد حساب کاربری خود شوید."),
    ("sign in to your account", "وارد حساب کاربری خود شوید"),
    ("No reviews yet. Be the first to review this product!", "هنوز دیدگاهی برای این کالا ثبت نشده است. اولین نفری باشید که نظر می‌دهد!"),
    ("Related & Recommended Products", "کالاهای مرتبط و پیشنهادی"),
    ("Product Price:", "قیمت کالا:"),
    ("Variant:", "تنوع:"),

    # Cart & Checkout
    ("YOUR SELECTION", "انتخاب شما"),
    ("Items", "قلم کالا"),
    ("Product", "محصول"),
    ("Unit Price", "قیمت واحد"),
    ("Quantity", "تعداد"),
    ("Total", "جمع کل"),
    ("Order Summary", "خلاصه سبد سفارش"),
    ("Items Subtotal:", "جمع کل اقلام:"),
    ("Shipping Cost:", "هزینه ارسال:"),
    ("Free", "رایگان"),
    ("Total Payable:", "مبلغ قابل پرداخت:"),
    ("Your shopping cart is currently empty!", "سبد خرید شما در حال حاضر خالی است!"),
    ("Return to Shop and Explore Products", "بازگشت به فروشگاه و مشاهده محصولات"),
    ("1. Cart", "۱. سبد خرید"),
    ("2. Shipping & Payment", "۲. اطلاعات ارسال و پرداخت"),
    ("3. Bank Gateway & Confirmation", "۳. درگاه بانکی و تأیید"),
    ("Select Shipping Address", "انتخاب آدرس تحویل سفارش"),
    ("+ Add New Address", "+ افزودن آدرس جدید"),
    ("You haven't saved any shipping addresses yet.", "شما هنوز آدرس پستی ثبت نکرده‌اید."),
    ("Add First Shipping Address", "ثبت اولین آدرس پستی"),
    ("Select Shipping Method", "انتخاب شیوه ارسال"),
    ("Express Post", "پست پیشتاز"),
    ("24 to 48 business hours nationwide delivery", "تحویل ۲۴ تا ۴۸ ساعت کاری به سراسر کشور"),
    ("Tipax Express", "تیپاکس اکسپرس"),
    ("Home delivery with full item insurance", "تحویل درب منزل با بیمه کامل کالا"),
    ("Pay on Delivery", "پس‌کرایه"),
    ("Select Payment Method", "انتخاب روش پرداخت"),
    ("Online Bank Payment", "پرداخت آنلاین اینترنتی"),
    ("Instant connection to national banking gateway (Saman / ZarinPal)", "اتصال به درگاه معتبر بانکی کشور (سامان / زرین‌پال)"),
    ("Cash on Delivery (POS)", "پرداخت در محل (کارتخوان سیار)"),
    ("Payment upon receiving package at your door (Tehran only)", "پرداخت هنگام دریافت بسته درب منزل (ویژه تهران)"),
    ("Order Notes (Optional):", "یادداشت سفارش (اختیاری):"),
    ("Additional delivery details, recipient time preference...", "توضیحات تکمیلی تحویل، زمان مناسب دریافت و..."),
    ("Order Invoice", "فاکتور نهایی سفارش"),
    ("Tax / VAT:", "مالیات و عوارض:"),
    ("Pay & Place Order", "پرداخت و ثبت نهایی سفارش"),
    ("Place Order", "ثبت نهایی سفارش"),
    ("Order Confirmation", "تأیید سفارش"),
    ("Order Success Title", "سفارش شما با موفقیت ثبت شد!"),
    ("Order Number:", "شماره سفارش:"),
    ("Tracking Code:", "کد پیگیری:"),

    # Accounts & Authentication
    ("Sign In to Your Account", "ورود به حساب کاربری"),
    ("Mobile Number or Email:", "شماره موبایل یا ایمیل:"),
    ("Password:", "رمز عبور:"),
    ("Remember Me", "مرا به خاطر بسپار"),
    ("Forgot Password?", "فراموشی رمز عبور؟"),
    ("Sign In", "ورود به حساب"),
    ("Don't have an account? Sign Up", "حساب کاربری ندارید؟ ثبت‌نام کنید"),
    ("Create an Account", "ثبت‌نام در فروشگاه"),
    ("First Name:", "نام:"),
    ("Last Name:", "نام خانوادگی:"),
    ("Phone Number:", "شماره تماس:"),
    ("Email Address:", "آدرس ایمیل:"),
    ("Confirm Password:", "تکرار رمز عبور:"),
    ("I accept the terms and conditions.", "قوانین و شرایط خرید از سایت را می‌پذیرم."),
    ("Register Account", "ثبت‌نام و ایجاد حساب"),
    ("Already have an account? Sign In", "قبلاً ثبت‌نام کرده‌اید؟ وارد شوید"),
    ("Account Information", "اطلاعات حساب کاربری"),
    ("Order History", "تاریخچه سفارش‌ها"),
    ("My Addresses", "آدرس‌های من"),
    ("Change Password", "تغییر رمز عبور"),
    ("Current Password:", "رمز عبور فعلی:"),
    ("New Password:", "رمز عبور جدید:"),
    ("Save Changes", "ذخیره تغییرات"),
    ("Edit Profile", "ویرایش اطلاعات"),
    ("Your Wishlist is Empty", "لیست علاقه‌مندی‌های شما خالی است"),

    # Static Policies & About & Contact
    ("About Our Store", "درباره فروشگاه ما"),
    ("Contact Our Specialists", "ارتباط و تماس با کارشناسان فروشگاه"),
    ("We are ready to answer all your questions and feedback promptly.", "پاسخگوی تمامی سؤالات، پیشنهادات و پیگیری‌های شما در کوتاه‌ترین زمان هستیم"),
    ("Head Office Address:", "آدرس دفتر مرکزی:"),
    ("Direct Contact Number:", "شماره تماس مستقیم:"),
    ("Support Email Address:", "آدرس ایمیل پشتیبانی:"),
    ("Working Hours:", "ساعات کاری و پاسخگویی:"),
    ("Full Name:", "نام و نام خانوادگی شما:"),
    ("Phone Number (Optional):", "شماره تماس (اختیاری):"),
    ("Subject:", "موضوع پیام:"),
    ("Your Message:", "متن پیام شما:"),
    ("Send Message", "ارسال پیام"),
    ("Frequently Asked Questions", "پرسش‌های متداول و راهنما"),
    ("Terms and Conditions", "قوانین و مقررات"),
    ("Privacy Policy", "سیاست حریم خصوصی"),
    ("Shipping Policies", "رویه ارسال سفارشات"),
    ("Return Policies", "رویه بازگردانی کالا"),
    ("Cookie Policies", "سیاست کوکی‌ها"),

    # Banners in Database
    ("Flagships of the Digital World, Direct & Guaranteed", "پرچم‌داران دنیای دیجیتال، بدون واسطه و با گارانتی معتبر"),
    ("iPhone 16 Pro Max, Galaxy S24 Ultra & the latest laptops with express nationwide delivery", "آیفون ۱۶ پرو مکس، گلکسی اس ۲۴ اولترا و جدیدترین لپ‌تاپ‌های دنیا با ارسال فوری و تحویل اکسپرس"),
    ("View Selected Products", "مشاهده محصولات منتخب"),
    ("Latest Smart Gadgets 2026", "جدیدترین گجت‌های هوشمند ۲۰۲۶"),
    ("Up to 30% off all tech accessories and tools", "تا ۳۰٪ تخفیف روی تمامی لوازم جانبی و ابزارهای تکنولوژی"),
    ("View Offers", "مشاهده تخفیف‌ها"),
    ("Unrivaled Hi-Fi Sound Quality", "کیفیت صدای بی‌نظیر های‌فای"),
    ("Top professional headphones & speakers with warranty", "بهترین هدفون‌ها و اسپیکرهای حرفه‌ای با ضمانت تعویض"),
    ("Shop Audio Systems", "خرید سیستم صوتی"),
    ("Tech & Luxury Home Appliances Festival", "جشنواره فصل فناوری و لوازم خانگی لوکس"),
    ("Free shipping on orders above 500,000 Tomans with code WELCOME10", "ارسال رایگان برای تمام سفارش‌های بالای ۵۰۰ هزار تومان با کد تخفیف WELCOME10"),
    ("Special Deals", "خرید شگفت‌انگیز"),

    # Categories in Database (all 83 categories)
    ("Digital Goods", "کالای دیجیتال"),
    ("Mobile", "موبایل"),
    ("Mobile Phones", "گوشی موبایل"),
    ("Mobile Accessories", "لوازم جانبی موبایل"),
    ("Laptops & Computers", "لپ‌تاپ و کامپیوتر"),
    ("Laptops", "لپ‌تاپ"),
    ("Monitors", "مانیتور"),
    ("Keyboards & Mice", "کیبورد و ماوس"),
    ("Hardware & Storage", "قطعات و ذخیره‌سازی"),
    ("Tablets & E-Readers", "تبلت و کتابخوان"),
    ("Tablets", "تبلت"),
    ("E-Readers", "کتابخوان"),
    ("Audio & Video", "صوتی و تصویری"),
    ("Headphones & Headsets", "هدفون و هدست"),
    ("Wireless Headphones", "هدفون بی‌سیم"),
    ("Speakers", "اسپیکر"),
    ("TVs & Projectors", "تلویزیون و پروژکتور"),
    ("Cameras & Photography", "دوربین و فیلم‌برداری"),
    ("Cameras", "دوربین"),
    ("Action Cameras", "دوربین اکشن"),
    ("Modems & Networking", "مودم و شبکه"),
    ("Smartwatches & Wearables", "ساعت و پوشیدنی هوشمند"),
    ("Smartwatches", "ساعت هوشمند"),
    ("Smart Bands", "مچ‌بند هوشمند"),
    ("Wearables", "لوازم پوشیدنی"),
    ("Gaming", "گیمینگ"),
    ("Gaming Consoles", "کنسول بازی"),
    ("Controllers & Accessories", "دسته و لوازم جانبی"),
    ("Gaming Gear", "تجهیزات گیمینگ"),
    ("Gaming Chairs", "صندلی گیمینگ"),
    ("Home Appliances", "لوازم خانگی"),
    ("Kitchen", "آشپزخانه"),
    ("Coffee & Tea Makers", "قهوه‌ساز و چای‌ساز"),
    ("Food Processors & Blenders", "غذاساز و مخلوط‌کن"),
    ("Air Fryers & Microwaves", "سرخ‌کن و مایکروویو"),
    ("Small Electric Appliances", "لوازم برقی کوچک"),
    ("Washing & Laundry", "شست‌وشو"),
    ("Washing Machines", "ماشین لباسشویی"),
    ("Dishwashers", "ظرفشویی"),
    ("Cleaning & Hygiene", "نظافت و پاکیزگی"),
    ("Vacuum Cleaners", "جاروبرقی"),
    ("Robot Vacuums", "جاروی رباتیک"),
    ("Climate & Air Quality", "آب و هوا"),
    ("Air Purifiers", "تصفیه هوا"),
    ("Water Purifiers", "تصفیه آب"),
    ("Fans & Humidifiers", "پنکه و بخور"),
    ("Health & Beauty", "زیبایی و سلامت"),
    ("Hair & Beard Care", "مراقبت مو و ریش"),
    ("Hair Dryers & Straighteners", "سشوار و اتو مو"),
    ("Shavers & Trimmers", "ریش‌تراش و تریمر"),
    ("Skincare", "مراقبت پوست"),
    ("Health & Massage", "سلامت و ماساژ"),
    ("Massagers", "ماساژور"),
    ("Scales & Health Tools", "ترازو و ابزار سلامت"),
    ("Fashion & Apparel", "مد و پوشاک"),
    ("Men's", "مردانه"),
    ("Women's", "زنانه"),
    ("Bags & Backpacks", "کیف و کوله"),
    ("Accessories", "اکسسوری"),
    ("Sports & Travel", "ورزش و سفر"),
    ("Fitness Equipment", "تجهیزات تناسب اندام"),
    ("Travel Bags & Suitcases", "کیف و چمدان مسافرتی"),
    ("Camping & Nature", "کمپینگ و طبیعت‌گردی"),
    ("Tents & Sleeping Bags", "چادر و کیسه خواب"),
    ("Thermos & Cooking Gear", "فلاسک و تجهیزات پخت‌وپز"),
    ("Stationery & Art", "لوازم تحریر و هنر"),
    ("Writing Instruments", "نوشت‌افزار"),
    ("Notebooks & Paper", "دفتر و کاغذ"),
    ("Drawing & Painting", "طراحی و نقاشی"),
    ("Office Supplies", "لوازم اداری و بایگانی"),
    ("Automotive Tools", "ابزار و خودرو"),
    ("Hand & Power Tools", "ابزار دستی و برقی"),
    ("Power Tools", "ابزار برقی"),
    ("Hand Tools", "ابزار دستی"),
    ("Car Care & Accessories", "لوازم و تجهیزات خودرو"),
    ("Car Audio & Video", "سیستم صوتی و تصویری خودرو"),
    ("Car Care & Wax", "شوینده و واکس خودرو"),
    ("Safety & Security Equipment", "تجهیزات ایمنی و نظارتی"),
    ("Security Cameras", "دوربین مداربسته"),
    ("Alarms & Sensors", "دزدگیر و سنسور"),

    # Products in Database (all 36 products)
    ("Apple iPhone 16 Pro Max 256GB", "گوشی موبایل اپل مدل iPhone 16 Pro Max ظرفیت ۲۵۶ گیگابایت"),
    ("Samsung Galaxy S24 Ultra 256GB", "گوشی موبایل سامسونگ مدل Galaxy S24 Ultra ظرفیت ۲۵۶ گیگابایت"),
    ("Xiaomi 14T Pro 512GB", "گوشی موبایل شیائومی مدل 14T Pro ظرفیت ۵۱۲ گیگابایت"),
    ("Anker PowerCore 20000mAh Fast Charging Power Bank", "پاوربانک انکر مدل PowerCore 20000 میلی‌آمپر با شارژ سریع"),
    ("Anker 65W GaN 3-Port Wall Charger", "شارژر دیواری انکر مدل 65W GaN سه‌پورت"),
    ("Apple MacBook Air 13-inch M3 512GB", "لپ‌تاپ اپل مدل MacBook Air 13 اینچ M3 ظرفیت ۵۱۲ گیگابایت"),
    ("ASUS Zenbook 14 OLED Ultra 7 Laptop", "لپ‌تاپ ایسوس مدل Zenbook 14 OLED اولترا ۷"),
    ("Samsung Odyssey G5 27-inch Gaming Monitor", "مانیتور گیمینگ سامسونگ مدل Odyssey G5 سایز ۲۷ اینچ"),
    ("Logitech MX Master 3S Wireless Mouse", "ماوس بی‌سیم لاجیتک مدل MX Master 3S"),
    ("Logitech MX Keys Mini Mechanical Keyboard", "کیبورد مکانیکال لاجیتک مدل MX Keys Mini"),
    ("Samsung T7 1TB External SSD", "حافظه SSD اکسترنال سامسونگ مدل T7 ظرفیت ۱ ترابایت"),
    ("Apple iPad Air 11-inch M2 128GB", "تبلت اپل مدل iPad Air 11 اینچ M2 ظرفیت ۱۲۸ گیگابایت"),
    ("Samsung Galaxy Tab S9 FE 128GB", "تبلت سامسونگ مدل Galaxy Tab S9 FE ظرفیت ۱۲۸ گیگابایت"),
    ("Apple AirPods Pro 2nd Gen USB-C Wireless Earbuds", "هندزفری بی‌سیم اپل مدل AirPods Pro نسخه ۲ با پورت USB-C"),
    ("Sony WH-1000XM5 Wireless Headphones", "هدفون بی‌سیم سونی مدل WH-1000XM5"),
    ("JBL Charge 5 Bluetooth Speaker", "اسپیکر بلوتوثی جی‌بی‌ال مدل Charge 5"),
    ("Xiaomi TV A2 55-inch Smart TV", "تلویزیون هوشمند شیائومی مدل TV A2 سایز ۵۵ اینچ"),
    ("GoPro HERO12 Black Action Camera", "دوربین اکشن گوپرو مدل HERO12 Black"),
    ("Canon EOS R50 Mirrorless Camera with 18-45mm Lens", "دوربین بدون آینه کانن مدل EOS R50 همراه لنز 18-45mm"),
    ("Apple Watch Ultra 2 49mm Smartwatch", "ساعت هوشمند اپل مدل Watch Ultra 2 سایز ۴۹ میلی‌متری"),
    ("Samsung Galaxy Watch 6 Classic 47mm Smartwatch", "ساعت هوشمند سامسونگ مدل Galaxy Watch 6 Classic سایز ۴۷ میلی‌متری"),
    ("Xiaomi Smart Band 9 Fitness Tracker", "مچ‌بند هوشمند شیائومی مدل Smart Band 9"),
    ("Sony PlayStation 5 Slim Disc Edition", "کنسول بازی سونی مدل PlayStation 5 Slim نسخه دیسک‌خور"),
    ("Sony DualSense Wireless Controller for PS5", "دسته بازی سونی مدل DualSense Wireless برای PS5"),
    ("Razer BlackWidow V4 X Mechanical Gaming Keyboard", "کیبورد مکانیکال گیمینگ ریزر مدل BlackWidow V4 X"),
    ("DeLonghi Dedica EC685 Espresso Maker", "اسپرسوساز دلونگی مدل Dedica EC685"),
    ("Philips Airfryer XXL Series 7 Oil-Free Fryer", "سرخ‌کن بدون روغن فیلیپس مدل Airfryer XXL سری ۷"),
    ("Philips HR3655 Blender with 2L Glass Jar", "مخلوط‌کن فیلیپس مدل HR3655 با پارچ شیشه‌ای ۲ لیتری"),
    ("Bosch Series 6 9kg Washing Machine WGA252ZIR", "ماشین لباسشویی بوش مدل WGA252ZIR سری ۶ ظرفیت ۹ کیلوگرم"),
    ("Dyson V12 Detect Slim Cordless Vacuum", "جاروی شارژی دایسون مدل V12 Detect Slim"),
    ("Xiaomi Robot Vacuum S10 Plus", "جاروی رباتیک شیائومی مدل Robot Vacuum S10 Plus"),
    ("Philips Series 3000i AC2930 Air Purifier", "تصفیه هوا فیلیپس مدل AC2930 سری ۳۰۰۰i"),
    ("Braun Series 9 Pro Shaver with Clean & Charge Station", "ریش‌تراش براون مدل Series 9 Pro با پایه شارژ و اتوکلین"),
    ("Relax Pro Cordless Neck Massager with Soothing Heat", "ماساژور گردنی شارژی مدل Relax Pro با گرمای ملایم"),
    ("Xiaomi Electric Scooter 4 Pro", "اسکوتر برقی شیائومی مدل Electric Scooter 4 Pro"),
    ("Nike Brasilia 25L Training Backpack", "کوله‌پشتی ورزشی نایک مدل Brasilia ظرفیت ۲۵ لیتر"),

    # Brands in Database (all 24 brands)
    ("Anker", "انکر"),
    ("Apple", "اپل"),
    ("HP", "اچ‌پی"),
    ("ASUS", "ایسوس"),
    ("Braun", "براون"),
    ("Bose", "بوز"),
    ("Bosch", "بوش"),
    ("JBL", "جی‌بی‌ال"),
    ("Dyson", "دایسون"),
    ("DeLonghi", "دلونگی"),
    ("Razer", "ریزر"),
    ("Samsung", "سامسونگ"),
    ("Sony", "سونی"),
    ("Xiaomi", "شیائومی"),
    ("Philips", "فیلیپس"),
    ("Logitech", "لاجیتک"),
    ("Lenovo", "لنوو"),
    ("Nike", "نایک"),
    ("Panasonic", "پاناسونیک"),
    ("PlayStation", "پلی‌استیشن"),
    ("Canon", "کانن"),
    ("Crucial", "کروز"),
    ("Garmin", "گارمین"),
    ("GoPro", "گوپرو"),

    # Site Settings & Brand Identity
    ("Avangard Online Store", "فروشگاه اینترنتی آوانگارد"),
    ("Easy Shopping, Unbeatable Prices, Guaranteed Authenticity", "خرید آسان، قیمت بی‌رقیب، اصالت قطعی کالا"),
    ("5th Floor, Avangard Tech Tower, Valiasr St, Vanak Sq, Tehran", "تهران، میدان ونک، خیابان ولیعصر، برج فناوری آوانگارد، طبقه ۵"),
    ("Saturday to Wednesday 9:00 - 18:00 | Thursday 9:00 - 14:00", "شنبه تا چهارشنبه ۹ الی ۱۸ - پنجشنبه ۹ الی ۱۴"),
    ("Our online store was established to provide the best products with guaranteed authenticity and unbeatable prices.", "فروشگاه اینترنتی ما با هدف ارائه برترین محصولات با اصالت تضمین‌شده و بهترین قیمت آغاز به کار نموده است."),
    ("We respect our users' privacy and protect personal data using the highest security standards.", "ما به حریم خصوصی تمامی کاربران احترام می‌گذاریم و اطلاعات شما را با بالاترین استانداردهای امنیتی محافظت می‌کنیم."),
    ("Using this store's services constitutes full acceptance of e-commerce terms and regulations.", "استفاده از خدمات این فروشگاه به معنای پذیرش کامل قوانین و مقررات تجارت الکترونیک است."),
    ("Orders in Tehran are delivered via Express Courier, and provincial orders via Express Post and Tipax within 24-48 business hours.", "ارسال سفارشات تهران با پیک اکسپرس و شهرستان‌ها با پست پیشتاز و تیپاکس ظرف ۲۴ تا ۴۸ ساعت کاری انجام می‌پذیرد."),
    ("Returns are accepted within 7 days of delivery if seals are intact or in case of verified technical defect.", "امکان مرجوعی کالا تا ۷ روز پس از تحویل در صورت عدم باز شدن پلمپ یا اشکال فنی کالا وجود دارد."),
    ("This website uses standard cookies to enhance user experience and maintain your cart state.", "این وب‌سایت برای بهبود تجربه کاربری و حفظ وضعیت سبد خرید از کوکی‌های استاندارد استفاده می‌کند."),

    # Order & Payment Statuses
    ("Awaiting Payment", "در انتظار پرداخت"),
    ("Payment Gateway", "درگاه پرداخت"),
    ("Paid & Confirmed", "پرداخت شده و تایید شده"),
    ("Processing & Packaging", "در حال آماده‌سازی و بسته‌بندی"),
    ("Handed over to Courier", "تحویل به شرکت حمل و نقل"),
    ("Delivered to Customer", "تحویل داده شده به مشتری"),
    ("Cancelled", "لغو شده"),
    ("Returned", "مرجوع شده"),
    ("Refunded", "استرداد وجه انجام شد"),
    ("Successful & Confirmed", "موفق و تایید شده"),
    ("Failed with Error", "ناموفق با خطا"),
    ("Cancelled by Customer", "انصراف توسط خریدار"),

    # Variations of headings and actions
    ("Add to Wishlist", "افزودن به علاقه‌مندی‌ها"),
    ("Add to Wishlist", "افزودن به علاقهمندیها"),
    ("New Arrivals", "تازه رسیده‌ها"),
    ("New Arrivals", "تازه رسیدهها"),
    ("Newest Products", "جدیدترین محصولات"),
    ("View Newest", "مشاهده جدیدترین‌ها"),
    ("View Newest", "مشاهده جدیدترینها"),
    ("What Our Customers Say", "مشتری‌ها چه می‌گویند؟"),
    ("What Our Customers Say", "مشتریها چه میگویند؟"),
    ("Customer Reviews", "رضایت مشتریان"),
    ("Shop Brands You Know", "از برندهایی که می‌شناسید بخرید"),
    ("Shop Brands You Know", "از برندهایی که میشناسید بخرید"),
    ("Direct partnership with world-renowned brands.", "نمایندگی و ضمانت محصولات برندهای شناخته‌شده دنیا."),
    ("Direct partnership with world-renowned brands.", "نمایندگی و ضمانت محصولات برندهای شناختهشده دنیا."),

    # Reviews & Testimonials
    ("Real Titanium", "تیتانیوم واقعیه"),
    ("The weight is noticeable, but the build quality is extraordinary.", "وزنش محسوسه ولی کیفیت ساخت فوق‌العاده‌ست."),
    ("Kourosh Jamshidi", "کوروش جمشیدی"),

    ("Brilliant Display", "نمایشگر درخشان"),
    ("Crystal clear even under direct sunlight. Arrived in perfect packaging.", "زیر نور آفتاب هم کاملاً واضحه. بسته‌بندی سالم رسید."),
    ("Parisa Naderi", "پریسا نادری"),

    ("Great for Flights", "برای پرواز عالیه"),
    ("Battery really lasts 30 hours. The carrying case is great too.", "باتری واقعاً ۳۰ ساعت جواب میده. کیف حمل خوبی هم داره."),
    ("Saman Rostami", "سامان رستمی"),

    ("Accurate Mapping", "نقشه‌برداری دقیق"),
    ("I control it with the app; cleans the home without any mess.", "با اپ کنترلش می‌کنم، توی خانه کثیف کاری هم نمی‌کنه."),
    ("Akbar Valizadeh", "اکبر ولیزاده"),

    ("Smooth Shave Without Irritation", "اصلاح بدون تحریک"),
    ("My skin is sensitive, but with this shaver I have zero irritation.", "پوستم حساسه ولی با این ریش‌تراش هیچ سوزشی ندارم."),
    ("Shahin Abbasi", "شاهین عباسی"),

    ("Best Budget Pick", "بهترین انتخاب اقتصادی"),
    ("At this price point, its performance matches flagships. Fast charging is phenomenal.", "با این قیمت عملکردی در حد پرچمدارها داره. شارژ سریعش معرکه‌ست."),
    ("Reza Sharifi", "رضا شریفی"),

    ("Great Value", "ارزش خرید"),
    ("With 15 bar pressure, the difference compared to cheap machines is obvious.", "با ۱۵ بار فشار، تفاوتش با دستگاه‌های ارزون کاملاً مشخصه."),
    ("Navid Parsa", "نوید پارسا"),

    ("Home Cleaning Transformed", "نظافت خانه متحول شد"),
    ("Laser illumination reveals invisible dust! Suction power is very strong.", "لامپ لیزر گرد و خاک نامرئی رو نشون میده! مکشش خیلی قویه."),
    ("Fatemeh Yousefi", "فاطمه یوسفی"),

    ("For Professional Work", "برای کار حرفه‌ای"),
    ("MagSpeed scrolling is a miracle in spreadsheets. Superb ergonomics.", "اسکرول MagSpeed توی اکسل معجزه می‌کنه. ارگونومی عالی."),
    ("Pouya Asadi", "پویا اسدی"),

    ("Comfort and Quality", "راحتی و کیفیت"),
    ("Very lightweight and stays secure in ears. Sleek charging case.", "خیلی سبکه و توی گوش نمی‌افته. کیس شارژ مرتبه."),
    ("Mina Ahmadi", "مینا احمدی"),

    ("Light and Silent", "سبک و بی‌صدا"),
    ("Flawless for design and everyday work. The chassis feels premium.", "برای طراحی و کار روزمره بی‌نقصه. بدنه‌اش خوش‌دسته."),
    ("Aida Naghibi", "آیدا نقیبی"),

    ("High Value for Money", "ارزش خرید بالا"),
    ("Upgraded from 13 Pro; speaker clarity and build quality are clearly superior.", "از ۱۳ پرو آپگرید کردم، صدای اسپیکر و کیفیت ساخت تفاوت واضحی داره."),
    ("Amir Rezaei", "امیر رضایی"),

    ("For Pro Athletics", "برای ورزش حرفه‌ای"),
    ("Battery easily lasts a marathon run, and the screen is clear under direct sun.", "باتریش برای دوی ماراتن کافیه و نمایشگر زیر نور خورشید هم واضحه."),
    ("Sahar Abdi", "سحر عبدی"),

    ("Excellent Battery", "باتری عالی"),
    ("I work a full day without needing the charger. The display is fantastic too.", "یک روز کامل کار می‌کنم بدون شارژر. صفحه‌اش هم عالیه."),
    ("Farbod Rezaei", "فربد رضایی"),

    ("Light and Practical", "سبک و کاربردی"),
    ("Great for sleep tracking and steps, and battery actually lasts 20 days.", "برای پایش خواب و قدم‌ها عالیه و باتریش واقعاً ۲۰ روزه."),
    ("Hasti Kazemi", "هستی کاظمی"),

    ("Best Phone I've Owned", "بهترین گوشی‌ای که داشتم"),
    ("Camera quality is extraordinary and battery lasts a full day. Shipping was fast too.", "کیفیت دوربین فوق‌العاده‌ست و باتری برای یک روز کامل کافیه. ارسال هم سریع بود."),
    ("Sara Mohammadi", "سارا محمدی"),

    ("Excellent", "عالی"),
    ("Seamless integration with Mac and iPhone.", "برای مک و آیفون هماهنگی کامل داره."),
    ("Hamed Nouri", "حامد نوری"),

    ("Good but Pricey", "خوب اما گرون"),
    ("The phone is great, though expensive. Shopping on this store was a great experience.", "گوشی عالیه ولی قیمتش بالاست. خودِ خرید از این سایت تجربه خوبی بود."),
    ("Negar Karimi", "نگار کریمی"),

    ("Cafe-Quality Espresso at Home", "اسپرسوی کافه‌ای در خانه"),
    ("Crema and aroma are unbeatable. Slim profile fits nicely on any counter.", "کرما و طعمش حرف نداره. طراحی باریکش روی کابینت جا میشه."),
    ("Shirin Mahdavi", "شیرین مهدوی"),

    ("Light and Powerful", "سبک و قوی"),
    ("Great for hard floors and rugs, very easy to store away.", "برای ماکرو و فرش عالیه، جمع کردنش هم راحته."),
    ("Babak Rahimi", "بابک رحیمی"),

    ("Crispy Fries Without Oil!", "سیب‌زمینی بدون روغن!"),
    ("Kids love it, and our kitchen oil usage was cut in half. Very easy to clean.", "بچه‌ها عاشقش شدن و مصرف روغن خونه نصف شد. تمیز کردنش هم آسونه."),
    ("Zahra Amini", "زهرا امینی"),

    ("Fast Shipping", "ارسال سریع"),
    ("Delivered in two days, factory sealed and pristine. Time to game!", "دو روزه رسید، پلمپ و سالم. الان وقت بازی کردنه!"),
    ("Behnam Sadeghi", "بهنام صادقی"),

    ("Incredible Noise Canceling", "نویز کنسلینگ فوق‌العاده"),
    ("Can't hear a sound on the subway! Audio fidelity is outstanding.", "توی مترو هیچ صدایی نمی‌شنوم! کیفیت صدا هم بی‌نظیره."),
    ("Arash Tehrani", "آرش تهرانی"),

    ("No More Wrist Strain", "دست درد نمی‌گیره"),
    ("After hours of computer work, my wrist no longer aches.", "بعد از ساعت‌ها کار با کامپیوتر، دیگه مچ دستم درد نمی‌گیره."),
    ("Maryam Soltani", "مریم سلطانی"),

    ("Unbelievable Sound Power", "قدرت صدای باورنکردنی"),
    ("Superb for outdoors and parties; waterproof build gives peace of mind.", "برای بیرون و پارتی عالیه و ضدآب بودنش خیال‌آسوده."),
    ("Siavash Kiani", "سیاوش کیانی"),

    ("Best Headphones on the Market", "بهترین هدفون بازار"),
    ("Noise cancelation beats every headphone I've had, and comfort is superb.", "نویز کنسلینگش از هر هدفونی که داشتم بهتره و راحتیش عالیه."),
    ("Kiana Moradi", "کیانا مرادی"),

    ("Effortless City Commuting", "رفت‌وآمد شهری راحت"),
    ("No more getting stuck in traffic on my way to work. Braking is rock solid.", "برای شرکت رفتن دیگه ترافیک نمی‌بینم. ترمزش مطمئنه."),
    ("Danial Azizi", "دانیال عزیزی"),

    ("Perfect for Students", "برای دانشجوها عالیه"),
    ("I take notes with Apple Pencil. Lightweight and very easy to carry around.", "با اپل پنسیل یادداشت‌برداری می‌کنم. وزنش سبکه و راحت حمل میشه."),
    ("Niloufar Ahmadi", "نیلوفر احمدی"),

    ("Solid and Complete", "خوب و کامل"),
    ("Great choice for watching movies and web browsing. S-Pen included.", "برای فیلم دیدن و وب‌گردی انتخاب خوبیه. قلمش هم همراهشه."),
    ("Yaser Mahmoudi", "یاسر محمودی"),

    ("200MP Zoom is Mind-Blowing", "زوم ۲۰۰ مگاپیکسل باورنکردنیه"),
    ("Exceptional for pro mobile photography, and the S-Pen is super handy.", "برای عکاسی حرفه‌ای عالیه، قلم هم خیلی کاربردیه."),
    ("Mohammad Hosseini", "محمد حسینی"),

    ("Leica Camera is Superb", "دوربین لایکا عالی"),
    ("Night shots look stunning. Handset stays cool under load.", "عکس‌های شب خیلی خوب می‌شن. دستم گرم نمی‌کنه."),
    ("Elham Ghasemi", "الهام قاسمی"),

    ("Great for Pets", "برای حیوانات خونگی"),
    ("Picks up cat hair thoroughly. Very quiet operation.", "موی گربه رو خوب جمع می‌کنه. صداش کمه."),
    ("Lida Farhadi", "لیدا فرهادی"),

    ("Next-Gen Gaming Experience", "تجربه بازی نسل جدید"),
    ("Game load speeds are astonishing. The DualSense controller feels like magic.", "سرعت لود بازی‌ها باورنکردنیه. کنترلر دالسنس حس متفاوتی داره."),
    ("Alireza Karimi", "علیرضا کریمی"),
]


def normalize_key(s):
    if not s:
        return ''
    return (
        str(s)
        .replace('\u200c', '')
        .replace('\u200b', '')
        .replace('\ufeff', '')
        .replace('‌', '')
        .replace(' ', '')
        .replace('\t', '')
        .replace('\n', '')
        .replace('\r', '')
        .replace('ي', 'ی')
        .replace('ك', 'ک')
        .replace('هٔ', 'ه')
        .lower()
    )


# Build bidirectional dictionaries
TRANSLATIONS = {}
TRANSLATIONS_LOWER = {}
TRANSLATIONS_NORM = {}

CUSTOM_EN = {
    "Currency Toman": "Toman",
    "Currency Toman Short": "Toman",
}

for en, fa in RAW_PAIRS:
    display_en = CUSTOM_EN.get(en, en)
    entry = {"en": display_en, "fa": fa}
    TRANSLATIONS[en] = entry
    TRANSLATIONS[fa] = entry
    TRANSLATIONS_LOWER[en.lower()] = entry
    TRANSLATIONS_LOWER[fa.lower()] = entry
    TRANSLATIONS_NORM[normalize_key(en)] = entry
    TRANSLATIONS_NORM[normalize_key(fa)] = entry


def lookup_translation(key, lang='fa'):
    if key is None:
        return ''
    key_str = str(key).strip()
    if not key_str:
        return ''

    target = 'fa' if (lang and str(lang).lower().startswith('fa')) else 'en'

    # Direct match
    if key_str in TRANSLATIONS:
        return TRANSLATIONS[key_str].get(target, key_str)

    # Lowercase match
    k_low = key_str.lower()
    if k_low in TRANSLATIONS_LOWER:
        return TRANSLATIONS_LOWER[k_low].get(target, key_str)

    # Normalized match (handles spaces, half-spaces, Arabic vs Persian chars)
    k_norm = normalize_key(key_str)
    if k_norm in TRANSLATIONS_NORM:
        return TRANSLATIONS_NORM[k_norm].get(target, key_str)

    return key_str


@register.simple_tag(takes_context=True)
def tr(context, key):
    request = context.get('request') if context else None
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if not lang:
        lang = translation.get_language() or 'fa'
    return lookup_translation(key, lang)


@register.filter(name='tr')
def tr_filter(key, lang=None):
    if not lang:
        lang = translation.get_language() or 'fa'
    return lookup_translation(key, lang)


@register.filter(name='toman')
def toman(value, lang=None):
    """Formats a price with thousands separators (e.g. 98500000 -> 98,500,000 or ۹۸٬۵۰۰٬۰۰۰)."""
    if value is None or value == '':
        return '0'
    if not lang:
        lang = translation.get_language() or 'fa'

    raw = (
        str(value)
        .replace(',', '')
        .replace('٬', '')
        .replace('تومان', '')
        .replace('Toman', '')
        .replace(' ', '')
        .strip()
    )
    try:
        number = int(float(raw))
    except (ValueError, TypeError):
        return value

    negative = number < 0
    grouped = f"{abs(number):,}"

    if lang and str(lang).lower().startswith('fa'):
        grouped = grouped.replace(',', '٬')
        persian = grouped.translate(str.maketrans(EN_DIGITS, FA_DIGITS))
        return ('-' + persian) if negative else persian
    return ('-' + grouped) if negative else grouped


@register.filter(name='currency')
def currency(value, lang=None):
    """Outputs Toman or تومان based on language."""
    if not lang:
        lang = translation.get_language() or 'fa'
    if lang and str(lang).lower().startswith('fa'):
        return 'تومان'
    return 'Toman'


@register.filter(name='fa_num')
def fa_num(value):
    if value is None or value == '':
        return '۰'
    s = str(value)
    return s.translate(str.maketrans(EN_DIGITS, FA_DIGITS))


@register.filter(name='num')
def num_filter(value, lang=None):
    if value is None or value == '':
        return ''
    if not lang:
        lang = translation.get_language() or 'fa'
    s = str(value)
    if lang and str(lang).lower().startswith('fa'):
        return s.translate(str.maketrans(EN_DIGITS, FA_DIGITS))
    return s.translate(str.maketrans(FA_DIGITS, EN_DIGITS))
