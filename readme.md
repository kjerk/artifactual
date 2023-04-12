# ArtiFactual

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/downloads/)

ArtiFactual is a simple library and desktop application that allows users to decode and view encoded information from images easily and conveniently, as well as a backing library that can encode images easily with string metadata that is resilient to metadata stripping. It works by reading/writing generation information or imprinted data of an image and displaying it, ensuring that the image file serves as a standalone ship, and is resilient to the transmission medium.

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

## Embedding Algo (Library)

#### Encoding
1. An image is converted to an array of bytes w/ numpy for ease of use.
2. The offset to the beginning of the last 8 rows of pixels is calculated and then the array is sliced to include only those rows.
3. The image parameters are encoded into a byte string, and then compressed using gz, which is efficient for small text strings.
4. `IF` there is a password/key set in the user options, the compressed string is encrypted using the sha-256 hashed value of the user's password in `AES-256-CBC`, with padding.
5. `0X0CAB005E` is appended as a suffix.
6. For efficiency, rather than loop over pixels, the operation is done in bulk, splitting the data to bits and then [blitting](https://en.wikipedia.org/wiki/Bit_blit) the data over top of the existing image data after truncating the pixel view to the right size. So only as many pixels as it takes to fit the information are affected.
7. The image is reconstituted in place from the byte array without allocating a new image.

#### Decoding
Steps 1, 2 of Encoding, then
1. Extract the bits off the last 8 rows of data and re-compact them.
2. `0X0CAB005E` is sought as a suffix. If not found this was not an imprinted image. If found, the array is sliced to that marker.
3. `IF` there is a password/key set in the user options, the compressed string is decrypted using this password.
4. We check for the magic bytes telling us whether the data is gzip compressed or not, if it is, we decompress it.
5. The byte string is decoded into a utf-8 string and returned.

## Design Considerations
#### Why 0x0CAB005E?
- It's cute. Needed to detect the end of the envelope anyway. 🚂💨🎵

#### Why only 8 rows?
- In order to try to leave an image as unaltered as possible, altering only the last 8 rows of pixels is a happy medium that pushes the data toward the end, but still leaves the image mostly intact. The perceptual difference is still zero, but this way we only affect ~1.5% of the pixels in the image at absolute maximum. That does put a hard constraint on the data size.
- With the gzip compression in place, `3.6KB` of text/json can compress down to `928 bytes`, comfortably fitting in the `1.5KB` space limit.
- This keeps slightly in alignment with jpeg compression (which uses 8x8 blocks) for future endeavors, possibly working across that block size with a jpeg resilient method at a later time.

#### Why gz?
- This is the clear winner for small strings, even testing experimental compression like bz3

![file sizes](https://user-images.githubusercontent.com/2738686/231032207-5910e90b-fa6f-4174-8e7d-17b63b47e9af.png)

## License

ArtiFactual is licensed under the [MIT License](./LICENSE.txt).
