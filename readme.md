# ArtiFactual

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/downloads/)

ArtiFactual is a simple library and desktop application that allows users to decode and view encoded information from images easily and conveniently. It works by reading generation information or imprinted data of an image and displaying it, ensuring that the image file serves as a standalone ship.

<img src="./_repo/screenshot.png" width="200px" height="200px">

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contribution](#contribution)
- [License](#license)

## Features

- Decode encoded information from images, either metadata or fingerprinted.
- Encode information into images (Library only for now)
- View decoded data in a simple and convenient way
- Supports drag and drop Files and URLs (so works w/ Discord and links)
- Uses QT6/PySide6 for GUI
- Standalone desktop application for ease of use

## Example

https://user-images.githubusercontent.com/2738686/231028804-8a1ee6d6-8579-4a3d-95e9-00993b96d2ff.mp4

## Getting Started

### Prerequisites

- Python 3.7 or higher

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/kjerk/artifactual.git
   ```

2. Navigate to the project directory:

   ```
   cd artifactual
   ```

3. Install required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python app_dropid.py
   ```

### Todo List
* ✅ Add readme and screenshots
* ✅ Be excellent to each other
* ☐ Add support for decoding with a password (in lib but not gui)

## License

ArtiFactual is licensed under the [MIT License](./LICENSE.txt).
