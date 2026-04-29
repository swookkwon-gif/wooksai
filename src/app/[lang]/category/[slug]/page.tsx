import Link from "next/link";
import { getSortedPostsData } from "@/lib/posts";
import { notFound } from "next/navigation";

interface CategoryPageProps {
  params: Promise<{
    slug: string;
    lang: string;
  }>;
}

// Generate static params for all categories
export async function generateStaticParams() {
  const postsKo = getSortedPostsData('ko');
  const postsEn = getSortedPostsData('en');
  
  const categoriesKo = Array.from(new Set(postsKo.map(post => post.category || 'Insight')));
  const categoriesEn = Array.from(new Set(postsEn.map(post => post.category || 'Insight')));
  
  return [
    ...categoriesKo.map(category => ({ lang: 'ko', slug: category.toLowerCase().replace(/\s+/g, '-') })),
    ...categoriesEn.map(category => ({ lang: 'en', slug: category.toLowerCase().replace(/\s+/g, '-') }))
  ];
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const { slug, lang } = await params;
  const posts = getSortedPostsData(lang);
  
  // URL 슬러그와 포스트의 카테고리 매칭
  const filteredPosts = posts.filter(post => {
    const postCategorySlug = (post.category || 'Insight').toLowerCase().replace(/\s+/g, '-');
    return postCategorySlug === slug;
  });

  if (filteredPosts.length === 0) {
    notFound();
  }

  // 표시용 원본 카테고리명 가져오기
  const displayCategory = filteredPosts[0].category;

  return (
    <div className="font-sans">
      {/* Post List */}
      <div className="flex flex-col">
        {filteredPosts.map((post) => (
          <article key={post.slug} className="mm-post-item group">
            <h2 className="text-xl md:text-2xl font-bold mb-2">
              <Link href={`/${lang}/posts/${post.slug}`} className="text-neutral-900 group-hover:text-blue-600 transition-colors">
                {post.title}
              </Link>
            </h2>
            <div className="text-sm text-neutral-500 mb-3 space-x-3">
              <time dateTime={post.date}>{post.date}</time>
              <span>•</span>
              <span className="font-medium text-neutral-600">{post.category || "Insight"}</span>
            </div>
            <p className="text-neutral-600 leading-relaxed text-sm md:text-base mb-3 max-w-3xl">
              {post.excerpt}
            </p>
          </article>
        ))}
      </div>
    </div>
  );
}
