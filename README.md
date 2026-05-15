# 🧶 Nassij Engine V3.0
## The Advanced Arabic Document Weaver

**Nassij** (Arabic for *Weaving*) is a next-generation Arabic document reconstruction engine. It doesn't just convert files; it re-weaves them. By combining high-precision OCR with culturally-rooted typography and institutional-grade layout logic, Nassij delivers the highest fidelity PDF-to-DOCX transformation available for the Arabic script.

---

---

## 🏛️ Project Vision
Nassij is built on the philosophy that Arabic technology shouldn't just be functional—it should be beautiful. Our aesthetic treats the Arabic script as a living visual material, merging ancient calligraphic logic with modern minimalist structure.

---

---

## ✨ Key Features

### 🛡️ Linguistic Merkle Trees (Integrity Layer)
- **Cryptographic Verification**: Generates `.nassij-proof` JSON files leveraging Merkle trees to seal document contents.
- **Canonical Arabic Hashing**: Normalizes Arabic diacritics, presentation forms, and removes Kashida before hashing, ensuring equivalent strings share the same cryptographic identity.
- **Trust & Verification**: Verify that a generated DOCX wasn't tampered with post-conversion.

### 💎 Precision Reconstruction
- **Direct Copy Mode (NassijScanner)**: Extremely fast, 100% accurate extraction for digital native PDFs, bypassing OCR and extracting coordinate-perfect layouts.
- **Institutional-Grade Fidelity**: Specialized handling for complex Arabic ligatures (e.g., "لا", "الله", "إلا").
- **Diacritics Preservation**: Advanced regex and Unicode normalization to preserve tashkeel (>=90% accuracy).
- **RTL Sovereignty**: Native Right-to-Left (RTL) enforcement at the XML level for Microsoft Word.

### 🧠 Intelligence Layers
- **Multi-Engine Strategy**: Seamless switching between EasyOCR and PaddleOCR PP-OCRv5.
- **TableMagic**: Sophisticated reconstruction of complex, merged, and borderless tables.
- **Local-First**: All processing happens on your machine. Privacy by design.

### 🌐 Hybrid Interface
- **Powerful CLI**: For developers and batch processing.
- **Museum-Grade Web UI**: A stunning, dark-mode web interface built with FastAPI and Tailwind CSS, featuring a "Nucleus" drag-and-drop experience.

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/logiccrafterdz/nassij.git
   cd nassij
   ```

2. **Install the engine**:
   ```bash
   # Standard install
   pip install -e .
   
   # With Web UI and OCR optimizations
   pip install -e .[web,paddle]
   ```

### Running the Web Interface
Experience the Nassij UI locally:
```bash
python web/app.py
# Open http://127.0.0.1:8000
```

### CLI Usage
```bash
# Basic conversion
nassij convert input.pdf -o output.docx

# Generate a Cryptographic Proof
nassij convert input.pdf -o output.docx --proof

# Verify a generated Proof
nassij verify output.docx --proof output.docx.nassij-proof

