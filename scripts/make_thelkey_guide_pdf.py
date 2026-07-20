"""Genera un PDF sencillo que explica el flujo de THEKEY para una aplicacion.

Se basa en el flujo real verificado del RunCoordinator:
  create -> baseline -> plan -> approve -> execute -> verify -> decide -> close
con los 4 gates (BUILD, UNIT_TESTS, SECURITY, DOCUMENTATION) y el estado por run.
"""

from fpdf import FPDF

ACCENT = (33, 99, 140)      # azul THEKEY
DARK = (40, 40, 40)
GREY = (110, 110, 110)
LIGHT = (235, 242, 248)
GATE = (46, 125, 70)


def _txt(pdf, w, h, txt, size=10, color=DARK, style=""):
    pdf.set_font("Helvetica", style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(w, h, txt)


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "THEKEY - Como procesa tu aplicacion (guia sencilla)", align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, f"Pagina {self.page_no()}  -  klssxx/THEKEY  -  v0.2.0", align="C")


def title(pdf, txt):
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 8, txt)
    pdf.ln(1)


def h2(pdf, txt):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 7, txt)
    pdf.ln(0.5)


def body(pdf, txt, size=10):
    _txt(pdf, 0, 5.2, txt, size=size)
    pdf.ln(1.5)


def bullet(pdf, txt, size=10):
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(*DARK)
    x = pdf.get_x()
    pdf.cell(5, 5.2, "-")
    pdf.set_x(x + 5)
    pdf.multi_cell(0, 5.2, txt)


def box(pdf, label, txt, fill=LIGHT, border=ACCENT):
    pdf.ln(1.5)
    pdf.set_x(pdf.l_margin)
    # label chip
    pdf.set_fill_color(*border)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"  {label}", fill=True, ln=1)
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(*fill)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(0, 4.8, txt, fill=True, border="L")
    pdf.ln(1)


def state_chain(pdf):
    """Dibuja la cadena de estados como cajas conectadas."""
    states = [
        ("SUBMITTED", "Llega la app"),
        ("BASELINED", "Se captura el estado inicial"),
        ("ANALYZED", "Se entiende el codigo"),
        ("PLAN_PROPUESTO", "Se propone el cambio"),
        ("APROBADO", "Tu visto bueno"),
        ("IMPLEMENTADO", "Se aplica el cambio"),
        ("TESTED", "Se ejecutan los tests"),
        ("RELEASE_ELIGIBLE", "Listo para publicar"),
    ]
    pdf.set_font("Helvetica", "B", 8.5)
    col_w = 22
    gap = 3
    x0 = pdf.get_x()
    y = pdf.get_y()
    for i, (st, desc) in enumerate(states):
        x = x0 + i * (col_w + gap)
        if x + col_w > pdf.w - pdf.r_margin:
            # wrap to next line
            x = x0
            y += 16
        pdf.set_xy(x, y)
        pdf.set_fill_color(*LIGHT)
        pdf.set_draw_color(*ACCENT)
        pdf.set_text_color(*ACCENT)
        pdf.rect(x, y, col_w, 9, style="DF")
        pdf.set_xy(x + 1, y + 1.2)
        pdf.multi_cell(col_w - 2, 3.2, st, align="C")
        pdf.set_xy(x, y + 9.5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*GREY)
        pdf.multi_cell(col_w, 3, desc, align="C")
        pdf.set_font("Helvetica", "B", 8.5)
        if i < len(states) - 1:
            nx = x + col_w
            if nx + col_w <= pdf.w - pdf.r_margin:
                pdf.set_draw_color(*ACCENT)
                pdf.line(nx, y + 4.5, nx + gap, y + 4.5)
    pdf.set_xy(x0, y + 22)


