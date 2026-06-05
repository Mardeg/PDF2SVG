# PDF to SVG Gallery tool

A lightweight Python/Tkinter GUI workbench built for Linux that automates the transformation of image-only, "cheap and dirty" raster PDFs into 100% self-contained, highly optimized interactive web galleries of those same cheap and dirty raster images that this totally non-AI 🙄 readme will now outline.

---

### 👽 Examples

Lorem Ipsum can take a hike. All examples should be content exposing Dianetics for the pseudoscientific grift it is, whatever cloak it's wearing.

*  [Volney Mathison and Alphia Hart FDA investigative documents - 1963](https://web.archive.org/web/20260605014217id_/http://scientology.c1.biz/Volney-Mathison-and-Alphia-Hart-FDA-investigative-documents.svg)
*  [Intra-departmental Report on Scientologists breaking in to the Toronto office of Nancy McLean's lawyer - 1974](https://web.archive.org/web/20260605014002id_/http://scientology.c1.biz/toronto_breakin.svg)
*  [Spain Expels 6 Scientologists in Fraud Case - 1988](https://web.archive.org/web/20260605025610id_/http://scientology.c1.biz/thecompiler-1988-8.svg#p6)
*  [Allegations Common to All Counts - 2009](https://web.archive.org/web/20260605013317id_/http://scientology.c1.biz/Allegations-Common-to-All-Counts.svg)

## PDFs with rotated pages

*  [L.Ron Hubbard - An Opinion and a Summing Up - 1964](https://web.archive.org/web/20260605013812id_/http://scientology.c1.biz/OpinionSummingUp-1964-2.svg)
*  [I've no idea what this says but I'm sure it's scathing - 1984](https://web.archive.org/web/20260605013135id_/http://scientology.c1.biz/19920516.svg)
*  [Why a Portland Jury awarded $39 million in damages against one of the world's most profitable cults - 1985](https://web.archive.org/web/20260605021724id_/http://scientology.c1.biz/PortlandJury-1985.svg)
*  [Narconon Rehab Fined For Wild Claims About Detox Programs - 2015](https://web.archive.org/web/20260605013629id_/http://scientology.c1.biz/NarcononFalseAdvertising.svg)

---

### ⚠️ Scope & Use-Case Limit

Something tells you, maybe even this very line in the readme, that this tool is **strictly engineered for "dirty" image-only PDFs** (such as drag-and-drop file merge outputs, automatic office copier streams, or scanner output packages where every single page layout element is wrapped inside an embedded PNG image payload). 

It is **not** intended for standard text-selectable digital layout documents (such as vectorized PDFs containing real type font geometry layers… why did I whisper that?). Also it doesn't currently do batch processing or include detection for non-PNG raster images inside PDFs… contributions welcome!

---

### 📉 The Tedious Workflow This Tool Automates

Before this automation script, verifying and processing these files required a painfully repetitive manual pipeline:
1. **Validation**: Importing a PDF file into Inkscape, exporting it, and opening the layout wrapper inside a plain-text editor just to manually check for an absence of real selectable fonts.
2. **Page Count Verification**: Copying data-URIs out by hand to see if the extracted PNG object sequence perfectly matched the physical page count metadata.
3. **Dimension Inversion Testing**: Manually pasting base64 data-URIs straight into a Firefox browser tab to read the dimension output attributes inside the tab headers.
4. **Orientation Correction**: Manually fighting hidden rotation layers and reverse photograph-negative color channel bugs (`/Decode` matrices) created by scanner hardware.
5. **Reality Adjustment**: Repeatedly bashing my head against the wall.
6. **Optimization passes**: Drag-dropping raw file assets through external tool chains to strip hidden profile metadata chunks before stitching the code containers back together.

**This GUI maps out that entire sequence inside a responsive processing timeline window, transforming minutes of error-prone manual labour into a single click.**

---

### 🔧 System Requirements & Installation

Because this tool chains together high-performance binary layout optimization and stream decoding engines natively, you must configure the following dependencies inside your Linux terminal environment.

#### 1. System Package Installations (Debian / Ubuntu / Linux Mint)
Open your terminal and execute this exact string (without the red colouring) to install the required JBIG2 raster image decoder and lossless re-compression compilers:

```bash
sudo apt update && sudo apt install -y python3 python3-pip optipng pngcrush advancecomp jbig2dec
```

#### 2. Python Package Configurations
Modern Linux distributions block raw global environment updates to protect core system parameters. Run this exact pip line using the required safety override flags:

```bash
pip3 install pypdf pillow --break-system-packages
```

---

### 💡 Core Engineering & Performance Hacks Included

*   **100% Pure URL Pagination**: The viewer functions completely without runtime JavaScript [INDEX]. Browser pagination is controlled entirely through native SVG `<view>` IDs matching the URL document fragment [INDEX]. This means you can display individual pages from the .svg output directly in a webpage using an IMG or IFRAME src, or even a CSS background-image url() by including the #fragment in the URL. Up yours, inferior `<symbol>` spritesheets!
*   **The Page-Bleed Separation Buffer**: To prevent adjacent pages, mobile scroll-frames, or nav layout button overlays from bleeding into view when dealing with mixed landscape and portrait aspects, every image layer is mathematically isolated inside the column by an extra **100% full-page height buffer space gap.**
*   **Aria-Labelled Semantic Accessibility**: In an otherwise inaccessible text-as-png format, the SVG output features clean accessibility code like `aria-labelledby="pdf-title"` and  alongside descriptive `role="button"` properties on all touch-friendly interactive anchors. Mmmm, touch-friendly… ( • )( • )ԅ(‾⌣‾ԅ)
*   **The Inversion Array Mask Sweeper**: The extraction parser queries underlying object properties to intercept hidden reverse colour maps (`/Decode [1 0]`), running local transpositions in Pillow to guarantee blah blah blah RGB colour compliance without… who the fuck even reads this far?

---

### 🛠️ Image Truncation & Optimization Troubleshooting

If an extracted page output throws an error or fails to load its raster canvas elements inside web engines after running the file through the compiler, lie in bed and cry into your pillow, then whatever this shit says:
1. **The 1x1 Spacer Tracking Artifact Trap**: Scanners frequently slide tiny 1x1 tracking dots or transparent watermark sheets into structural layout code beds [INDEX]. The application includes an automated **Pixel Volume Smart Filter** (`volume = w * h`) to isolate the true page canvas, but heavily corrupted files can occasionally lock onto tracking artifacts if specific keys are missing.
2. **Zopfli Compression Thresholds**: Stage 3 compression relies on `advpng` utilizing maximum Zopfli depth loops (`-z -4`). If a huge document scan contains thousands of complex color DPI layers, this process can take longer to complete. Watch the visual Tkinter stage metrics bar to confirm that task workers are sequentially handling compilation.

---

### 📂 How To Initialize & Run The Script

You can launch the program in two different ways under Linux and maybe BSD and Redox but no promises, because fuck you Apple and Microsoft: via the terminal, or as a standalone double-clickable desktop application.

#### Method A: Linux Mint example Desktop File Manager (Double-Click)
To configure the file so it opens instantly without using a terminal window:
1. Open your **File Manager** (Nemo) inside Linux Mint.
2. Locate your saved python script file (`PNGonlyPDF2SVG.py`), **right-click** it, and select **Properties**.
3. Move to the **Permissions** tab and ensure **"Allow executing file as a program"** is explicitly ticked.
4. Close the properties dialog box.
5. In the top File Manager menu panel, navigate to **Edit** ➔ **Preferences**.
6. Select the **Behavior** tab.
7. Under the **Executable Text Files** configuration rules block, switch the preference setting selection to either **"Ask each time"** or **"Run them"**.
8. You can now simply double-click the `PNGonlyPDF2SVG.py` file icon and choose **"Run"** to launch the graphical user interface instantly.

#### Method B: Linux Terminal Interface
Alternatively, ensure you are inside the directory path hosting your application script and execute it directly from your console environment:

```bash
python3 PNGonlyPDF2SVG.py
```

This readme was brought to you by the letter ζ
