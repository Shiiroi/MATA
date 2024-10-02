# MATA

A voice-controlled text-to-speech software for blind and visually impaired learners (Grade 12 Research).

## Features
- Extracts text from chosen pdf files
- Utilizes Text-to-Speech to play audio version of the file.
- Voice Control to
  - pause
  - play
  - stop
  - rewind
  - fast forward
  - play next, and
  - previous

## Prerequisites
- Python 3.x
- Virtual Environment (optional)



## Installation
### Method 1

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Shiiroi/GoPush.git
2. **Create a venv (optional)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    .\venv\Scripts\activate  # On Windows
3. **Install requirements.txt**
    ```bash
    pip install -r requirements.txt
4. **Run the application**

   NOTE: Make sure you are in the right directory 
    ```bash
    python main.py
### Method 2
1. Download the dist folder, then run `.exe`


## Contact Information

For any questions or feedback, please reach out to the me:

- **Email**: vmagwili@gmail.com
- **GitHub**: [Shiiroi](https://github.com/Shiiroi)

## Acknowledgments

This project is inspired by the need for accessible education tools for blind and visually impaired learners. Special thanks to the developers of the libraries used in this project for their invaluable contributions.

## License

This project is licensed under the GNU General Public License v3.0. You may copy, distribute, and modify the software as long as you track changes/dates in source files. Any modifications to this project must also be made available under the same license. For more information, see the LICENSE file.

## Code Reference

The base code for the MP3 player side of the project is from [Bloom Player](https://github.imc.re/bitan005/Bloom-Player?tab=readme-ov-file) developed by [@bitan005](https://github.com/bitan005) and [@TheKaushikGoswami](https://github.com/TheKaushikGoswami), licensed under GNU GPLv3. The original project was used as a foundation for the development of the text extraction, text-to-speech, and voice-control features in MATA.
