import Link from "next/link";
import { getSortedPostsData } from "@/lib/posts";
import { notFound } from "next/navigation";

interface CategoryPageProps {
  params: {
    slug: string;
  };
}

// Generate static params for all categories
export function generateStaticParams() {
  const posts = getSortedPostsData();
  const categories = Array.from(new Set(posts.map(post => post.category || 'Insight')));
  
  return categories.map(category => ({
    slug: category.toLowerCase().replace(/\s+/g, '-'),
  }));
}

export default function CategoryPage({ params }: CategoryPageProps) {
  const posts = getSortedPostsData();
  
  // URL 슬러그와 포스트의 카테고리 매칭
  const filteredPosts = posts.filter(post => {
    const postCategorySlug = (post.category || 'Insight').toLowerCase().replace(/\s+/g, '-');
    return postCategorySlug === params.slug;
  });

  if (filteredPosts.length === 0) {
    notFound();
  }

  // 표시용 원본 카테고리명 가져오기
  const displayCategory = filteredPosts[0].category;

  return (
    <div className="font-sans">
      <h1 className="text-3xl font-extrabold text-neutral-900 mb-8 border-b border-gray-100 pb-4">
        Category: {displayCategory}
      </h1>

      {/* Post List */}
      <div className="flex flex-col">
        {filteredPosts.map((post) => (
          <article key={post.slug} className="mm-post-item group">
            <h2 className="text-xl md:text-2xl font-bold mb-2">
              <Link href={`/posts/${post.slug}`} className="text-neutral-900 group-hover:text-blue-600 transition-colors">
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
            <Link 
              href={`/posts/${post.slug}`} 
              className="inline-block text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
            >
              Read more &rarr;
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
