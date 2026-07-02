<div align="center">
  <img src="banner.jpg" alt="Barcode PDF Generator Banner" width="100%">
  
  <h1>📊 Barcode PDF Generator</h1>
  <p><b>Python utility for generating batches of barcodes and compiling them into print-ready PDF files.</b></p>
  
  <p>
    <a href="#description">Description</a> •
    <a href="#data-requirements">Data Requirements</a> •
    <a href="#installation-and-launch">Installation & Launch</a>
  </p>
</div>

---

## 📝 Description
**Barcode PDF Generator** is a powerful utility with a modern web interface designed for the mass generation of barcode PDF files (Code128 format) from a CSV table. It's perfectly suited for preparing labels for marketplaces. 
The default barcode size is set to **58x40 mm** (standard thermal label size).

### Key Features:
- 📄 Reads CSV files in various encodings (including `utf-8`, `cp1251`).
- 👁 Web interface for previewing data before generating the PDFs.
- 📦 Batch download of all generated barcodes in a single, convenient ZIP archive.
- 🤖 Includes a CLI version for integration and automation.

## 📋 Data Requirements
Your CSV file must contain the following columns:
- **Seller SKU** (Артикул продавца) - used as the final file name
- **Barcodes** (Баркоды) - the barcode digits
- **Product Name** (Наименование) - the name of the product printed on the label
- *Optional:* **WB SKU** (Артикул WB)

## 🚀 Installation and Launch
1. Ensure you have Python installed (version 3.8+).
2. Clone the repository:
   ```bash
   git clone https://github.com/v1per4ever/barcode-pdf-generator.git
   cd barcode-pdf-generator
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application (web or cli) depending on your needs, following the internal instructions.
