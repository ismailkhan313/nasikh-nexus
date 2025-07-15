import { getBookInfo, getPage } from 'turath-sdk';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

// --- Helper function to create safe filenames ---
function sanitizeFilename(name) {
	// Removes characters that are invalid in filenames and replaces spaces with underscores
	return name
		.replace(/[<>:"/\\|?*]/g, '')
		.replace(/\s+/g, '_')
		.substring(0, 100);
}

const BOOK_ID = 313;

async function downloadBookByChapter(bookId) {
	try {
		console.log(`🚀 Fetching info for book ID: ${bookId}...`);
		const bookInfo = await getBookInfo(bookId);

		const chapters = bookInfo.indexes?.headings;
		const title = bookInfo.meta?.name || 'Untitled';
		const totalPages = bookInfo.indexes?.volume_bounds?.['1']?.[1];

		if (!chapters || chapters.length === 0 || !totalPages) {
			console.error(
				'❌ Error: Could not find chapter list or total pages in the API response.'
			);
			return;
		}

		// 1. Create a dedicated directory for the book's files
		const bookDirectory = `book_${bookId}_${sanitizeFilename(title)}`;
		await mkdir(bookDirectory, { recursive: true });
		console.log(
			`\n📂 Created directory to store chapter files: ./${bookDirectory}`
		);

		// 2. Loop through each chapter to create individual files
		for (let i = 0; i < chapters.length; i++) {
			const chapter = chapters[i];
			let chapterContent = `# ${chapter.title}\n\n`; // Start with the chapter title
			const startPage = chapter.page;
			const endPage =
				i + 1 < chapters.length ? chapters[i + 1].page - 1 : totalPages;

			console.log(
				`\nDownloading section: "${chapter.title}" (Pages ${startPage}-${endPage})`
			);

			// Fetch all pages for the current chapter
			for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
				try {
					const pageData = await getPage(bookId, pageNum);
					if (pageData && pageData.text) {
						chapterContent += pageData.text + '\n';
					}
					process.stdout.write('▪'); // Progress indicator
				} catch (pageError) {
					console.error(
						`\n⚠️ Failed to download page ${pageNum}: ${pageError.message}`
					);
				}
			}

			// 3. Create a clean, sorted filename for the chapter
			const chapterNumber = (i + 1).toString().padStart(2, '0'); // "01", "02", etc.
			const chapterFilename = `${chapterNumber}_${sanitizeFilename(
				chapter.title
			)}.txt`;
			const filePath = path.join(bookDirectory, chapterFilename);

			// 4. Save the current chapter's content to its own file
			await writeFile(filePath, chapterContent, 'utf8');
			console.log(`\n✅ Saved: ${filePath}`);
		}

		console.log(
			`\n\n🎉 All chapters have been downloaded and saved successfully into the "${bookDirectory}" folder!`
		);
	} catch (error) {
		console.error(`\n\n❌ An unexpected error occurred: ${error.message}`);
	}
}

downloadBookByChapter(BOOK_ID);
