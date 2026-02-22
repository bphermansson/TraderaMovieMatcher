***

```markdown
# Tradera Movie Matcher 🎬

A Python-based desktop application built for Ubuntu/Linux that helps you find the best sellers on [Tradera.com](https://www.tradera.com) for your movie wishlist. 

Instead of buying movies one by one and paying multiple shipping fees, this tool searches for your entire wishlist, cross-references the results, and sorts the sellers based on how many of your wanted movies they have in stock. 

![Screenshot placeholder](https://via.placeholder.com/800x450.png?text=Add+a+screenshot+of+the+app+here)

## ✨ Features

* **Bulk Searching:** Enter multiple movie titles at once.
* **Smart Filtering:** Automatically limits the search to Tradera's specific "Movies" category (Category 13: DVD, Blu-ray, VHS) to avoid irrelevant hits like posters or comic books.
* **Cross-Referencing:** Identifies which sellers have multiple items from your list, saving you money on combined shipping!
* **Detailed Output:** Displays the exact item title, the parsed price, and a list of which movies from your wishlist the seller is *missing*.
* **Clickable Links:** Click `[Öppna annons]` right inside the app to instantly open the auction in your default web browser.
* **Save/Load:** Save your movie wishlist to a `.txt` file and load it back up for future searches.
* **Anti-Blocking & Multithreading:** Uses concurrent background requests and browser-like headers to scrape data quickly without freezing the UI or getting blocked by Cloudflare.

## 🛠️ Prerequisites

This application is built with Python 3 and Tkinter. You will need to install a few dependencies before running it.

Open your terminal and run:

```bash
# Install Tkinter and pip for Python 3
sudo apt update
sudo apt install python3-tk python3-pip

# Install the required Python packages
pip3 install requests beautifulsoup4
```

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/tradera-movie-matcher.git
   cd tradera-movie-matcher
   ```

2. **Make the script executable:**
   ```bash
   chmod +x tradera_matcher.py
   ```

3. **Run the application:**
   ```bash
   ./tradera_matcher.py
   ```

### How to use:
1. Type or paste your movie wishlist into the top text box (one movie title per line).
2. Click **"🔍 Hitta Säljare"** (Find Sellers).
3. Wait a few moments while the app safely scans Tradera.
4. Browse the results! Sellers are sorted so the ones with the most matches appear at the very top. You can easily see the price and click the link to go straight to the auction.

## ⚠️ Disclaimer

This tool is created for educational purposes and personal use. Web scraping should be done responsibly. The script includes delays (`time.sleep()`) to ensure it does not overload Tradera's servers. Tradera may occasionally change their HTML structure, which could require future updates to the scraping logic. 

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

***
