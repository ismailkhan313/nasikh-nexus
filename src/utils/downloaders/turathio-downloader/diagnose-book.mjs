import { getBookInfo } from 'turath-sdk';

const BOOK_ID = 313;

async function diagnoseBook(bookId) {
	console.log(`🚀 Diagnosing book ID: ${bookId}...`);
	try {
		const bookInfo = await getBookInfo(bookId);

		console.log('\n--- Full API Response Received ---');
		// This will print the entire object we get back from the server
		console.dir(bookInfo, { depth: null });

		console.log('\n--- Analysis ---');
		if (!bookInfo) {
			console.log('Result: The API returned an empty or null response.');
		} else if (!bookInfo.index || bookInfo.index.length === 0) {
			console.log(
				"Result: The book's metadata was returned, but it is missing the chapter 'index'."
			);
		} else {
			console.log(
				'Result: A chapter index was found! The original script may have a different issue.'
			);
		}
		console.log(
			'\nConclusion: This output strongly suggests that full book details are only available to authenticated users.'
		);
	} catch (error) {
		console.error(
			`\n❌ An error occurred during the API call: ${error.message}`
		);
	}
}

diagnoseBook(BOOK_ID);