# High-accuracy mode for scanned manuscripts
nassij convert input.pdf -o output.docx --mode accurate --dpi 400
```

---

## 🏗️ Architecture

```text
nassij/
├── core/             # The Weaving Logic
│   ├── pdf_reader.py # Coordinate-aware extraction
│   ├── engines/      # OCR Strategies (Paddle, EasyOCR)
│   ├── layout/       # Column and Block detection
│   └── arabic/       # Ligatures & Bidi processing
├── web/              # The Aesthetic Layer (FastAPI)
├── utils/            # Quality Metrics & Unicode helpers
└── cli.py            # The Developer Gateway
```

---

## 📊 Quality Benchmarks

| Metric | Target | Description |
|-------|--------|-------------|
| **CER** | < 8% | Character Error Rate |
| **WER** | < 20% | Word Error Rate |
| **Ligatures** | 100% | Accuracy for "لا", "إلا", etc. |
| **Tables** | ≥ 90% | Cell structure preservation |

---

## 📜 License
Licensed under the **MIT License**. Created with passion for the Arabic script by **LogicCrafterDZ**.

---

<div dir="rtl">

# 🧶 محرك نسيج | الإصدار 3.0
## حل متطور لمعالجة الوثائق العربية والتوثيق المشفّر

**نسيج** هو محرك من الجيل الجديد لإعادة بناء المستندات العربية. لا يكتفي البرنامج بمجرد التحويل، بل يعيد "نسج" الملفات عبر دمج تقنيات التعرف الضوئي (OCR) عالية الدقة مع فلسفة بصرية تعتز بأصالة الخط العربي.

---

---

## 🏛️ رؤية المشروع
يتمحور "نسيج" حول فلسفة أن التقنية العربية يجب أن تتجاوز مجرد الأداء الوظيفي لتصبح قطعة فنية. نعتمد توجهاً يعامل الحرف العربي كمادة بصرية حية، يمزج بين منطق الخط الكوفي الأصيل والبنية الرقمية الحديثة.

---

---

## ✨ المميزات الرئيسية

### 🛡️ الأشجار الميركالية اللغوية (طبقة التوثيق)
- **الإثبات الرياضي**: توليد ملفات `.nassij-proof` تعتمد على خوارزميات Merkle Trees لختم محتوى المستند.
- **التطبيع اللغوي (Canonical Hashing)**: توحيد البصمة البايتية للنصوص عبر تجاهل الكشيدة، فصل التشكيل، وفك الـ Presentation Forms، بحيث يكون للنصوص المتكافئة نفس الهاش.
- **التحقق من النزاهة**: فحص الوثائق رقمياً لضمان عدم تعرضها للتلاعب أو التحريف بعد تحويلها.

### 💎 دقة مؤسساتية
- **الاستخراج المباشر (NassijScanner)**: سرعة فائقة ودقة 100% للمستندات الرقمية الحديثة (Digital Native) مع تجاوز الـ OCR بالكامل وبناء الهيكل مكانياً.
- **محاكاة الحرف**: معالجة متقدمة للروابط اللغوية المعقدة (مثل: لا، إلا، الله).
- **حفظ التشكيل**: استخدام تقنيات النورملة الموحدة (Unicode NFC) للحفاظ على الحركات (دقة >= 90%).
- **سيادة اليمين**: فرض اتجاه الكتابة (RTL) على مستوى ملف الـ XML لضمان التوافق المطلق مع Microsoft Word.

### 🧠 طبقات الذكاء
- **استراتيجية المحركات المتعددة**: تبديل سلس بين محركات EasyOCR و PaddleOCR PP-OCRv5.
- **نسج الجداول**: تقنيات ذكية لإعادة بناء الجداول المعقدة، المدمجة، وعديمة الحدود.
- **الخصوصية أولاً**: تتم جميع عمليات المعالجة محلياً على جهازك دون الحاجة للإنترنت.

### 🌐 واجهات هجينة
- **بوابة المطورين (CLI)**: واجهة سطر أوامر قوية للعمليات المكثفة.
- **الواجهة النخبوية (Web UI)**: واجهة ويب مذهلة مبنية بـ FastAPI و Tailwind CSS، تتميز بتجربة "النواة" (Nucleus) للسحب والإفلات.

---

## 🚀 البدء السريع

### التثبيت

1. **تحميل المستودع**:
   ```bash
   git clone https://github.com/logiccrafterdz/nassij.git
   cd nassij
   ```

2. **تثبيت المحرك**:
   ```bash
   # التثبيت القياسي
   pip install -e .
   
   # التثبيت مع واجهة الويب ومحركات OCR المتطورة
   pip install -e .[web,paddle]
   ```

### تشغيل واجهة الويب
عش تجربة "نسيج" محلياً:
```bash
python web/app.py
# افتح الرابط http://127.0.0.1:8000
```

### استخدام سطر الأوامر
```bash
# تحويل بسيط
nassij convert input.pdf -o output.docx

# تحويل مع توليد ملف إثبات التوثيق اللغوي
nassij convert input.pdf -o output.docx --proof

# التحقق من سلامة مستند تم تحويله سابقاً
nassij verify output.docx --proof output.docx.nassij-proof

# وضع الدقة العالية للمخطوطات والمسوحات الضوئية
nassij convert input.pdf -o output.docx --mode accurate --dpi 400
```

---

## 📊 معايير الجودة

| المعيار | الهدف | الوصف |
|-------|--------|-------------|
| **معدل خطأ الحرف** | < 8% | Character Error Rate |
| **معدل خطأ الكلمة** | < 20% | Word Error Rate |
| **دقة الروابط** | 100% | دقة معالجة "لا"، "إلا"، إلخ |
| **دقة الجداول** | ≥ 90% | الحفاظ على بنية الخلايا والمحتوى |

---

## 📜 الترخيص
المشروع مرخص تحت رخصة **MIT**. طُوّر بشغف للحرف العربي بواسطة **LogicCrafterDZ**.

</div>
