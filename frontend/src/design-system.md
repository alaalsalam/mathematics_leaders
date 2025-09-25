# Math Leaders Design System (Draft)

## 1. Brand Identity Summary

| Element | Description |
|--------|-------------|
| **Brand Essence** | تعليمي، محفّز، يزرع في الطالب الشعور بأنه قائد في الرياضيات. |
| **Tone** | رسمي مائل إلى الحيوية؛ يجمع بين الطابع المؤسسي والتفاعل المرح. |
| **Visual Motifs** | التاج والسيوف (الريادة), النخلة (النمو), رموز رياضية (التحدي والمعرفة). |
| **Animation Philosophy** | حركات خفيفة وسلسة (ease-in-out) تدعم الفهم ولا تشتت الانتباه. |

## 2. Palette

مستقاة بصريًا من شعار "زعماء الرياضيات" مع ألوان داعمة.

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-primary` | `#0F8A3E` | الأخضر الأساسي (الأزرار الرئيسية، الروابط المهمة). |
| `--color-primary-strong` | `#0B6C30` | حالات hover/active للأخضر. |
| `--color-primary-soft` | `#D3E8DC` | خلفيات ناعمة للأقسام المرتبطة بالأخضر. |
| `--color-secondary` | `#C8A03B` | الذهبي (العناوين، الحواف المميّزة، الرموز). |
| `--color-secondary-soft` | `#EAD8A2` | خلفيات باهتة للأقسام الثانوية. |
| `--color-accent` | `#0D6E8C` | لون بارد للتباين و CTA الثانوية. |
| `--color-accent-soft` | `#D1ECF4` | خلفية للتنبيهات الباردة. |
| `--color-neutral-900` | `#1A1F16` | النص الداكن في الوضع الفاتح. |
| `--color-neutral-500` | `#4A4E45` | نصوص ثانوية. |
| `--color-neutral-100` | `#F7F4EE` | خلفية فاتحة دافئة. |
| `--color-surface-elevated` | `#FFFFFF` | بطاقات، حاويات. |
| `--color-success` | `#22C55E` | إشعارات النجاح. |
| `--color-warning` | `#FACC15` | تنبيهات/تحذيرات. |
| `--color-danger` | `#EF4444` | الأخطاء. |
| `--color-night-900` | `#0C1319` | الخلفية الأساسية للوضع الداكن. |
| `--color-night-700` | `#15202B` | بطاقات في الوضع الداكن. |
| `--color-night-400` | `#2E3A46` | حدود في الوضع الداكن. |
| `--color-night-100` | `#D9E1E5` | نصوص مساعدة/حدود فاتحة في الوضع الداكن. |

## 3. Typography

| Usage | Arabic font | Latin fallback | Weights |
|-------|-------------|----------------|---------|
| Display / Hero | "Cairo", sans-serif | "Poppins", sans-serif | 700–800 |
| Body / UI | "Noto Sans Arabic", sans-serif | "Inter", sans-serif | 400–600 |
| Numbers | inherit | inherit | استخدم `tabular-nums` للحفاظ على المحاذاة. |

سيتم تحميل الخطوط عبر Google Fonts من خلال `src/assets/main.css`.

## 4. Component Foundations

### Buttons
- **Primary:** خلفية `--color-primary`, نص أبيض, ظل بسيط, انتقال على hover إلى `--color-primary-strong` مع رفع 2px.
- **Secondary:** حدود ذهبية مع خلفية شفافة، نص أخضر.
- **Ghost:** نص بلون العلامة فقط مع تأثير alpha عند hover.

### Cards
- نصف قطر 20px، ظل خفيف (0 16px 32px rgba(0,0,0,0.08)).
- يمكن إضافة طبقة زخرفية بملمس رياضي (شبكات، رموز رياضية شبه شفافة).

### Chips / Tags
- خلفية `--color-secondary-soft`، نص أخضر أو ذهبي، حواف 999px.

### Alerts
- **Success:** خلفية خضراء شفافة مع أيقونة ✔.
- **Warning:** ذهبي فاتح مع أيقونة ⚠.
- **Danger:** أحمر مع ظل داخلي بسيط.

### Progress Components
- شريط متدرج من الذهبي إلى الأخضر.
- حلقات بحدود دائرية تستخدم `stroke-dashoffset` للأنيميشن.

### Tables / Panels
- رؤوس بذهبي هادئ، صفوف مخططة شفافة، حواف رفيعة.
- في الوضع الداكن: خلفية داكنة، نص أبيض، حدود خضراء باهتة.

## 5. Layout & Responsiveness

- Breakpoints (Tailwind): `sm:480px`, `md:768px`, `lg:1024px`, `xl:1280px`, `2xl:1536px`.
- Sidebar collapses تحت `lg` مع زر واضح.
- Card grid يتبدل من صف واحد في الهواتف إلى شبكة 2–3 أعمدة في الأجهزة الكبيرة.
- خلفيات تفاعلية باستخدام gradations وSVG شبه شفافة مستوحاة من التاج والسيوف.

## 6. Motion Guidelines

| Interaction | Motion |
|-------------|--------|
| ظهور بطاقات/أقسام | Fade + slide-up (200–250ms, ease-out). |
| Hover على زر رئيسي | TranslateY(-2px) + تعزيز الظل (150ms). |
| تحديث النقاط | Animation على stroke-dashoffset (500ms) + عداد يتزايد تدريجيًا. |
| تبديل اللغة/الثيم | Cross-fade + transition للألوان (300ms). |
| Drag & drop في التحديات | Scale بسيط أثناء السحب، bounce عند الإفلات. |

## 7. Next Steps
1. تطبيق المتغيّرات في ملف CSS مركزي (light/dark).
2. تحديث Tailwind + DaisyUI لتمثيل ألوان العلامة والخطوط الجديدة.
3. إعادة بناء الواجهة وفق هذه الأساسات (البطاقات، التحديات، الصفحات).
