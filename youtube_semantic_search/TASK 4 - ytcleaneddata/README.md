# YouTube Data Cleaning Script

This Python script cleans a YouTube dataset CSV file by removing special
characters, converting text to lowercase, and standardizing video
duration into seconds.

## 🚀 Features

-   **Text Cleaning:** Removes unwanted characters from title and
    transcript columns.\
-   **Duration Conversion:** Converts HH:MM:SS or PT#H#M#S formats into
    total seconds.\
-   **Safe Processing:** Handles missing values gracefully.\
-   **CSV Output:** Saves the cleaned data to a new CSV file.

## 🧠 Functions Overview

### `clean_text(text)`

-   Removes non-alphanumeric characters except `. , ! ?`
-   Converts text to lowercase and trims spaces.

### `duration_to_seconds(duration)`

-   Converts duration strings into seconds.
-   Handles both `HH:MM:SS` and ISO 8601 (`PT#H#M#S`) formats.
-   Returns 0 for missing or invalid entries.

### `clean_csv(input_path, output_path)`

-   Reads a CSV file.
-   Cleans the specified columns if present (`title`, `transcript`,
    `duration`).
-   Writes the cleaned data to the output CSV path.

## ⚙️ Usage

Place your CSV file in the target folder (e.g.,
`G:\infosys_internship\TASK 4 - ytcleaneddata`).\
Update the file paths in the script:

``` python
input_csv = r"G:\infosys_internship\TASK 4 - ytcleaneddata\master_dataset_updated.csv"
output_csv = r"G:\infosys_internship\TASK 4 - ytcleaneddata\cleaned_youtube_details.csv"
```

Run the script:

``` bash
python clean_youtube_data.py
```

The cleaned file will be saved as:

    cleaned_youtube_details.csv

## 📁 Output Example

  title          transcript                    duration   duration_seconds
  -------------- ----------------------------- ---------- ------------------
  sample video   this is a sample transcript   PT2M30S    150

## 📄 Requirements

-   Python 3.x\
-   pandas

Install dependencies:

``` bash
pip install pandas
```

## ✅ Example Output Message

✅ Cleaned CSV saved to:
`G:\infosys_internship\TASK 4 - ytcleaneddata\cleaned_youtube_details.csv`

------------------------------------------------------------------------

**Author:** Infosys Internship Project\
**Task:** TASK 4 -- YouTube Data Cleaning\
**Language:** Python
