# 🧶 Nassij Engine V2.0
## The Futuristic Semitic Document Weaver

**Nassij** (Arabic for *Weaving*) is a next-generation Arabic document reconstruction engine. It doesn't just convert files; it re-weaves them. By combining high-precision OCR with culturally-rooted typography and institutional-grade layout logic, Nassij delivers the highest fidelity PDF-to-DOCX transformation available for the Arabic script.

---

## 🏛️ Project Vision: "Futuristic Semitic"
Nassij is built on the philosophy that Arabic technology shouldn't just be functional—it should be beautiful. Our **Futuristic Semitic** aesthetic treats the Arabic script as a living visual material, merging ancient calligraphic logic with modern minimalist structure.

---

## ✨ Key Features

### 💎 Precision Reconstruction
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
Experience the "Futuristic Semitic" UI locally:
```bash
python web/app.py
# Open http://127.0.0.1:8000
```

### CLI Usage
```bash
# Basic conversion
nassij convert input.pdf -o output.docx

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

# 🧶 محرك نسيج | الإصدار 2.0
## السامي المستقبلي لمعالجة الوثائق العربية

**نسيج** هو محرك من الجيل الجديد لإعادة بناء المستندات العربية. لا يكتفي البرنامج بمجرد التحويل، بل يعيد "نسج" الملفات عبر دمج تقنيات التعرف الضوئي (OCR) عالية الدقة مع فلسفة بصرية تعتز بأصالة الخط العربي.

---

## 🏛️ رؤية المشروع: "السامي المستقبلي"
يتمحور "نسيج" حول فلسفة أن التقنية العربية يجب أن تتجاوز مجرد الأداء الوظيفي لتصبح قطعة فنية. نعتمد توجه **"السامي المستقبلي"** الذي يعامل الحرف العربي كمادة بصرية حية، يمزج بين منطق الخط الكوفي الأصيل والبنية الرقمية الحديثة.

---

## ✨ المميزات الرئيسية

### 💎 دقة مؤسساتية
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
عش تجربة "السامي المستقبلي" محلياً:
```bash
python web/app.py
# افتح الرابط http://127.0.0.1:8000
```

### استخدام سطر الأوامر
```bash
# تحويل بسيط
nassij convert input.pdf -o output.docx

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
