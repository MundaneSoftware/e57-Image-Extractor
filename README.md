# E57 Spherical Image Extractor

A Python-based application to extract spherical images and metadata from `.e57` files, leveraging **Tkinter** for the GUI and industry-standard libraries such as **pye57**, **Pillow**, and **NumPy**. This tool allows users to process multiple `.e57` files, resize spherical images, and save them alongside metadata in a CSV file.

## Features

- **Batch Processing**: Select multiple `.e57` files and process them in one go.
- **Image Extraction**: Extract spherical images from `.e57` files and save them as resized JPEGs.
- **Metadata Recording**: Save translation and rotation metadata to a `coords.csv` file.
- **Progress Bar**: Real-time progress updates for batch processing.
- **User-Friendly GUI**: Simple interface built with Tkinter.

## Requirements

- Python 3.8+
- Libraries:
  - `pye57`
  - `Pillow`
  - `NumPy`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/MundaneSoftware/e57-Image-Extractor.git
   cd e57-spherical-image-extractor
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure that the `pye57` library is installed. You can find installation instructions for `pye57` [here](https://github.com/nu-book/pye57).

## Usage

1. Run the application:
   ```bash
   python extractor.py
   ```

2. Use the GUI to:
   - Select one or more `.e57` files using the **Select Files** button.
   - Click **Start Processing** to extract spherical images and metadata.

3. Output:
   - Resized images are saved in an `output` folder within the same directory as the first `.e57` file.
   - Metadata is recorded in a `coords.csv` file within the `output` folder.

## Output Format

- **Images**: Resized JPEG files with dimensions `8192x4096` pixels.
- **CSV Metadata**:
  - `coords.csv` contains:
    - `image_file_name`: Name of the extracted image.
    - `image_path`: Full path to the saved image.
    - `translation_x, translation_y, translation_z`: Translation coordinates.
    - `rotation_x, rotation_y, rotation_z, rotation_w`: Rotation quaternion values.

Example:
```csv
image_file_name,image_path,translation_x,translation_y,translation_z,rotation_x,rotation_y,rotation_z,rotation_w
scan1.jpeg,/output/scan1.jpeg,1.234,5.678,9.101,0.1,0.2,0.3,0.4
scan2.jpeg,/output/scan2.jpeg,2.345,6.789,10.111,0.5,0.6,0.7,0.8
```

## Project Structure

```plaintext
e57-spherical-image-extractor/
├── extractor.py         # Main application script
├── README.md            # Documentation
├── requirements.txt     # Python dependencies
└── output/              # Automatically created output directory
```

## Dependencies

- [pye57](https://github.com/nu-book/pye57): Library for reading `.e57` files.
- [Pillow](https://pillow.readthedocs.io/): Python Imaging Library (PIL fork) for image processing.
- [NumPy](https://numpy.org/): Numerical library for efficient data handling.
- [Tkinter](https://docs.python.org/3/library/tkinter.html): Standard library for GUI development.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature/bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pye57](https://github.com/nu-book/pye57) for enabling seamless interaction with `.e57` files.
- [Pillow](https://pillow.readthedocs.io/) for robust image handling.
- [NumPy](https://numpy.org/) for efficient numerical operations.