def gates_table(pdf):
    rows = [
        ("1. BUILD", "La app compila / instala sin errores", "Obligatorio"),
        ("2. UNIT_TESTS", "Los tests automaticos pasan", "Obligatorio"),
        ("3. SECURITY", "Sin secretos ni codigo peligroso", "Obligatorio"),
        ("4. DOCUMENTATION", "Docs coherentes con el codigo", "Obligatorio"),
        ("Smoke (opcional)", "Solo BUILD + TESTS para iterar rapido", "LAUNCH_SMOKE_TEST"),
    ]
    col1, col2, col3 = 38, 110, 0
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col1, 7, "  Gate", border=0, fill=True)
    pdf.cell(col2, 7, "  Que comprueba", border=0, fill=True)
    pdf.cell(0, 7, "  Tipo", border=0, fill=True, ln=1)
    for i, (g, d, t) in enumerate(rows):
        pdf.set_fill_color(*(LIGHT if i % 2 == 0 else (245, 248, 251)))
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(col1, 7, "  " + g, border=0, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(col2, 7, "  " + d, border=0, fill=True)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(*GATE)
        pdf.cell(0, 7, "  " + t, border=0, fill=True, ln=1)


def build():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # ---- Portada / intro ----
    title(pdf, "Que le pasa a tu aplicacion cuando la entregas a THEKEY")
    body(pdf,
        "THEKEY es un sistema que revisa y autoriza cambios de codigo de forma "
        "segura y verificable. No es una IA que 'hace lo que quiera': es un proceso "
        "controlado, paso a paso, donde cada decision deja evidencia y nada se aprueba "
        "sin que se haya comprobado.")
    box(pdf, "Idea clave",
        "Imagina una linea de montaje con puestos de control. Tu aplicacion entra por "
        "un extremo y solo sale por el otro si pasa TODOS los controles. Si falla uno, "
        "se detiene y se te explica por que.")

    # ---- Paso 1: la entrega ----
    h2(pdf, "1. La entrega (SUBMITTED)")
    body(pdf,
        "Tu aplicacion llega a THEKEY junto con una peticion clara: que cambio quieres "
        "hacer (corregir un bug, anadir una funcion, etc.). THEKEY le asigna un ID unico "
        "de ejecucion (run) y crea su propia carpeta aislada. Nada de lo que ocurra aqui "
        "toca tu carpeta original sin permiso.")

    # ---- Paso 2: la foto inicial ----
    h2(pdf, "2. La foto inicial (BASELINED)")
    body(pdf,
        "Antes de tocar nada, THEKEY guarda el estado actual de la app: archivos, hashes "
        "y configuracion. Es como una foto del 'antes'. Asi, si algo sale mal, siempre "
        "puede volver a ese punto exacto (rollback). El estado se guarda por cada ejecucion, "
        "no compartido, para que varias revisiones no se pisen entre si.")

    # ---- Paso 3: analisis ----
    h2(pdf, "3. Analisis (ANALYZED)")
    body(pdf,
        "THEKEY lee el codigo y entiende de que tipo de proyecto se trata (Python simple, "
        "aplicacion de escritorio, web, o un archivo suelto). Con eso decide que herramientas "
        "y limites usar. Todo este analisis se hace desde el codigo real, no de suposiciones.")

    # ---- Paso 4: plan ----
    h2(pdf, "4. Propuesta de plan (PLAN_PROPUESTO)")
    body(pdf,
        "Se propone un plan concreto: que archivos cambiar y por que. El plan se describe de "
        "forma restringida y validada; no puede contener acciones que no esten permitidas para "
        "el rol que opera.")

    # ---- Paso 5: tu aprobacion ----
    h2(pdf, "5. Tu aprobacion (PLAN_APPROVED)")
    box(pdf, "Punto de control humano",
        "Aqui TU decides. THEKEY no aplica ningun cambio hasta que tu lo apruebes. Si no te "
        "convence el plan, lo rechazas y el proceso se detiene. Esta es la parte de "
        "'gobernanza': el humano manda, la maquina ejecuta bajo control.")
    body(pdf, "(En modo demostracion este paso se aprueba automaticamente para enseñar el flujo.)")

    # ---- Paso 6: implementacion ----
    h2(pdf, "6. Implementacion (IMPLEMENTED)")
    body(pdf,
        "Se aplican los cambios dentro del espacio de trabajo aislado. Los cambios se registran "
        "como un diff (la diferencia exacta respecto a la foto inicial). El controlador anota cada "
        "paso en un registro que nadie puede alterar sin que se note.")

    # ---- Paso 7: verificacion / gates ----
    pdf.add_page()
    h2(pdf, "7. Verificacion: los 4 controles (TESTED)")
    body(pdf,
        "Antes de decir 'listo', la app debe pasar cuatro controles obligatorios. Si uno falla, "
        "el proceso se bloquea y te dice cual:")
    pdf.ln(1)
    gates_table(pdf)
    pdf.ln(2)
    box(pdf, "Evidencia, no promesas",
        "Cada control produce EVIDENCIA real (resultados de comandos ejecutados, no texto "
        "inventado) y se firma digitalmente. Si alguien manipula un registro, THEKEY lo detecta.")

    # ---- Paso 8: decision ----
    h2(pdf, "8. Decision y cierre (RELEASE_ELIGIBLE)")
    body(pdf,
        "Si pasa los 4 controles, la app queda 'apta para publicar'. THEKEY genera un resumen con "
        "el plan, los cambios, la evidencia y la decision. El estado final se guarda y el proceso "
        "se cierra. Tu aplicacion original solo se actualiza si tu lo autorizas.")

    # ---- Diagrama de estados ----
    pdf.add_page()
    h2(pdf, "El camino de estados (diagrama)")
    body(pdf, "Asi se mueve la app de un estado a otro. Flecha recta = flujo normal; si falla "
              "algun control, salta a BLOQUEADO o FALLADO y puede volver atras (rollback).")
    pdf.ln(2)
    state_chain(pdf)
    pdf.ln(2)
    body(pdf,
        "Estados de parada: BLOQUEADO (algo impide continuar), FALLADO (un control fallo), y "
        "ROLLED_BACK (se volvio a la foto inicial). Ninguno de estos publica cambios.")

    # ---- Resumen ----
    h2(pdf, "En resumen")
    bullet(pdf, "Tu app entra aislada y con su propio ID de ejecucion.")
    bullet(pdf, "Se guarda una foto inicial para poder volver atras.")
    bullet(pdf, "Se analiza y se propone un plan concreto.")
    bullet(pdf, "TU apruebas antes de cualquier cambio.")
    bullet(pdf, "Se aplican los cambios en un espacio aislado.")
    bullet(pdf, "Pasa 4 controles obligatorios con evidencia firmada.")
    bullet(pdf, "Solo si todo va bien queda lista para publicar.")
    pdf.ln(2)
    box(pdf, "Por que importa",
        "Porque tienes un proceso auditable: sabes exactamente que se cambio, por que, con que "
        "pruebas, y quien lo aprobo. Cero sorpresas, cero 'confia en mi'.",
        fill=(240, 248, 240), border=GATE)

    return pdf


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "THEKEY_Como_procesa_tu_aplicacion.pdf")
    build().output(out)
    print("PDF generado:", out)
