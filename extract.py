import json
import asyncio
from playwright.async_api import async_playwright

async def get_lat_lon_google_maps(address):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com/maps")
        
        search_box = await page.wait_for_selector("input#searchboxinput")
        await search_box.fill(address)
        await page.keyboard.press("Enter")

        # Espera o resultado carregar        
        await page.wait_for_selector('button[aria-label*="Rotas"], div[aria-label*="Resultados"]', timeout=15000)
        
        url = page.url
        print(f"🌍 URL: {url}")
        try:
            parts = url.split("/@")[1].split(",")
            lat, lon = parts[0], parts[1]
            return {"latitude": lat, "longitude": lon}
        except Exception as e:
            print(f"❌ Erro ao extrair coordenadas: {e}")
            return {"latitude": None, "longitude": None}
        finally:
            await browser.close()


async def process_restaurants(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        restaurants = json.load(f)

    for r in restaurants:
        print(f"🔎 Buscando: {r['name']}")
        coords = await get_lat_lon_google_maps(r["address"] + ", Londrina, Brazil")
        r.update(coords)
        await asyncio.sleep(2)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)

    print(f"✅ Arquivo salvo: {output_file}")


if __name__ == "__main__":
    input_json = "restaurantes_brasil_coffee_week.json"
    output_json = "restaurantes_brasil_coffee_week_com_coords.json"
    asyncio.run(process_restaurants(input_json, output_json))
