import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const postsDirectory = path.join(process.cwd(), 'content/posts');

export interface PostData {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  category: string;
  content: string;
}

function getAllMarkdownFiles(dirPath: string, arrayOfFiles: string[] = []) {
  if (!fs.existsSync(dirPath)) return arrayOfFiles;
  const files = fs.readdirSync(dirPath);
  files.forEach(function (file) {
    const fullPath = path.join(dirPath, file);
    if (fs.statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllMarkdownFiles(fullPath, arrayOfFiles);
    } else {
      if (file.endsWith('.md')) {
        arrayOfFiles.push(fullPath);
      }
    }
  });
  return arrayOfFiles;
}

export function getSortedPostsData(): PostData[] {
  const allFiles = getAllMarkdownFiles(postsDirectory);
  const allPostsData = allFiles.map((fullPath) => {
    const fileName = path.basename(fullPath);
    const slug = fileName.replace(/\.md$/, '');
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const { data, content } = matter(fileContents);
    
    // 부모 폴더 이름에서 카테고리 추출 (예: "2. AI News" -> "AI News")
    const parentFolder = path.basename(path.dirname(fullPath));
    const derivedCategory = parentFolder !== 'posts' 
      ? parentFolder.replace(/^\d+\.\s*/, '') 
      : (data.category || 'Insight');

    return {
      slug,
      content,
      title: data.title,
      date: data.date,
      excerpt: data.excerpt,
      ...data,
      category: derivedCategory,
    } as PostData;
  });

  return allPostsData.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPostData(slug: string): PostData {
  const allFiles = getAllMarkdownFiles(postsDirectory);
  const targetFile = allFiles.find(file => path.basename(file) === `${slug}.md`);
  
  if (!targetFile) {
    throw new Error(`Post not found for slug: ${slug}`);
  }

  const fileContents = fs.readFileSync(targetFile, 'utf8');
  const { data, content } = matter(fileContents);
  
  // 부모 폴더 이름에서 카테고리 추출
  const parentFolder = path.basename(path.dirname(targetFile));
  const derivedCategory = parentFolder !== 'posts' 
    ? parentFolder.replace(/^\d+\.\s*/, '') 
    : (data.category || 'Insight');

  return {
    slug,
    content,
    title: data.title,
    date: data.date,
    excerpt: data.excerpt,
    ...data,
    category: derivedCategory,
  } as PostData;
}
