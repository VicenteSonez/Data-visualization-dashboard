import asyncio
import os
from playwright.async_api import async_playwright

async def generate_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Obtener la ruta absoluta del archivo HTML
        html_path = f"file:///{os.path.abspath('dashboard.html').replace(chr(92), '/')}"
        
        await page.goto(html_path, wait_until='networkidle')
        
        # Esperar un poco para asegurar que las imágenes se carguen completamente
        await page.wait_for_timeout(2000)
        
        # Intentar generar el PDF en ambas rutas para actualizar el visor del usuario
        success_paths = []
        for pdf_name in ["Entregable_Dashboard_Final.pdf", "Entregable_Dashboard_Final_copia.pdf"]:
            try:
                await page.pdf(
                    path=pdf_name,
                    format="A4",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
                )
                print(f"PDF generado exitosamente como '{pdf_name}'.")
                success_paths.append(pdf_name)
            except Exception as e:
                if isinstance(e, PermissionError) or "Permission denied" in str(e):
                    print(f"AVISO: No se pudo sobrescribir '{pdf_name}' porque está abierto en otro programa.")
                else:
                    raise e
        
        if not success_paths:
            alt_path = "Entregable_Dashboard_Final_v3.pdf"
            await page.pdf(
                path=alt_path,
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
            )
            print(f"Se generó una copia alternativa en: '{alt_path}'.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(generate_pdf())
