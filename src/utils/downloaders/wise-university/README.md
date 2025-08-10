## How to get the lesson urls to use the downloader script

### Workflow

Use the JS snippet below grab all the unique urls lecture by lecture. This requires:

1. Going through all the videos in the lecture by extracting them all from the network log.
2. The snippet only works in Chrome.
3. In the network tap ensure the dropdown is not `top` but instead `scorm_object`.
4. Run the script. Extract the url and save them all to a md file. Put all the links from the md file in wise-uni.txt
5. Run the python script.

```javascript
const urls = performance
	.getEntriesByType('resource')
	.map((resource) => resource.name)
	.filter((name) => name.includes('.mp4'));

const uniqueUrls = [...new Set(urls)];

console.log(uniqueUrls.join('\n'));
```
