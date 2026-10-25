"""Convert matplotlib figures to sized report images."""
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, Spacer, PageBreak
from visualization import build_figures


def charts_section(report, styles):
    """Convert named figures into consistently sized PDF images."""
    story = [Paragraph('Network Analysis Visualizations', styles['Heading1'])]
    figures = build_figures(report.network, report.solution, report.model_type)
    for index, (title, figure) in enumerate(figures):
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', dpi=220, bbox_inches='tight', pad_inches=0.07)
        buffer.seek(0)
        width, height = PILImage.open(buffer).size
        scale = min(6.0 * inch / width, 7.6 * inch / height)
        buffer.seek(0)
        story.extend([Spacer(1, 0.05 * inch), Paragraph(title, styles['Heading2']),
                      Image(buffer, width=width * scale, height=height * scale)])
        if index < len(figures) - 1:
            story.append(PageBreak())
        plt.close(figure)
    return story
