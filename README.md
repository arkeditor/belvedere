# City of Belvedere RSS Generator

A Python script that automatically scrapes the [City of Belvedere news page](https://www.cityofbelvedere.org/news) and generates an RSS feed from the articles.

## Features

- 🔍 **Smart Article Detection** - Uses multiple strategies to find articles on the page
- 📰 **RSS 2.0 Compliant** - Generates proper RSS XML format with all required metadata
- 🛡️ **Error Handling** - Robust handling of network issues and malformed content
- 🚀 **Easy to Use** - Simple command-line interface
- ⚡ **Automation Ready** - Perfect for cron jobs or scheduled tasks

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/arkeditor/belvedere-rss-generator.git
   cd belvedere-rss-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
# Generate RSS feed to default file (belvedere_news.xml)
python belvedere_rss_generator.py

# Generate RSS feed to custom file
python belvedere_rss_generator.py my_custom_feed.xml
```

### Example Output
The script will display progress and found articles:
```
Fetching Belvedere news page...
Parsing articles...
Found 5 articles
  1. Connolly Calls for Rethink of Tiburon Blvd Bike Lanes
  2. City Council Goals & Updates
  3. Maintaining a Fire-Smart Yard
  4. Free Curbside Vegetation Pick Up Begins May 20
  5. Welcome New Volunteers & See More Opportunities

Generating RSS feed...
RSS feed saved to belvedere_news.xml

RSS feed successfully generated!
You can now use 'belvedere_news.xml' with any RSS reader.
```

## Automation

### Using Cron (Linux/Mac)
Set up automatic feed updates every hour:
```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed)
0 * * * * /usr/bin/python3 /path/to/belvedere_rss_generator.py /var/www/html/belvedere_feed.xml
```

### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., hourly)
4. Set action to run: `python C:\path\to\belvedere_rss_generator.py C:\path\to\output\feed.xml`

## RSS Feed Format

The generated RSS feed includes:
- **Channel metadata** (title, description, language, etc.)
- **Article items** with:
  - Title extracted from page
  - Direct link to original article
  - Description/summary
  - Publication date
  - Unique GUID

## Dependencies

- `requests` - For fetching web pages
- `beautifulsoup4` - For HTML parsing
- `lxml` - XML processing (faster parser for BeautifulSoup)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal use and educational purposes. Please respect the City of Belvedere's website terms of service and don't overload their servers with too frequent requests.
