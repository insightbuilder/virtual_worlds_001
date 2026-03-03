# Medical Paperwork Datasets

Based on our research across Kaggle and GitHub, here are the most relevant datasets with their direct working links for the three categories of medical documentation you mentioned: forms, receipts/bills, and prescriptions.

## 1. Medical Forms & Patient Intake

Patient intake forms are often difficult to find in raw, completed image formats due to HIPAA and PII restrictions. However, there are templates and related datasets:

*   **Medical Intake Pipeline:** An experimental automated pipeline repository by David Shapiro for analyzing medical intake.
    *   Link: [https://github.com/daveshap/Medical_Intake](https://github.com/daveshap/Medical_Intake) **(Reachable)**
*   **Awesome Healthcare Datasets:** A curated list of healthcare datasets, including clinical notes and texts.
    *   Link: [https://github.com/geniusrise/awesome-healthcare-datasets](https://github.com/geniusrise/awesome-healthcare-datasets) **(Reachable)**
*   **MIMIC-IV (PhysioNet):** While it requires credentialing, this is the gold standard for clinical data and EHR notes (which represent the digitized output of intake forms).
    *   Link: [https://physionet.org/content/mimiciv/](https://physionet.org/content/mimiciv/) **(Reachable)**

## 2. Receipts (Medical, Hotel, Pharmacy, & Retail)

Real medical receipts are heavily regulated, so we must often rely on general receipt OCR datasets (from retail, hotels, and pharmacies) to train and test the structural extraction models, supplementing with tabular medical cost data.

*   **Medical Cost Personal Dataset (Kaggle):** Highly popular for predicting insurance costs, but consists of tabular data (CSV) rather than images of bills. Good for logic testing.
    *   Link: [https://www.kaggle.com/datasets/mirichoi0218/insurance](https://www.kaggle.com/datasets/mirichoi0218/insurance) **(Reachable)**
*   **Consolidated Receipt Dataset (CORD) (GitHub):** A standard dataset for OCR and Layout tokenization featuring thousands of Indonesian retail/general receipts with heavy bounding box annotations.
    *   Link: [https://github.com/clovaai/cord](https://github.com/clovaai/cord) **(Reachable)**
*   **ICDAR 2019 SROIE Dataset (GitHub):** The Scanned Receipts OCR and Information Extraction dataset contains 1000 scanned images of receipts with text bounding boxes for company, address, date, and total. Highly applicable to hotel and pharmacy receipts.
    *   Link: [https://github.com/zzzDavid/ICDAR-2019-SROIE](https://github.com/zzzDavid/ICDAR-2019-SROIE) **(Reachable)**
*   **ReceiptSense / CORU Dataset (Hugging Face):** A massive dataset featuring 20,000 annotated receipts and 30,000 OCR-annotated images from diverse retail settings, supporting QA and info extraction.
    *   Link: [https://huggingface.co/datasets/abdoelsayed/CORU](https://huggingface.co/datasets/abdoelsayed/CORU) **(Reachable)**
*   **OCR-Scanned-Receipts (GitHub):** A deep learning approach and dataset collection for OCR on scanned structured and semi-structured receipts.
    *   Link: [https://github.com/tejasvi96/OCR-Scanned-Receipts](https://github.com/tejasvi96/OCR-Scanned-Receipts) **(Reachable)**

## 3. Handwritten Prescriptions

This is the most well-represented category for image-based datasets due to the specific challenge of doctor handwriting:

*   **Medical Prescription OCR Dataset (GitHub):** A comprehensive dataset of synthetic, fully annotated images, designed for training transformer-based OCR systems.
    *   Link: [https://github.com/JonSnow1807/medical-prescription-ocr](https://github.com/JonSnow1807/medical-prescription-ocr) **(Reachable)**
*   **Hugging Face `avi-kai/Medical_Prescription_Handwritten_Words`:** Contains images of individual medical words (e.g., specific drug names) cropped from prescriptions.
    *   Link: [https://huggingface.co/datasets/avi-kai/Medical_Prescription_Handwritten_Words](https://huggingface.co/datasets/avi-kai/Medical_Prescription_Handwritten_Words) **(Reachable)**

## 4. Clinical Trials & Pharmacovigilance (Drug Research)

A significant amount of manual paperwork in medical research (especially at Clinical Research Organizations - CROs) revolves around Case Report Forms (CRFs), adverse event reporting, and Clinical Data Management (CDM). 

*   **WangLabCSU/faers (GitHub):** Tools and data samples for the FDA Adverse Event Reporting System (FAERS), which collects spontaneous reports of adverse events and medication errors.
    *   Link: [https://github.com/WangLabCSU/faers](https://github.com/WangLabCSU/faers)

---

### Recommended Next Steps for the MCP Server

I recommend we:

1.  **Define a small synthetic/sample dataset:** We can generate 2-3 realistic sample images/PDFs for each category (a sample intake form, a hospital bill, and a prescription) to immediately start building and testing the MCP extraction tools.
2.  **Use public Kaggle datasets for scale:** Rely on the readable datasets (like the `medical-prescription-ocr` repo on GitHub and `Medical_Prescription_Handwritten_Words` on Hugging Face).
