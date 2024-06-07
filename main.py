import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

# Function to fetch the HTML and linked CSS, modify HTML links, and remove scripts
def download_html_css(url, directory):
    try:
        # Determine base URL and subdirectory name
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        subdirectory = parsed_url.netloc.replace('www.', '')  # Use domain name as subdirectory, removing 'www.'

        # Create the directory structure if it does not exist
        full_path = os.path.join(directory if directory else os.getcwd(), "downloads", subdirectory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Directory created at {full_path}")

        # Fetch the webpage
        response = requests.get(url, timeout=10)  # Added timeout for the request
        response.raise_for_status()  # Will halt if the fetch was unsuccessful
        print("Webpage fetched successfully.")

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script tags
        [script.decompose() for script in soup.find_all("script")]
        print("Script tags removed.")

        # Find all linked CSS files and update HTML links
        for link in soup.find_all("link"):
            if 'stylesheet' in link.get('rel', []):
                original_css_url = link['href']
                css_url = urljoin(base_url, original_css_url)  # Ensure the CSS URL is relative to the base URL

                try:
                    # Download CSS files
                    css_response = requests.get(css_url)
                    css_response.raise_for_status()

                    # Get the CSS file name and update the link in HTML
                    css_filename = css_url.split("/")[-1]
                    link['href'] = css_filename  # Update the href to point to local file

                    # Save the CSS file
                    with open(f"{full_path}/{css_filename}", "w", encoding='utf-8') as css_file:
                        css_file.write(css_response.text)
                    print(f"CSS file downloaded and saved: {css_filename}")
                except requests.exceptions.HTTPError as e:
                    print(f"Failed to download {css_url}: {e}")
                    link.decompose()  # Remove link if CSS file can't be downloaded

        # Save the modified HTML file
        with open(f"{full_path}/index.html", "w", encoding='utf-8') as file:
            file.write(str(soup))
        print(f"Modified HTML saved to {full_path}/index.html")

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
    except IOError as e:
        print(f"File writing error occurred: {e}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

# Get user input for the URL and directory
url = input("Enter the URL of the website: ")
directory = input("Enter the directory path to save the files: (Press enter to save in current directory)") or None

# Example usage with user input
download_html_css(url, directory)
