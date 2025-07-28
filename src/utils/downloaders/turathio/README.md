Run scripts in terminal as `node <name of script>`

Turath Book Downloader
This Node.js script downloads a book from the Turath online library using the turath-sdk. It fetches the book's metadata (title, author) and all of its pages, then compiles them into a single, well-formatted text file.

The script organizes the content by chapter headings, using Markdown formatting for titles, and includes progress indicators as it downloads the pages.

How to Use
Prerequisites

Node.js: You must have Node.js installed on your computer. You can download it from nodejs.org.

Setup

Save the Script: Save the code into a file named downloadBook.js (or any other name you prefer).

Open Your Terminal: Navigate to the directory where you saved the file.

Initialize a Node.js Project: If you don't already have a package.json file, run this command to create one:

npm init -y

Install Dependencies: The script requires the turath-sdk library. Install it using npm:

npm install turath-sdk

Running the Script

Execute the Script: Run the script from your terminal using Node.js:

node downloadBook.js

Check the Output: The script will first print the book's title, author, and total page count. It will then display its progress as it downloads the content.

Once finished, a new text file will be created in the same directory, named something like book_12836_Book_Title.txt. This file contains the complete, formatted text of the book.

Customization

To download a different book, simply change the BOOK_ID constant at the top of the script file:

// Before
const BOOK_ID = 12836;

// After (example for a different book)
const BOOK_ID = 99999; // Replace with the ID of the book you want
