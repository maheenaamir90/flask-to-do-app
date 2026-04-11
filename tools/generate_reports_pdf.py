from pathlib import Path

from fpdf import FPDF


def write_wrapped(pdf: FPDF, text: str, line_h: float = 5.6, width: int = 108) -> None:
    if text == "":
        pdf.ln(3)
        return

    remaining = text
    while remaining:
        if len(remaining) <= width:
            pdf.cell(0, line_h, remaining, new_x="LMARGIN", new_y="NEXT")
            break

        chunk = remaining[:width]
        cut = chunk.rfind(" ")
        if cut < 28:
            cut = width
        part = remaining[:cut]
        pdf.cell(0, line_h, part, new_x="LMARGIN", new_y="NEXT")
        remaining = remaining[cut:].lstrip()


def render_markdown_to_pdf(src: Path, dst: Path, title: str) -> None:
    lines = src.read_text(encoding="utf-8").splitlines()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # Cover title for cleaner output
    pdf.set_font("Helvetica", "B", 18)
    write_wrapped(pdf, title, line_h=8, width=64)
    pdf.set_font("Helvetica", "", 11)
    write_wrapped(pdf, f"Source: {src.as_posix()}", line_h=6, width=88)
    pdf.ln(4)

    in_code_block = False
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            pdf.ln(1)
            continue

        txt = line.replace("`", "")
        txt = txt.encode("latin-1", "replace").decode("latin-1")

        if line.startswith("# "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 16)
            write_wrapped(pdf, line[2:], line_h=7.5, width=70)
            continue
        if line.startswith("## "):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 13)
            write_wrapped(pdf, line[3:], line_h=6.8, width=84)
            continue
        if line.startswith("### "):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 11)
            write_wrapped(pdf, line[4:], line_h=6.2, width=96)
            continue

        if line.startswith("- "):
            pdf.set_font("Helvetica", "", 11)
            write_wrapped(pdf, f"* {txt[2:]}", line_h=5.6, width=102)
            continue

        if line.startswith("|"):
            # Keep markdown tables readable in monospaced lines.
            pdf.set_font("Courier", "", 8.3)
            write_wrapped(pdf, txt, line_h=4.8, width=132)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 9)
            write_wrapped(pdf, txt, line_h=5.0, width=120)
            continue

        pdf.set_font("Helvetica", "", 11)
        write_wrapped(pdf, txt, line_h=5.6, width=108)

    total_pages = pdf.page_no()
    for page_num in range(1, total_pages + 1):
        pdf.page = page_num
        pdf.set_y(-10)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, f"Page {page_num}", 0, 0, "C")

    pdf.output(str(dst))


def main() -> None:
    repo = Path(__file__).resolve().parents[1]

    report_pairs = [
        (repo / "app" / "THREATMODEL.md", repo / "THREAT_MODEL.pdf", "Threat Model Report"),
        (repo / "Final_Report.md", repo / "Final_Report.pdf", "Final Sprint Report"),
    ]

    for src, dst, title in report_pairs:
        if not src.exists():
            raise FileNotFoundError(f"Missing source markdown: {src}")
        render_markdown_to_pdf(src, dst, title)
        print(f"Generated: {dst} ({dst.stat().st_size} bytes)")

    # Keep legacy app copy in sync for convenience.
    app_copy = repo / "app" / "THREATMODEL.PDF"
    app_copy.write_bytes((repo / "THREAT_MODEL.pdf").read_bytes())
    print(f"Copied: {app_copy} ({app_copy.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
