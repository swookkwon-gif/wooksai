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
  related?: string[];
  prevPosts?: { slug: string; title: string; date: string }[];
  nextPosts?: { slug: string; title: string; date: string }[];
  relatedPosts?: { slug: string; title: string; date: string; category: string; excerpt: string }[];
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

function generateExcerpt(content: string, length: number = 150): string {
  // 마크다운 헤딩, 이미지, 링크 제거 및 줄바꿈을 공백으로 변경하여 순수 텍스트만 추출
  let text = content
    .replace(/^#+\s+.*/gm, '') // 헤딩 제거
    .replace(/!\[.*?\]\(.*?\)/g, '') // 이미지 제거
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // 링크는 텍스트만 남김
    .replace(/<[^>]*>/g, '') // HTML 태그 제거
    .replace(/[\r\n]+/g, ' ') // 줄바꿈을 공백으로
    .trim();
  
  if (text.length <= length) return text;
  return text.substring(0, length).trim() + '...';
}

export function getSortedPostsData(lang: string = 'ko'): PostData[] {
  const allFiles = getAllMarkdownFiles(postsDirectory);
  
  const filteredFiles = allFiles.filter(file => {
    if (lang === 'en') return file.endsWith('.en.md');
    return file.endsWith('.md') && !file.endsWith('.en.md');
  });

  const allPostsData = filteredFiles.map((fullPath) => {
    const fileName = path.basename(fullPath);
    const slug = fileName.replace(/\.(en|ko)?\.?md$/, '');
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const { data, content } = matter(fileContents);
    
    // 부모 폴더 이름에서 카테고리 추출 (예: "2. AI News" -> "AI News")
    const parentFolder = path.basename(path.dirname(fullPath));
    const derivedCategory = parentFolder !== 'posts' 
      ? parentFolder.replace(/^\d+\.\s*/, '') 
      : (data.category || 'Insight');

    const postDate = data.date instanceof Date 
      ? data.date.toISOString().split('T')[0]
      : (data.date ? String(data.date).split('T')[0] : new Date().toISOString().split('T')[0]);

    return {
      ...data,
      slug,
      content,
      title: data.title,
      date: postDate,
      excerpt: data.excerpt || generateExcerpt(content),
      category: derivedCategory,
    } as PostData;
  });

  return allPostsData.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPostData(slug: string, lang: string = 'ko'): PostData {
  const allFiles = getAllMarkdownFiles(postsDirectory);
  
  const targetFile = allFiles.find(file => {
    const fileName = path.basename(file);
    const fileSlug = fileName.replace(/\.(en|ko)?\.?md$/, '');
    if (fileSlug !== slug) return false;
    
    if (lang === 'en') return fileName.endsWith('.en.md');
    return fileName.endsWith('.md') && !fileName.endsWith('.en.md');
  });
  
  if (!targetFile) {
    throw new Error(`Post not found for slug: ${slug}`);
  }

  const fileContents = fs.readFileSync(targetFile, 'utf8');
  const { data, content } = matter(fileContents);
  
  const parentFolder = path.basename(path.dirname(targetFile));
  const derivedCategory = parentFolder !== 'posts' 
    ? parentFolder.replace(/^\d+\.\s*/, '') 
    : (data.category || 'Insight');

  // Related & Navigation Logic
  const allPosts = getSortedPostsData(lang); // sorted desc by date
  const categoryPosts = allPosts.filter(p => p.category === derivedCategory);
  const catIndex = categoryPosts.findIndex(p => p.slug === slug);
  
  // Prev is older (higher index), Next is newer (lower index)
  const prevPosts = categoryPosts.slice(catIndex + 1, catIndex + 4).map(p => ({ slug: p.slug, title: p.title, date: p.date }));
  const nextPosts = catIndex > 0 ? categoryPosts.slice(Math.max(0, catIndex - 3), catIndex).reverse().map(p => ({ slug: p.slug, title: p.title, date: p.date })) : [];

  let relatedPosts: { slug: string; title: string; date: string; category: string; excerpt: string }[] = [];
  if (data.related && Array.isArray(data.related)) {
    relatedPosts = allPosts
      .filter(p => data.related.includes(p.slug))
      .map(p => ({ slug: p.slug, title: p.title, date: p.date, category: p.category, excerpt: p.excerpt }));
  }

  const postDate = data.date instanceof Date 
    ? data.date.toISOString().split('T')[0]
    : (data.date ? String(data.date).split('T')[0] : new Date().toISOString().split('T')[0]);

  return {
    ...data,
    slug,
    content,
    title: data.title,
    date: postDate,
    excerpt: data.excerpt || generateExcerpt(content),
    category: derivedCategory,
    prevPosts,
    nextPosts,
    relatedPosts
  } as PostData;
}
