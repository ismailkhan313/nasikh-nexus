import { getBookInfo, getPage } from 'turath-sdk';
import { writeFile } from 'fs/promises';

const BOOK_ID = 8246;

async function downloadBook(bookId) {
	try {
		console.log(`🚀 Fetching info for book ID: ${bookId}...`);
		const bookInfo = await getBookInfo(bookId);

		// --- CORRECTED SECTION ---
		// The chapter data is in bookInfo.indexes.headings
		const chapters = bookInfo.indexes?.headings;
		const title = bookInfo.meta?.name || 'Untitled';
		const authorInfo = bookInfo.meta?.info.match(/المؤلف: (.+?)\n/);
		const authorName = authorInfo ? authorInfo[1] : 'Unknown Author';
		// Get total pages from the 'volume_bounds' data
		const totalPages = bookInfo.indexes?.volume_bounds?.['1']?.[1];

		if (!chapters || chapters.length === 0 || !totalPages) {
			console.error(
				'❌ Error: Could not find chapter list or total pages in the API response.'
			);
			console.log('Please check the full response below:');
			console.dir(bookInfo, { depth: null });
			return;
		}

		console.log(`📖 Title: ${title}`);
		console.log(`✍️ Author: ${authorName}`);
		console.log(`📄 Total Pages: ${totalPages}`);

		let fullBookContent = `# ${title}\n\nBy: ${authorName}\n\n---\n\n`;

		// Loop through all headings to build the book
		for (let i = 0; i < chapters.length; i++) {
			const chapter = chapters[i];
			const startPage = chapter.page;

			// The end page is the page before the next heading starts, or the last page of the book.
			const endPage =
				i + 1 < chapters.length ? chapters[i + 1].page - 1 : totalPages;

			// Use different markdown for different heading levels
			const headingMarker = '#'.repeat(chapter.level + 1); // level 1 -> ##, level 2 -> ###

			console.log(
				`\nDownloading: "${chapter.title}" (Pages ${startPage}-${endPage})`
			);
			fullBookContent += `${headingMarker} ${chapter.title}\n\n`;

			// Fetch all pages for the current section
			for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
				try {
					const pageData = await getPage(bookId, pageNum);
					if (pageData && pageData.text) {
						fullBookContent += pageData.text + '\n';
					}
					process.stdout.write('▪'); // Progress indicator
				} catch (pageError) {
					console.error(
						`\n⚠️ Failed to download page ${pageNum}: ${pageError.message}`
					);
				}
			}
			fullBookContent += '\n';
		}

		const fileName = `book_${bookId}_${title.replace(/[\s/]/g, '_')}.txt`;
		await writeFile(fileName, fullBookContent, 'utf8');
		console.log(`\n\n✅ Success! Book content has been saved to: ${fileName}`);
	} catch (error) {
		console.error(`\n\n❌ An unexpected error occurred: ${error.message}`);
	}
}

// Run the script
downloadBook(BOOK_ID);
