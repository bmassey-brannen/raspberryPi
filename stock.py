#!/usr/bin/env python
import os
import time
import pygame
import requests
from bs4 import BeautifulSoup

def get_stock_data(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # Mimic a browser user-agent
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {ticker}, status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    if not price_tag:
        raise Exception(f"Could not find price for {ticker}")
    try:
        price = float(price_tag.text.replace(',', ''))
    except ValueError:
        raise Exception(f"Invalid price format for {ticker}: {price_tag.text}")

    change_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
    percent_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
    if not change_tag or not percent_tag:
        raise Exception(f"Could not find change data for {ticker}")
    try:
        change = float(change_tag.text.replace(',', '').replace('+', '').replace('(', '').replace(')', '').strip())
        percent = float(percent_tag.text.replace('%', '').replace('+', '').replace('(', '').replace(')', '').strip())
    except ValueError:
        raise Exception(f"Invalid change format for {ticker}: Change='{change_tag.text}', Percent='{percent_tag.text}'")

    return {
        "price": price,
        "change": change,
        "percent": percent,
    }

def update_tickers(tickers):
    new_tickers = input("Enter new tickers separated by a comma: ").split(',')
    return [ticker.strip().upper() for ticker in new_tickers if ticker.strip()]

def main():
    # Colours
    WHITE = (255, 255, 255)
    GREY = (240, 240, 240)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    tickersymbols = ['RKLB', 'ASTS', 'SPY', 'QQQ', 'NVDA', 'GME']

    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    pygame.mouse.set_visible(False)
    
    # Set the display mode to full screen with 800x400 resolution
    lcd = pygame.display.set_mode((800, 400), pygame.FULLSCREEN)
    lcd.fill(BLACK)
    pygame.display.update()

    myfont = pygame.font.SysFont("arial", 40)

    keep_running = True

    try:
        while keep_running:
            lcd.fill(BLACK)
            print("Fetching data...")

            total_height = 70 * len(tickersymbols)  # Calculate total height
            start_y = (500 - total_height) // 2  # Center vertically

            max_width = 0
            stock_display_data = []

            for tickerSymbol in tickersymbols:
                try:
                    allInfo = get_stock_data(tickerSymbol)
                    stock_display = f"${allInfo['price']:,.2f} ({allInfo['change']:+.2f}, {allInfo['percent']:+.2f}%)"
                    text_width, _ = myfont.size(stock_display)
                    max_width = max(max_width, text_width)
                    stock_display_data.append((tickerSymbol, stock_display, allInfo['change'] > 0))
                except Exception as e:
                    print(f"Error fetching data for {tickerSymbol}: {e}\nWaiting 20 seconds.")
                    time.sleep(20)
                    continue

            start_x = (800 - (max_width + 200)) // 2  # Center horizontally with padding for ticker symbols

            for i, (tickerSymbol, stock_display, is_positive) in enumerate(stock_display_data):
                y_position = start_y + i * 70

                # Determine color
                color = GREEN if is_positive else RED

                ticker_text = myfont.render(tickerSymbol, True, WHITE)
                stock_text = myfont.render(stock_display, True, color)

                lcd.blit(ticker_text, (start_x, y_position))
                lcd.blit(stock_text, (start_x + 200, y_position))

            pygame.display.update()
            print("Done.\n")

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        lcd = pygame.display.set_mode((800, 400), pygame.FULLSCREEN if not lcd.get_flags() & pygame.FULLSCREEN else 0)
                    elif event.key == pygame.K_t:
                        tickersymbols = update_tickers(tickersymbols)

            time.sleep(60)

    except KeyboardInterrupt:
        print("\nQuitting...")
        keep_running = False
    except Exception as e:
        print(f"Error: {e}")
        lcd.fill(BLACK)
        textToPrint = myfont.render("ERROR...", True, WHITE)
        lcd.blit(textToPrint, (10, 180))
        pygame.display.update()
        raise

if __name__ == '__main__':
    main()
