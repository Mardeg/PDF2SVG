#!/usr/bin/env python3
import base64
import io
import os
import html
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageTk


class PDFGalleryApp:

    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Optimized Gallery SVG")
        self.root.geometry("650x580")
        self.root.resizable(True, True)

        # Core file tracking states
        self.pdf_path = None
        self.raw_pages_data = []  # Holds raw bytes and base dimensions
        self.page_rotations = {}  # Tracks user-selected thumbnail rotation degrees
        self.extracted_title = ""  # Document text title cache

        # Main Structural Container Frames
        self.top_frame = ttk.Frame(root, padding="15")
        self.top_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(
            self.top_frame,
            text="Select an image PDF to preview, rotate, and convert:",
            font=("Helvetica", 11),
        )
        self.title_label.pack(anchor=tk.W, pady=(0, 10))

        self.select_btn = ttk.Button(
            self.top_frame, text="Browse PDF File", command=self.select_and_load_previews
        )
        self.select_btn.pack(fill=tk.X, pady=(0, 10))

        # Persistent Metadata Title UI Label Display
        self.doc_title_var = tk.StringVar(value="Document Title: [No File Selected]")
        self.doc_title_label = ttk.Label(
            self.top_frame,
            textvariable=self.doc_title_var,
            font=("Helvetica", 10, "bold"),
            foreground="#0056b3"
        )
        self.doc_title_label.pack(anchor=tk.W, pady=(0, 5))

        # Status tracking elements
        self.status_var = tk.StringVar(value="Status: Idle")
        self.status_label = ttk.Label(
            self.top_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic")
        )
        self.status_label.pack(anchor=tk.W)
        # Horizontal container frame to hold both checkboxes and the dropdown side-by-side
        self.checkbox_frame = ttk.Frame(self.top_frame)
        self.checkbox_frame.pack(anchor=tk.W, pady=(5, 5))

        # Checkbox 1: Remove Transparency (Ticked by default)
        self.remove_transparency_var = tk.BooleanVar(value=True)
        self.transparency_chk = ttk.Checkbutton(
            self.checkbox_frame, 
            text="Remove transparency", 
            variable=self.remove_transparency_var
        )
        self.transparency_chk.pack(side=tk.LEFT, padx=(0, 15))

        # Checkbox 2: Reduce Colours (Unticked by default)
        self.reduce_colours_var = tk.BooleanVar(value=False)
        self.reduce_colours_chk = ttk.Checkbutton(
            self.checkbox_frame, 
            text="Reduce colours", 
            variable=self.reduce_colours_var,
            command=self.toggle_color_dropdown
        )
        self.reduce_colours_chk.pack(side=tk.LEFT, padx=(0, 5))

        # Dropdown: Dynamic colour spectrum picker (Greyed out by default)
        self.color_dropdown_var = tk.StringVar(value="256")
        self.color_dropdown = ttk.Combobox(
            self.checkbox_frame,
            textvariable=self.color_dropdown_var,
            values=["256", "128", "64", "32", "16", "8", "4"],
            width=5,
            state="disabled"
        )
        self.color_dropdown.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(self.top_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(5, 5))

        # --- Interactive Thumbnail Preview Grid UI Section ---
        self.preview_label = ttk.Label(root, text="Page Orientation Previews (Click item to rotate 90°):", font=("Helvetica", 10, "bold"))
        self.preview_label.pack(anchor=tk.W, padx=15, pady=(10, 2))

        # Creating scrollable canvas container hooks for thumbnails assembly
        self.canvas_frame = ttk.Frame(root, padding="10", relief=tk.SUNKEN)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, background="#ffffff")

        self.grid_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Action Execution Controls Frame
        self.action_frame = ttk.Frame(root, padding="15")
        self.action_frame.pack(fill=tk.X)

        self.convert_btn = ttk.Button(
            self.action_frame, text="Compile and Optimize SVG Gallery", command=self.start_svg_compilation, state=tk.DISABLED
        )
        self.convert_btn.pack(fill=tk.X)

    def toggle_color_dropdown(self):
        """Dynamic interface binder: activates or greys out the drop menu based on checkbox state."""
        if self.reduce_colours_var.get():
            self.color_dropdown.config(state="readonly")
        else:
            self.color_dropdown.config(state="disabled")

    def select_and_process(self):
        # Dummy anchor hook to keep internal Tkinter references mapped consistently
        pass
    def select_and_load_previews(self):
        self.pdf_path = filedialog.askopenfilename(
            title="Select Source PDF", filetypes=[("PDF Files", "*.pdf")]
        )
        if not self.pdf_path:
            return

        self.select_btn.config(state=tk.DISABLED)
        self.convert_btn.config(state=tk.DISABLED)
        
        # Clear existing thumbnail grids on new executions
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.raw_pages_data = []
        self.page_rotations = {}
        self.extracted_title = ""

        threading.Thread(
            target=self.load_pdf_previews_worker,
            args=(self.pdf_path,),
            daemon=True,
        ).start()

    def load_pdf_previews_worker(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            # Multi-Tier Title Extraction
            detected_title = ""

            # Tier 1: Standard Metadata Dictionary Check
            try:
                meta = reader.metadata
                if meta and "/Title" in meta and meta["/Title"]:
                    possible_title = str(meta["/Title"]).strip()
                    # Filter out useless auto-generated scanner values
                    if possible_title.lower() not in ["document", "untitled", "scan", "01", "page01"]:
                        detected_title = possible_title
            except Exception:
                pass

            # Tier 2: Dig into the Embedded XMP XML Document Streams (If Tier 1 failed)
            if not detected_title:
                try:
                    # Look for modern XMP container packets embedded in the PDF root Catalog
                    xmp_meta = reader.xmp_metadata
                    if xmp_meta:
                        # Query the Dublin Core schema element properties natively
                        dc_title = xmp_meta.dc_title
                        if dc_title and isinstance(dc_title, dict):
                            # XMP dc:title fields are usually dictionary maps keyed by language codes (e.g., 'x-default')
                            first_val = next(iter(dc_title.values()), "")
                            if str(first_val).strip().lower() not in ["document", "untitled", "scan"]:
                                detected_title = str(first_val).strip()
                except Exception:
                    pass

            # Tier 3: Intercept the Structural Outline Bookmark Tree (If Tiers 1 and 2 failed)
            if not detected_title:
                try:
                    outlines = reader.outline
                    if outlines and len(outlines) > 0:
                        # Grab the very first structural text label bookmark in the file
                        first_node = outlines[0]
                        # Ensure it's a structural dictionary wrapper and not a nested array group list
                        if isinstance(first_node, dict) and "/Title" in first_node:
                            node_title = str(first_node["/Title"]).strip()
                            if node_title.lower() not in ["document", "untitled", "scan"]:
                                detected_title = node_title
                except Exception:
                    pass

            # Tier 4: Fallback to the clean base filename if all extraction methods drew a blank
            if not detected_title:
                detected_title = os.path.splitext(os.path.basename(pdf_path))[0]

            # Finalize sanitation to keep the generated markup code completely XML compliant
            self.extracted_title = html.escape(detected_title)

            # Update the interface label safely on the main UI thread loop
            self.root.after(0, lambda t=self.extracted_title: self.doc_title_var.set(f"Document Title: {t}"))

            for index, page in enumerate(reader.pages):
                page_num = index + 1
                self.update_status(f"Loading previews: Page {page_num}/{total_pages}...")

                if not page.images or len(page.images) == 0:
                    continue

                target_img_obj = None
                max_pixel_volume = -1
                for img_asset in page.images:
                    try:
                        volume = int(img_asset.image.width) * int(img_asset.image.height)
                        if volume > max_pixel_volume:
                            max_pixel_volume = volume
                            target_img_obj = img_asset
                    except Exception:
                        if target_img_obj is None:
                            target_img_obj = img_asset

                if target_img_obj is None:
                    target_img_obj = page.images

                # Normalise color channels via Pillow context
                pil_img = target_img_obj.image
                if pil_img.mode in ("CMYK", "YCbCr", "LAB"):
                    pil_img = pil_img.convert("RGB")
                elif pil_img.mode == "1":
                    pil_img = pil_img.convert("L")

                # Handle decode mirror corrections immediately
                try:
                    img_dict = target_img_obj.indirect_reference.get_object()
                    if "/Decode" in img_dict:
                        decode_arr = img_dict["/Decode"]
                        if len(decode_arr) >= 2 and float(decode_arr[0]) > float(decode_arr[1]):
                            pil_img = ImageOps.invert(pil_img)
                except Exception:
                    pass

                # Cache properties array map memory pointers
                self.raw_pages_data.append({
                    "pil_image": pil_img,
                    "page_num": page_num
                })
                self.page_rotations[page_num] = 0

                # Render thumbnail interface frames dynamically onto main window thread loop
                self.root.after(0, lambda p=page_num, img=pil_img, idx=index: self.render_thumbnail_tile(p, img, idx))
                self.set_progress(page_num, total_pages)

            self.update_status("Pre-loading finished. Adjust layout orientation and compile.")
            self.root.after(0, lambda: self.convert_btn.config(state=tk.NORMAL))

        except Exception as e:
            self.root.after(0, lambda msg=str(e): messagebox.showerror("Loading Error", f"Failed parsing document streams:\n{msg}"))
        
        self.root.after(0, lambda: self.select_btn.config(state=tk.NORMAL))

    def render_thumbnail_tile(self, page_num, pil_img, index):
        # Create thumbnail image copies safely
        thumb_img = pil_img.copy()
        thumb_img.thumbnail((120, 120))
        photo_img = ImageTk.PhotoImage(thumb_img)

        # Calculate grid cell coordinates positions (4 column grid pattern layout)
        row = index // 4
        col = index % 4

        cell_frame = ttk.Frame(self.grid_frame, padding="5", relief=tk.GROOVE)
        cell_frame.grid(row=row, column=col, padx=8, pady=8)

        img_label = tk.Label(cell_frame, image=photo_img, background="#eaeaea", cursor="hand2")
        img_label.image = photo_img  # type: ignore 
        img_label.pack()

        lbl_text = ttk.Label(cell_frame, text=f"Page {page_num} (0°)")
        lbl_text.pack(pady=(2, 0))

        # Attach interactive mouse button action listeners to loop click changes
        img_label.bind("<Button-1>", lambda e, p=page_num, label=img_label, txt=lbl_text: self.rotate_thumbnail_action(p, label, txt))

    def rotate_thumbnail_action(self, page_num, label_widget, text_widget):
        # Increment angles by 90 degree segments
        current_deg = (self.page_rotations[page_num] + 90) % 360
        self.page_rotations[page_num] = current_deg

        # Lookup cached baseline pixel data mapping attributes
        base_pil = next(p["pil_image"] for p in self.raw_pages_data if p["page_num"] == page_num)
        
        thumb_copy = base_pil.copy()
        if current_deg == 90:
            thumb_copy = thumb_copy.transpose(Image.Transpose.ROTATE_270)
        elif current_deg == 180:
            thumb_copy = thumb_copy.transpose(Image.Transpose.ROTATE_180)
        elif current_deg == 270:
            thumb_copy = thumb_copy.transpose(Image.Transpose.ROTATE_90)

        thumb_copy.thumbnail((120, 120))
        updated_photo = ImageTk.PhotoImage(thumb_copy)
        
        label_widget.config(image=updated_photo)
        label_widget.image = updated_photo  # type: ignore
        text_widget.config(text=f"Page {page_num} ({current_deg}°)")
    def start_svg_compilation(self):
        self.select_btn.config(state=tk.DISABLED)
        self.convert_btn.config(state=tk.DISABLED)
        
        # Set progress bar to a small baseline "heartbeat" instantly
        self.progress_bar.config(value=5)
        
        threading.Thread(
            target=self.compilation_pipeline_worker,
            daemon=True
        ).start()

    def compilation_pipeline_worker(self):
        try:
            total_pages = len(self.raw_pages_data)
            views = []
            content_elements = []
            img_width, img_height = 0, 0
            extracted_pages_metadata = []
            sibling_selectors = []

            for index, page_data in enumerate(self.raw_pages_data):
                page_num = page_data["page_num"]
                pil_img = page_data["pil_image"]
                chosen_rotation = self.page_rotations[page_num]
                
                self.update_status(f"Compiling: Optimizing Page {page_num}/{total_pages}...")

                # --- START OF DUAL-CHECKBOX IMAGE MODIFICATION ---
                processed_img = pil_img.copy()
                transparency_detected = False
                color_reduced = False

                # 1. Handle Transparency Path
                if self.remove_transparency_var.get():
                    if processed_img.mode in ("RGBA", "LA") or (processed_img.mode == "P" and "transparency" in processed_img.info):
                        transparency_detected = True
                        
                        # Format status message using the script's native arrow aesthetic
                        status_msg = f"Page {index + 1} → Removing transparency..."
                        
                        if hasattr(self, 'pipeline_error_queue'):
                            self.pipeline_error_queue.put(status_msg)
                        elif hasattr(self, 'status_queue'):
                            getattr(self, 'status_queue').put(status_msg)
                        elif hasattr(self, 'error_queue'):
                            getattr(self, 'error_queue').put(status_msg)
                        elif hasattr(self, 'status_var'):
                            self.status_var.set(status_msg)

                        if processed_img.mode != "RGBA":
                            processed_img = processed_img.convert("RGBA")
                            
                        background = Image.new("RGB", processed_img.size, (255, 255, 255))
                        alpha_mask = processed_img.getchannel('A')
                        background.paste(processed_img, (0, 0), mask=alpha_mask)
                        processed_img = background.convert("L").convert("P", palette=Image.Palette.ADAPTIVE, colors=128)

                # 2. Handle Solid Background Path (Only if Transparency wasn't triggered)
                if not transparency_detected and self.reduce_colours_var.get():
                    color_reduced = True
                    
                    status_msg = f"Page {index + 1} → Reducing colors..."
                    if hasattr(self, 'pipeline_error_queue'):
                        self.pipeline_error_queue.put(status_msg)
                    elif hasattr(self, 'status_queue'):
                        getattr(self, 'status_queue').put(status_msg)
                    elif hasattr(self, 'error_queue'):
                        getattr(self, 'error_queue').put(status_msg)
                    elif hasattr(self, 'status_var'):
                        self.status_var.set(status_msg)
                    
                    # Pull dynamic colour selection from UI and convert to integer fallback safely
                    chosen_colors = int(self.color_dropdown_var.get())
                    
                    # Crush full color layer down to user's targeted bit target spectrum value
                    processed_img = processed_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=chosen_colors)

                buffer = io.BytesIO()
                
                # If either modification logic was applied, save cleanly to bypass heavy compression inflation
                if transparency_detected or color_reduced:
                    processed_img.save(buffer, format="PNG")
                else:
                    processed_img.save(buffer, format="PNG", optimize=True)
                    
                raw_bytes = buffer.getvalue()
                # --- END OF MODIFICATION ---

                # Pass stream to external compression tools ONLY if no custom processing occurred
                if transparency_detected or color_reduced:
                    optimized_bytes = raw_bytes
                else:
                    optimized_bytes = self.optimize_png_bytes(raw_bytes, page_num)

                b64_data = base64.b64encode(optimized_bytes).decode("utf-8")
                data_uri = f"data:image/png;base64,{b64_data}"

                width = int(pil_img.width)
                height = int(pil_img.height)

                if width <= 5 or height <= 5:
                    width, height = 2480, 3505

                if index == 0:
                    img_width, img_height = width, height

                extracted_pages_metadata.append({
                    "uri": data_uri,
                    "width": width,
                    "height": height,
                    "rotation": chosen_rotation
                })
                self.set_progress(page_num, total_pages)

            self.update_status("Building pure CSS target-driven layout structure...")

            calculated_font_size = int(img_height // 10)
            calculated_line_height = int(calculated_font_size * 1.2)
            padding_bottom = int(calculated_font_size // 2)

            # Assembly loop blocks
            for index, page_meta in enumerate(extracted_pages_metadata):
                page_num = index + 1
                y_offset = int(index * 2 * img_height)

                # Base structural tracking anchors
                if page_num >= 2:
                    views.append(
                        f'<view id="p{page_num}" viewBox="0 {y_offset} {img_width} {img_height}"/>'
                    )

                content_elements.append(
                    f'<image x="0" y="{y_offset}" href="{page_meta["uri"]}" '
                    f'role="img" aria-label="Page {page_num} of {total_pages}" />'
                )

                # Navigation sequence maps
                prev_href = f"#p{total_pages}" if page_num == 1 else ("#" if page_num == 2 else f"#p{page_num - 1}")
                next_href = "#" if page_num == total_pages else f"#p{page_num + 1}"
                
                prev_target_num = total_pages if page_num == 1 else (1 if page_num == 2 else page_num - 1)
                next_target_num = 1 if page_num == total_pages else page_num + 1

                text_y = int(y_offset + img_height - padding_bottom)
                x_prev = int(img_width * 0.05)
                x_next = int(img_width * 0.95 - (calculated_font_size * 1.2))

                content_elements.append(
                    f'<a href="{prev_href}" role="button" aria-label="Go to Page {prev_target_num}">'
                    f'<text x="{x_prev}" y="{text_y}">⏮️</text></a>'
                )
                content_elements.append(
                    f'<a href="{next_href}" role="button" aria-label="Go to Page {next_target_num}">'
                    f'<text x="{x_next}" y="{text_y}">⏭️</text></a>'
                )

                # CSS Target-Driven Rotation
                if page_meta["rotation"] > 0:
                    if page_num == 1:
                        sibling_selectors.append(
                            f'#p1:target > image[y="{y_offset}"], '
                            f'svg:not(:target) > image[y="{y_offset}"] {{ '
                            f'transform: rotate({page_meta["rotation"]}deg); '
                            f'}}'
                        )
                    else:
                        sibling_selectors.append(
                            f'#p{page_num}:target ~ image[y="{y_offset}"] {{ '
                            f'transform: rotate({page_meta["rotation"]}deg); '
                            f'}}'
                        )

            svg_output = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg id="p1" version="2" viewBox="0 0 {img_width} {img_height}" 
     role="application" aria-labelledby="pdf-title"
     xmlns="http://www.w3.org/2000/svg">
<title id="pdf-title">{self.extracted_title}</title>
<style>
/* <![CDATA[ */
svg{{width:100vw;height:100vh;background-color:#444}}
image{{
    width:{img_width}px;
    height:{img_height}px;
    transform-box: fill-box;
    transform-origin: center;
}}
text{{
    font-size:{calculated_font_size}px;
    opacity:0.3;
    user-select:none;
    line-height:{calculated_line_height}px;
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif;
}}
a:hover > text, a:active > text{{opacity: 0.9; cursor: pointer}}
{"\n".join(sibling_selectors)}
/* ]]> */
</style>
{"\n".join(views)}
{"\n".join(content_elements)}
</svg>"""

            output_svg_path = os.path.splitext(self.pdf_path)[0] + ".svg"
            with open(output_svg_path, "w", encoding="utf-8") as f:
                f.write(svg_output)

            self.update_status("Done!")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Gallery SVG successfully saved to:\n{output_svg_path}"
                )
            )

        except Exception as e:
            error_message = str(e)
            self.root.after(
                0,
                lambda msg=error_message: messagebox.showerror(
                    "Fatal Compilation Error", f"An error occurred:\n{msg}"
                )
            )

        self.root.after(0, self.reset_ui)

    def optimize_png_bytes(self, raw_bytes, page_num):
        """Sequential losslessly optimizing engine with stage reporting updates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "raw_src.png")
            optipng_path = os.path.join(tmpdir, "opti.png")
            pngcrush_path = os.path.join(tmpdir, "crush.png")

            with open(input_path, "wb") as f:
                f.write(raw_bytes)

            self.update_status(f"Page {page_num} ➔ Running OptiPNG...")
            try:
                subprocess.run(
                    ["optipng", "-o2", "-strip", "all", "-out", optipng_path, input_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                optipng_path = input_path

            self.update_status(f"Page {page_num} ➔ Running Pngcrush...")
            try:
                subprocess.run(
                    ["pngcrush", "-rem", "allb", "-reduce", "-ow", optipng_path, pngcrush_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
                final_crush_target = pngcrush_path if os.path.exists(pngcrush_path) else optipng_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                final_crush_target = optipng_path

            self.update_status(f"Page {page_num} ➔ Max Zopfli re-compressing...")
            try:
                subprocess.run(["advpng", "-z", "-4", final_crush_target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            with open(final_crush_target, "rb") as f:
                return f.read()

    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(f"Status: {message}"))

    def set_progress(self, current, total):
        percentage = (current / total) * 100
        self.root.after(0, lambda: self.progress_bar.config(value=percentage))

    def reset_ui(self):
        self.select_btn.config(state=tk.NORMAL)
        self.convert_btn.config(state=tk.NORMAL)
        self.status_var.set("Status: Idle")
        self.progress_bar.config(value=0)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFGalleryApp(root)
    root.mainloop()
